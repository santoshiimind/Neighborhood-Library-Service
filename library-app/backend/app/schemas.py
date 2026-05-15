from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Book schemas ────────────────────────────────────────────────────────────

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    genre: Optional[str] = Field(None, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: int = Field(1, ge=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    genre: Optional[str] = None
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: Optional[int] = Field(None, ge=1)


class BookResponse(BookBase):
    id: uuid.UUID
    available_copies: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Member schemas ───────────────────────────────────────────────────────────

class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = None
    is_active: bool = True


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class MemberResponse(MemberBase):
    id: uuid.UUID
    membership_date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Loan schemas ─────────────────────────────────────────────────────────────

class BorrowRequest(BaseModel):
    book_id: uuid.UUID
    member_id: uuid.UUID


class ReturnRequest(BaseModel):
    pass  # loan_id comes from path


class LoanResponse(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    member_id: uuid.UUID
    borrowed_at: datetime
    due_date: date
    returned_at: Optional[datetime]
    fine_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    book: Optional[BookResponse] = None
    member: Optional[MemberResponse] = None

    model_config = {"from_attributes": True}


# ─── Stats schema ─────────────────────────────────────────────────────────────

class LibraryStats(BaseModel):
    total_books: int
    total_members: int
    active_loans: int
    overdue_loans: int
