import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title           = Column(String(255), nullable=False)
    author          = Column(String(255), nullable=False)
    isbn            = Column(String(20), unique=True)
    genre           = Column(String(100))
    published_year  = Column(Integer)
    total_copies    = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="ck_books_total_copies"),
        CheckConstraint("available_copies >= 0", name="ck_books_available_copies"),
        CheckConstraint("available_copies <= total_copies", name="ck_books_available_le_total"),
    )

    loans = relationship("Loan", back_populates="book", passive_deletes=True)


class Member(Base):
    __tablename__ = "members"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, nullable=False)
    phone           = Column(String(30))
    address         = Column(Text)
    is_active       = Column(Boolean, nullable=False, default=True)
    membership_date = Column(Date, nullable=False, default=date.today)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    loans = relationship("Loan", back_populates="member")


class Loan(Base):
    __tablename__ = "loans"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id     = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    member_id   = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    borrowed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date    = Column(Date, nullable=False)
    returned_at = Column(DateTime(timezone=True))
    fine_amount = Column(Numeric(8, 2), nullable=False, default=0.00)
    status      = Column(String(20), nullable=False, default="active")
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'returned', 'overdue')", name="ck_loans_status"),
    )

    book   = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")
