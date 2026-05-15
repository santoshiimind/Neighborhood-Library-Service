from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text

from app.database import engine, get_db, Base
from app.models import Book, Loan, Member
from app.routers import books, loans, members
from app.schemas import LibraryStats


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Neighborhood Library API",
    description="REST API for managing books, members, and lending operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Neighborhood Library API", "docs": "/docs"}


@app.get("/stats", response_model=LibraryStats, tags=["Health"])
async def get_stats():
    from app.database import AsyncSessionLocal
    from datetime import date

    async with AsyncSessionLocal() as db:
        total_books   = await db.scalar(select(func.count()).select_from(Book))
        total_members = await db.scalar(select(func.count()).select_from(Member))
        active_loans  = await db.scalar(
            select(func.count()).select_from(Loan).where(Loan.status.in_(["active", "overdue"]))
        )
        overdue_loans = await db.scalar(
            select(func.count()).select_from(Loan).where(
                Loan.status.in_(["active", "overdue"]), Loan.due_date < date.today()
            )
        )
    return LibraryStats(
        total_books=total_books or 0,
        total_members=total_members or 0,
        active_loans=active_loans or 0,
        overdue_loans=overdue_loans or 0,
    )
