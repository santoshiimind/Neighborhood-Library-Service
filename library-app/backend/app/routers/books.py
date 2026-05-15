import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Book
from app.schemas import BookCreate, BookResponse, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db)):
    if payload.isbn:
        existing = await db.scalar(select(Book).where(Book.isbn == payload.isbn))
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="ISBN already registered")

    book = Book(**payload.model_dump(), available_copies=payload.total_copies)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.get("", response_model=List[BookResponse])
async def list_books(
    search: Optional[str] = Query(None, description="Search by title or author"),
    genre: Optional[str] = None,
    available_only: bool = False,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Book)
    if search:
        like = f"%{search}%"
        query = query.where(or_(Book.title.ilike(like), Book.author.ilike(like)))
    if genre:
        query = query.where(Book.genre.ilike(f"%{genre}%"))
    if available_only:
        query = query.where(Book.available_copies > 0)
    query = query.offset(skip).limit(limit).order_by(Book.title)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: uuid.UUID, payload: BookUpdate, db: AsyncSession = Depends(get_db)
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")

    updates = payload.model_dump(exclude_unset=True)

    if "total_copies" in updates:
        delta = updates["total_copies"] - book.total_copies
        new_available = book.available_copies + delta
        if new_available < 0:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Cannot reduce total_copies below currently borrowed copies",
            )
        book.available_copies = new_available

    for field, value in updates.items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.available_copies < book.total_copies:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Cannot delete a book that has active loans",
        )
    await db.delete(book)
    await db.commit()
