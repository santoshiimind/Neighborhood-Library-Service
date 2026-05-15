# Neighborhood Library Service

A full-stack library management application built with:

| Layer | Technology |
|-------|-----------|
| Backend API | Python · FastAPI (async REST) |
| Database | PostgreSQL 16 |
| Frontend | Next.js 14 · React · Tailwind CSS |
| Container | Docker Compose |

---

## Quick Start (Docker – recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

```bash
# Clone / enter the project root
cd library-app

# Start all services (db + backend + frontend)
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (Next.js) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

The database schema is applied automatically via `backend/migrations/init.sql` on first run.

---

## Manual Setup (without Docker)

### 1 – PostgreSQL

```bash
# Create database and user
psql -U postgres -c "CREATE USER library_user WITH PASSWORD 'library_pass';"
psql -U postgres -c "CREATE DATABASE library_db OWNER library_user;"

# Apply schema
psql -U library_user -d library_db -f backend/migrations/init.sql
```

### 2 – Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL if your credentials differ

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3 – Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Set API URL (optional – defaults to http://localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Open http://localhost:3000 in your browser.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://library_user:library_pass@localhost:5432/library_db` | Async DB connection string |
| `LOAN_PERIOD_DAYS` | `14` | Days before a loan becomes overdue |
| `FINE_PER_DAY` | `0.50` | Fine in $ per overdue day |

### Frontend (`.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## API Reference

### Books

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/books` | Create a book |
| `GET` | `/books` | List books (search, genre, available_only filters) |
| `GET` | `/books/{id}` | Get a single book |
| `PUT` | `/books/{id}` | Update a book |
| `DELETE` | `/books/{id}` | Delete a book (blocked if copies are on loan) |

### Members

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/members` | Register a member |
| `GET` | `/members` | List members (search, active_only filters) |
| `GET` | `/members/{id}` | Get a single member |
| `PUT` | `/members/{id}` | Update a member |
| `DELETE` | `/members/{id}` | Delete a member |

### Loans

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/loans/borrow` | Borrow a book |
| `POST` | `/loans/{id}/return` | Return a borrowed book |
| `GET` | `/loans` | List all loans (optional `?status=active\|returned\|overdue`) |
| `GET` | `/loans/member/{id}` | All loans for a member |
| `GET` | `/loans/book/{id}` | Loan history for a book |
| `GET` | `/loans/overdue` | All overdue loans |
| `GET` | `/loans/{id}` | Get a single loan |

### Health / Stats

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/stats` | Library-wide statistics |

Full interactive documentation is available at **http://localhost:8000/docs**.

---

## Database Schema

```
books
  id              UUID PK
  title           VARCHAR(255)
  author          VARCHAR(255)
  isbn            VARCHAR(20) UNIQUE
  genre           VARCHAR(100)
  published_year  INTEGER
  total_copies    INTEGER  (≥ 0)
  available_copies INTEGER (≥ 0, ≤ total_copies)
  created_at / updated_at  TIMESTAMPTZ

members
  id              UUID PK
  name            VARCHAR(255)
  email           VARCHAR(255) UNIQUE
  phone           VARCHAR(30)
  address         TEXT
  is_active       BOOLEAN
  membership_date DATE
  created_at / updated_at  TIMESTAMPTZ

loans
  id              UUID PK
  book_id         UUID FK → books.id
  member_id       UUID FK → members.id
  borrowed_at     TIMESTAMPTZ
  due_date        DATE
  returned_at     TIMESTAMPTZ (NULL while active)
  fine_amount     NUMERIC(8,2)
  status          'active' | 'returned' | 'overdue'
  created_at / updated_at  TIMESTAMPTZ
```

---

## Sample Client

A standalone Python script demonstrates every API operation:

```bash
cd backend
pip install httpx        # if not already installed
python sample_client.py  # backend must be running on port 8000
```

---

## Business Rules

- A book cannot be borrowed if `available_copies == 0`.
- A member cannot borrow the same book twice simultaneously.
- Inactive members cannot borrow books.
- Returning a book automatically calculates fine: `max(0, overdue_days × FINE_PER_DAY)`.
- Overdue status is refreshed on read when `due_date < today` and `status == 'active'`.
- A book cannot be deleted while copies are on loan.
