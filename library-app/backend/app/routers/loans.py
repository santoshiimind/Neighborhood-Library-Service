import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models import Book, Loan, Member
from app.schemas import BorrowRequest, LoanResponse

router = APIRouter(prefix="/loans", tags=["Loans"])


def _compute_fine(due_date: date, returned_at: Optional[datetime] = None) -> Decimal:
    check_date = (returned_at or datetime.now(timezone.utc)).date()
    overdue_days = (check_date - due_date).days
    if overdue_days <= 0:
        return Decimal("0.00")
    return Decimal(str(settings.fine_per_day * overdue_days)).quantize(Decimal("0.01"))


@router.post("/borrow", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def borrow_book(payload: BorrowRequest, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.available_copies < 1:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="No copies available")

    member = await db.get(Member, payload.member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member not found")
    if not member.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Member account is inactive")

    # Prevent borrowing the same book twice simultaneously
    existing = await db.scalar(
        select(Loan).where(
            Loan.book_id == payload.book_id,
            Loan.member_id == payload.member_id,
            Loan.status == "active",
        )
    )
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Member already has an active loan for this book",
        )

    due = date.today().replace(
        day=date.today().day  # keep today's day arithmetic simple via timedelta below
    )
    from datetime import timedelta
    due = date.today() + timedelta(days=settings.loan_period_days)

    loan = Loan(
        book_id=payload.book_id,
        member_id=payload.member_id,
        due_date=due,
        status="active",
    )
    book.available_copies -= 1
    db.add(loan)
    await db.commit()
    await db.refresh(loan)

    result = await db.execute(
        select(Loan).options(selectinload(Loan.book), selectinload(Loan.member)).where(Loan.id == loan.id)
    )
    return result.scalar_one()


@router.post("/{loan_id}/return", response_model=LoanResponse)
async def return_book(loan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Loan).options(selectinload(Loan.book), selectinload(Loan.member)).where(Loan.id == loan_id)
    )
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Loan not found")
    if loan.status == "returned":
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Book already returned")

    now = datetime.now(timezone.utc)
    fine = _compute_fine(loan.due_date, now)

    loan.returned_at = now
    loan.fine_amount = fine
    loan.status = "returned"
    loan.book.available_copies += 1

    await db.commit()
    await db.refresh(loan)
    return loan


@router.get("", response_model=List[LoanResponse])
async def list_loans(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Loan).options(selectinload(Loan.book), selectinload(Loan.member))

    # Refresh overdue status before returning results
    overdue_result = await db.execute(
        select(Loan).where(Loan.status == "active", Loan.due_date < date.today())
    )
    for overdue_loan in overdue_result.scalars().all():
        overdue_loan.status = "overdue"
        overdue_loan.fine_amount = _compute_fine(overdue_loan.due_date)
    await db.commit()

    if status_filter:
        query = query.where(Loan.status == status_filter)
    query = query.offset(skip).limit(limit).order_by(Loan.borrowed_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/member/{member_id}", response_model=List[LoanResponse])
async def loans_by_member(
    member_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member not found")

    query = (
        select(Loan)
        .options(selectinload(Loan.book), selectinload(Loan.member))
        .where(Loan.member_id == member_id)
    )
    if status_filter:
        query = query.where(Loan.status == status_filter)
    query = query.order_by(Loan.borrowed_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/book/{book_id}", response_model=List[LoanResponse])
async def loan_history_for_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")

    result = await db.execute(
        select(Loan)
        .options(selectinload(Loan.book), selectinload(Loan.member))
        .where(Loan.book_id == book_id)
        .order_by(Loan.borrowed_at.desc())
    )
    return result.scalars().all()


@router.get("/overdue", response_model=List[LoanResponse])
async def list_overdue_loans(db: AsyncSession = Depends(get_db)):
    today = date.today()
    result = await db.execute(
        select(Loan)
        .options(selectinload(Loan.book), selectinload(Loan.member))
        .where(Loan.status.in_(["active", "overdue"]), Loan.due_date < today)
        .order_by(Loan.due_date)
    )
    loans = result.scalars().all()
    for loan in loans:
        if loan.status != "overdue":
            loan.status = "overdue"
            loan.fine_amount = _compute_fine(loan.due_date)
    await db.commit()
    return loans


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Loan)
        .options(selectinload(Loan.book), selectinload(Loan.member))
        .where(Loan.id == loan_id)
    )
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan
