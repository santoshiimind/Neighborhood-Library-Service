import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Member
from app.schemas import MemberCreate, MemberResponse, MemberUpdate

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(payload: MemberCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(Member).where(Member.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    member = Member(**payload.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.get("", response_model=List[MemberResponse])
async def list_members(
    search: Optional[str] = Query(None, description="Search by name or email"),
    active_only: bool = False,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Member)
    if search:
        like = f"%{search}%"
        query = query.where(or_(Member.name.ilike(like), Member.email.ilike(like)))
    if active_only:
        query = query.where(Member.is_active == True)
    query = query.offset(skip).limit(limit).order_by(Member.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(member_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: uuid.UUID, payload: MemberUpdate, db: AsyncSession = Depends(get_db)
):
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member not found")

    if payload.email and payload.email != member.email:
        conflict = await db.scalar(select(Member).where(Member.email == payload.email))
        if conflict:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)

    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member not found")
    await db.delete(member)
    await db.commit()
