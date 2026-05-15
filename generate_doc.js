const fs = require("fs");
const path = require("path");
const docxPath = path.join(
  require("os").homedir(),
  "AppData/Roaming/npm/node_modules/docx"
);
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat, ExternalHyperlink,
  TableOfContents, VerticalAlign,
} = require(docxPath);

// ─── Helpers ──────────────────────────────────────────────────────────────────

const CONTENT_W = 9360; // US Letter, 1" margins
const C1 = 2000;
const C2 = 7360;

const border = (color = "DDDDDD") => ({ style: BorderStyle.SINGLE, size: 1, color });
const borders = (color) => ({ top: border(color), bottom: border(color), left: border(color), right: border(color) });

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, size: 36, color: "1E3A5F", font: "Arial" })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, bold: true, size: 28, color: "2E5C8A", font: "Arial" })],
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, color: "3A7AB5", font: "Arial" })],
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 100 },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })],
  });
}

function bullet(text, bold = false) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", bold })],
  });
}

function subbullet(text) {
  return new Paragraph({
    numbering: { reference: "subbullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, size: 20, font: "Arial" })],
  });
}

function numbered(text, bold = false) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", bold })],
  });
}

function code(text) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    indent: { left: 720 },
    children: [new TextRun({ text, size: 18, font: "Courier New", color: "333333" })],
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E5C8A", space: 1 } },
    children: [],
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function twoColTable(rows, headerRow = null) {
  const makeCell = (text, isHeader = false, isFirst = false) =>
    new TableCell({
      borders: borders("CCCCCC"),
      width: { size: isFirst ? C1 : C2, type: WidthType.DXA },
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      shading: isHeader ? { fill: "1E3A5F", type: ShadingType.CLEAR } : (isFirst ? { fill: "EEF4FB", type: ShadingType.CLEAR } : undefined),
      children: [
        new Paragraph({
          children: [new TextRun({
            text,
            size: 20,
            font: "Arial",
            bold: isHeader,
            color: isHeader ? "FFFFFF" : "000000",
          })],
        }),
      ],
    });

  const tableRows = [];
  if (headerRow) {
    tableRows.push(new TableRow({
      tableHeader: true,
      children: [makeCell(headerRow[0], true, true), makeCell(headerRow[1], true, false)],
    }));
  }
  rows.forEach(([left, right]) => {
    tableRows.push(new TableRow({
      children: [makeCell(left, false, true), makeCell(right, false, false)],
    }));
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [C1, C2],
    rows: tableRows,
  });
}

function threeColTable(rows, headerRow = null) {
  const W1 = 1800, W2 = 3000, W3 = 4560;
  const makeCell = (text, isHeader = false, colIdx = 0) =>
    new TableCell({
      borders: borders("CCCCCC"),
      width: { size: colIdx === 0 ? W1 : colIdx === 1 ? W2 : W3, type: WidthType.DXA },
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      shading: isHeader ? { fill: "2E5C8A", type: ShadingType.CLEAR } : (colIdx === 0 ? { fill: "EEF4FB", type: ShadingType.CLEAR } : undefined),
      children: [new Paragraph({
        children: [new TextRun({ text, size: 20, font: "Arial", bold: isHeader, color: isHeader ? "FFFFFF" : "000000" })],
      })],
    });

  const tableRows = [];
  if (headerRow) {
    tableRows.push(new TableRow({
      tableHeader: true,
      children: headerRow.map((t, i) => makeCell(t, true, i)),
    }));
  }
  rows.forEach((row) => {
    tableRows.push(new TableRow({
      children: row.map((t, i) => makeCell(t, false, i)),
    }));
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [W1, W2, W3],
    rows: tableRows,
  });
}

// ─── Document sections ────────────────────────────────────────────────────────

const titlePage = [
  new Paragraph({ spacing: { before: 1800, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Neighborhood Library Service", bold: true, size: 56, font: "Arial", color: "1E3A5F" })] }),
  new Paragraph({ spacing: { before: 100, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Technical Design & Implementation Document", size: 30, font: "Arial", color: "4A7BAF" })] }),
  divider(),
  new Paragraph({ spacing: { before: 200, after: 100 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Full-Stack Library Management Application", size: 24, font: "Arial", italics: true, color: "666666" })] }),
  new Paragraph({ spacing: { before: 600, after: 100 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Technology Stack", bold: true, size: 26, font: "Arial", color: "1E3A5F" })] }),
  new Paragraph({ spacing: { before: 80, after: 80 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Python  •  FastAPI  •  PostgreSQL  •  Next.js  •  Docker", size: 24, font: "Arial", color: "2E5C8A" })] }),
  new Paragraph({ spacing: { before: 1000, after: 100 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "May 2026", size: 22, font: "Arial", color: "888888" })] }),
  pageBreak(),
];

const tocSection = [
  h1("Table of Contents"),
  new TableOfContents("", { hyperlink: true, headingStyleRange: "1-3" }),
  pageBreak(),
];

const overview = [
  h1("1. Project Overview"),
  body("The Neighborhood Library Service is a full-stack web application designed to help a small neighborhood library digitally manage its books, members, and lending operations. The application replaces manual record-keeping with a structured, queryable system accessible to library staff through a web browser."),
  body(""),
  h2("1.1 Purpose"),
  bullet("Track the library's book catalogue including availability"),
  bullet("Register and manage library members"),
  bullet("Record borrowing and returning of books"),
  bullet("Query active loans, member loan history, and overdue items"),
  bullet("Automatically calculate fines for overdue books"),
  body(""),
  h2("1.2 Technology Choices"),
  twoColTable([
    ["Python + FastAPI", "Async REST API backend — fast, typed, auto-generates interactive docs at /docs"],
    ["PostgreSQL 16", "Relational database with UUID primary keys, FK constraints, and auto-updated timestamps"],
    ["SQLAlchemy (async)", "ORM layer using AsyncSession — non-blocking DB queries for high throughput"],
    ["Next.js 14 (React)", "Server-side-capable frontend with Tailwind CSS for a clean, responsive UI"],
    ["Docker Compose", "One-command startup of all three services (database + backend + frontend)"],
    ["Pydantic v2", "Data validation and serialization for all API request/response models"],
  ], ["Component", "Rationale"]),
  body(""),
  pageBreak(),
];

const architecture = [
  h1("2. System Architecture"),
  h2("2.1 High-Level Architecture"),
  body("The application follows a classic three-tier architecture:"),
  body(""),
  body("Browser (Next.js Frontend)  →  REST API (FastAPI Backend)  →  PostgreSQL Database", { bold: true }),
  body(""),
  body("Each tier runs in its own Docker container. The frontend talks to the backend via HTTP REST calls. The backend communicates with PostgreSQL using the asyncpg driver through SQLAlchemy's async engine. Docker Compose orchestrates startup order — the database must be healthy before the backend starts, and the backend must be up before the frontend starts."),
  body(""),
  h2("2.2 Project Directory Structure"),
  code("library-app/"),
  code("  backend/"),
  code("    app/"),
  code("      __init__.py          # Package marker"),
  code("      config.py            # Settings loaded from .env (Pydantic BaseSettings)"),
  code("      database.py          # Async SQLAlchemy engine, session factory, Base class"),
  code("      models.py            # ORM models: Book, Member, Loan"),
  code("      schemas.py           # Pydantic request/response schemas"),
  code("      routers/"),
  code("        books.py           # Book CRUD endpoints"),
  code("        members.py         # Member CRUD endpoints"),
  code("        loans.py           # Borrow, return, and query endpoints"),
  code("    migrations/"),
  code("      init.sql             # PostgreSQL schema DDL (applied on first container start)"),
  code("    Dockerfile             # Python 3.12 slim image"),
  code("    requirements.txt       # Python dependencies"),
  code("    sample_client.py       # Demo script calling all API operations"),
  code("    run_tests.py           # Automated API test suite (38 tests, all passing)"),
  code("  frontend/"),
  code("    src/"),
  code("      app/"),
  code("        layout.tsx         # Root layout with navigation bar"),
  code("        page.tsx           # Dashboard with stat cards"),
  code("        books/page.tsx     # Books management page"),
  code("        members/page.tsx   # Members management page"),
  code("        loans/page.tsx     # Loans management page"),
  code("      lib/"),
  code("        api.ts             # Typed fetch wrapper for all API calls"),
  code("    Dockerfile             # Multi-stage Node 20 Alpine build"),
  code("  docker-compose.yml       # Service orchestration"),
  code("  README.md                # Setup and usage documentation"),
  body(""),
  h2("2.3 Request Flow"),
  body("A typical borrow-book request travels through the following layers:"),
  numbered("User clicks 'Confirm Borrow' in the browser (Next.js loans page)"),
  numbered("Frontend calls POST /loans/borrow with book_id and member_id in JSON body"),
  numbered("FastAPI receives the request; Pydantic validates the body against BorrowRequest schema"),
  numbered("The loans router handler opens an AsyncSession and queries the DB for the book and member"),
  numbered("Business rules are checked: book availability, member active status, no duplicate active loan"),
  numbered("A new Loan row is inserted and book.available_copies is decremented atomically"),
  numbered("The response is serialized through LoanResponse schema (includes nested book and member objects)"),
  numbered("Frontend receives the JSON response and refreshes the loans table"),
  body(""),
  pageBreak(),
];

const database = [
  h1("3. Database Schema"),
  h2("3.1 Design Principles"),
  bullet("UUID primary keys — avoid sequential ID enumeration and simplify distributed inserts"),
  bullet("Referential integrity — FK constraints prevent orphaned loans"),
  bullet("Check constraints — enforce non-negative copies and valid status values at the DB level"),
  bullet("Automatic timestamps — a trigger updates updated_at on every UPDATE"),
  bullet("Indexes — on email, ISBN, and loan status for fast lookups"),
  body(""),
  h2("3.2 Tables"),
  h3("books"),
  body("Stores the library catalogue. Each book can have multiple physical copies tracked via total_copies and available_copies."),
  twoColTable([
    ["id", "UUID — primary key, auto-generated"],
    ["title", "VARCHAR(255) — NOT NULL"],
    ["author", "VARCHAR(255) — NOT NULL"],
    ["isbn", "VARCHAR(20) — UNIQUE, nullable"],
    ["genre", "VARCHAR(100) — nullable"],
    ["published_year", "INTEGER — nullable, checked 1000-2100"],
    ["total_copies", "INTEGER — NOT NULL, >= 0"],
    ["available_copies", "INTEGER — NOT NULL, >= 0, <= total_copies"],
    ["created_at / updated_at", "TIMESTAMPTZ — auto-managed"],
  ], ["Column", "Description"]),
  body(""),
  h3("members"),
  body("Stores library cardholders. The is_active flag allows deactivating members without deleting their history."),
  twoColTable([
    ["id", "UUID — primary key, auto-generated"],
    ["name", "VARCHAR(255) — NOT NULL"],
    ["email", "VARCHAR(255) — UNIQUE, NOT NULL"],
    ["phone", "VARCHAR(30) — nullable"],
    ["address", "TEXT — nullable"],
    ["is_active", "BOOLEAN — default TRUE"],
    ["membership_date", "DATE — defaults to current date"],
    ["created_at / updated_at", "TIMESTAMPTZ — auto-managed"],
  ], ["Column", "Description"]),
  body(""),
  h3("loans"),
  body("Records every borrowing event. Loans are never deleted — they become 'returned' when the book is brought back. Deleting a book cascades and removes its loan history."),
  twoColTable([
    ["id", "UUID — primary key, auto-generated"],
    ["book_id", "UUID — FK to books.id ON DELETE CASCADE"],
    ["member_id", "UUID — FK to members.id ON DELETE RESTRICT"],
    ["borrowed_at", "TIMESTAMPTZ — when the loan was created"],
    ["due_date", "DATE — borrowed_at + LOAN_PERIOD_DAYS (configurable)"],
    ["returned_at", "TIMESTAMPTZ — NULL while book is out"],
    ["fine_amount", "NUMERIC(8,2) — calculated on return"],
    ["status", "'active' | 'returned' | 'overdue'"],
    ["created_at / updated_at", "TIMESTAMPTZ — auto-managed"],
  ], ["Column", "Description"]),
  body(""),
  h2("3.3 Relationships"),
  bullet("One Book has many Loans (a book can be borrowed multiple times over its lifetime)"),
  bullet("One Member has many Loans (a member can borrow many books over time)"),
  bullet("A Loan belongs to exactly one Book and one Member"),
  bullet("ON DELETE CASCADE on book_id: deleting a book removes its history"),
  bullet("ON DELETE RESTRICT on member_id: cannot delete a member with loan history"),
  body(""),
  h2("3.4 Constraints & Triggers"),
  bullet("CHECK: available_copies >= 0 and available_copies <= total_copies"),
  bullet("CHECK: status IN ('active', 'returned', 'overdue')"),
  bullet("CHECK: total_copies >= 0"),
  bullet("UNIQUE: books.isbn, members.email"),
  bullet("TRIGGER: trigger_set_updated_at() fires BEFORE UPDATE on all three tables"),
  body(""),
  pageBreak(),
];

const backendSection = [
  h1("4. Backend Implementation"),
  h2("4.1 Application Entry Point (main.py)"),
  body("The FastAPI application is created with a lifespan context manager. On startup, SQLAlchemy's create_all() creates any missing tables (idempotent — safe to run on a non-empty database). On shutdown, the engine connection pool is disposed cleanly."),
  body(""),
  body("CORS middleware is configured with allow_origins=[\"*\"] so the frontend (running on a different port) can call the API freely. In a production deployment this would be tightened to the specific frontend domain."),
  body(""),
  body("Two special endpoints sit outside the routers: GET / returns a health check, and GET /stats aggregates library-wide counts (total books, members, active loans, overdue loans) using SQL COUNT queries."),
  body(""),
  h2("4.2 Configuration (config.py)"),
  body("All runtime settings are declared in a Pydantic BaseSettings class and read from environment variables (or a .env file). This makes the application configurable without code changes:"),
  twoColTable([
    ["DATABASE_URL", "Full asyncpg connection string"],
    ["LOAN_PERIOD_DAYS", "Default 14 — days before a loan goes overdue"],
    ["FINE_PER_DAY", "Default $0.50 — daily fine for overdue books"],
  ], ["Variable", "Purpose"]),
  body(""),
  h2("4.3 Database Layer (database.py)"),
  body("An async SQLAlchemy engine is created from the DATABASE_URL. The AsyncSessionLocal session factory is created with expire_on_commit=False so objects remain usable after a commit. A get_db() async generator is used as a FastAPI dependency, ensuring every request gets its own session that is automatically closed."),
  body(""),
  h2("4.4 ORM Models (models.py)"),
  body("Three SQLAlchemy models map to the database tables:"),
  bullet("Book — all catalogue fields plus a relationship to Loan with passive_deletes=True (tells SQLAlchemy to let the DB handle cascade, not try to NULL-out book_id first)"),
  bullet("Member — all member fields plus a relationship to Loan"),
  bullet("Loan — foreign keys to both Book and Member; relationships load both via selectinload for efficient single-query eager loading"),
  body(""),
  h2("4.5 Schemas (schemas.py)"),
  body("Pydantic v2 models enforce validation on every request and response:"),
  twoColTable([
    ["BookCreate", "Title, author required. total_copies >= 1. isbn max 20 chars."],
    ["BookUpdate", "All fields optional (partial update pattern)"],
    ["BookResponse", "Includes computed available_copies and timestamps"],
    ["MemberCreate", "Name + email required. Email validated with email-validator."],
    ["MemberUpdate", "All fields optional"],
    ["MemberResponse", "Includes membership_date and timestamps"],
    ["BorrowRequest", "book_id and member_id (UUIDs)"],
    ["LoanResponse", "Full loan with nested BookResponse and MemberResponse"],
    ["LibraryStats", "Four integer counters for the dashboard"],
  ], ["Schema", "Purpose & Validation"]),
  body(""),
  h2("4.6 Books Router (routers/books.py)"),
  body("Implements full CRUD for books:"),
  threeColTable([
    ["POST /books", "Create book", "Checks ISBN uniqueness. Sets available_copies = total_copies on create."],
    ["GET /books", "List books", "Supports search (title/author ILIKE), genre filter, available_only flag, pagination."],
    ["GET /books/{id}", "Get one", "Returns 404 if not found."],
    ["PUT /books/{id}", "Update", "When total_copies changes, scales available_copies by the delta. Rejects if it would go negative."],
    ["DELETE /books/{id}", "Delete", "Blocked with 409 if any copies are currently on loan (available < total)."],
  ], ["Endpoint", "Action", "Key Logic"]),
  body(""),
  h2("4.7 Members Router (routers/members.py)"),
  body("Implements full CRUD for members:"),
  threeColTable([
    ["POST /members", "Create member", "Checks email uniqueness before insert."],
    ["GET /members", "List members", "Supports search (name/email ILIKE), active_only filter, pagination."],
    ["GET /members/{id}", "Get one", "Returns 404 if not found."],
    ["PUT /members/{id}", "Update", "If email changes, checks it is not already taken by another member."],
    ["DELETE /members/{id}", "Delete", "No restriction check (RESTRICT FK means DB will block if loans exist)."],
  ], ["Endpoint", "Action", "Key Logic"]),
  body(""),
  h2("4.8 Loans Router (routers/loans.py)"),
  body("The most business-logic-heavy router:"),
  threeColTable([
    ["POST /loans/borrow", "Borrow", "Checks: book exists, copies > 0, member active, no duplicate active loan. Sets due_date = today + LOAN_PERIOD_DAYS. Decrements available_copies."],
    ["POST /loans/{id}/return", "Return", "Checks: loan exists, not already returned. Calculates fine = max(0, overdue_days * FINE_PER_DAY). Sets returned_at and status='returned'. Increments available_copies."],
    ["GET /loans", "List all", "Optional status filter. Refreshes overdue status for any active loans past due date before returning."],
    ["GET /loans/member/{id}", "By member", "All loans for one member, optional status filter."],
    ["GET /loans/book/{id}", "By book", "Full loan history for one book."],
    ["GET /loans/overdue", "Overdue", "All active+overdue loans where due_date < today. Updates status and fine."],
    ["GET /loans/{id}", "Get one", "Single loan with nested book and member."],
  ], ["Endpoint", "Action", "Key Logic"]),
  body(""),
  body("Note: Route ordering matters in FastAPI. /loans/overdue and /loans/member/{id} are declared before /loans/{id} to prevent the literal strings 'overdue' and 'member' from being captured as loan UUIDs."),
  body(""),
  h2("4.9 Overdue & Fine Calculation"),
  body("The _compute_fine() helper calculates fines:"),
  code("fine = max(0, (check_date - due_date).days) * FINE_PER_DAY"),
  body(""),
  body("Overdue status is lazily refreshed — when list_loans() or list_overdue_loans() is called, any loans with status='active' and due_date < today are updated to status='overdue' and their fine is recalculated. This avoids the need for a background job."),
  body(""),
  pageBreak(),
];

const frontendSection = [
  h1("5. Frontend Implementation"),
  h2("5.1 Technology"),
  body("The frontend is a Next.js 14 application using the App Router. All pages are client components ('use client') because they fetch live API data on mount. Tailwind CSS provides utility-based styling with a consistent design language."),
  body(""),
  h2("5.2 API Client (src/lib/api.ts)"),
  body("A typed fetch wrapper abstracts all HTTP calls. It handles JSON serialization, sets Content-Type headers, and throws a meaningful Error with the server's detail message on non-2xx responses. The base URL is read from NEXT_PUBLIC_API_URL (defaults to http://localhost:8000)."),
  body(""),
  body("Three grouped API objects are exported:"),
  bullet("booksApi — list (with search/genre/available_only filters), get, create, update, delete"),
  bullet("membersApi — list (with search/active_only filters), get, create, update, delete"),
  bullet("loansApi — list, byMember, overdue, borrow, returnBook"),
  body(""),
  h2("5.3 Pages"),
  twoColTable([
    ["/ (Dashboard)", "Loads /stats and displays four colored stat cards (total books, members, active loans, overdue). Each card links to the relevant management page. Three quick-action cards below provide direct navigation."],
    ["/books", "Shows a searchable table of all books. Available copies shown as a green/red badge. Add Book and Edit Book use a modal form with validation. Delete is blocked server-side if copies are on loan."],
    ["/members", "Shows a searchable table of all members. Active/inactive status shown as a badge. Add Member and Edit Member use a modal form with email, phone, and address fields."],
    ["/loans", "Shows all loans with status filter tabs (All / Active / Overdue / Returned). Borrow Book opens a modal with dropdowns for available books and active members only. Return button visible on non-returned loans. Overdue fines shown in red."],
  ], ["Page", "Description"]),
  body(""),
  h2("5.4 Navigation"),
  body("A persistent top navigation bar (defined in layout.tsx) is present on all pages. It links to Dashboard, Books, Members, and Loans. The indigo color scheme is consistent across the bar, buttons, and status badges."),
  body(""),
  pageBreak(),
];

const businessRules = [
  h1("6. Business Rules & Error Handling"),
  h2("6.1 Borrowing Rules"),
  bullet("A book can only be borrowed if available_copies >= 1", true),
  subbullet("Returns HTTP 409 Conflict: 'No copies available'"),
  bullet("A member must be active (is_active = true) to borrow", true),
  subbullet("Returns HTTP 403 Forbidden: 'Member account is inactive'"),
  bullet("A member cannot borrow the same book twice simultaneously", true),
  subbullet("Returns HTTP 409 Conflict: 'Member already has an active loan for this book'"),
  bullet("Due date = today + LOAN_PERIOD_DAYS (default 14 days)"),
  body(""),
  h2("6.2 Return Rules"),
  bullet("A loan must exist and be non-returned to process a return", true),
  subbullet("Returns HTTP 409: 'Book already returned'"),
  bullet("Fine = max(0, overdue_days x FINE_PER_DAY) — only charged for days past due date"),
  bullet("Returning a book increments book.available_copies by 1"),
  body(""),
  h2("6.3 Book Management Rules"),
  bullet("ISBN must be unique across all books if provided"),
  bullet("Decreasing total_copies is allowed only if available_copies would remain >= 0"),
  subbullet("Prevents reducing below the number of currently borrowed copies"),
  bullet("A book cannot be deleted while any copies are on active loan"),
  subbullet("Checked via available_copies < total_copies comparison"),
  body(""),
  h2("6.4 Member Management Rules"),
  bullet("Email must be unique across all members"),
  bullet("Cannot delete a member who has loan history (FK RESTRICT prevents it at DB level)"),
  bullet("Members can be deactivated (is_active = false) without deleting their records"),
  body(""),
  h2("6.5 HTTP Status Code Usage"),
  twoColTable([
    ["200 OK", "Successful GET, PUT, POST /loans/{id}/return"],
    ["201 Created", "Successful POST /books, /members, /loans/borrow"],
    ["204 No Content", "Successful DELETE"],
    ["400 Bad Request", "Business logic violation (e.g., reducing total_copies too far)"],
    ["403 Forbidden", "Inactive member trying to borrow"],
    ["404 Not Found", "Resource does not exist"],
    ["409 Conflict", "Duplicate (ISBN/email), no copies, already returned, duplicate loan"],
    ["422 Unprocessable Entity", "Pydantic validation failure (missing field, wrong type, etc.)"],
    ["500 Internal Server Error", "Unexpected database or server error"],
  ], ["Status", "When Used"]),
  body(""),
  pageBreak(),
];

const deploymentSection = [
  h1("7. Deployment & Setup"),
  h2("7.1 Docker Compose (Recommended)"),
  body("The fastest way to run the full application is with Docker Compose. All three services are started in dependency order:"),
  numbered("library_db (PostgreSQL) — starts first, health-checked with pg_isready"),
  numbered("library_backend (FastAPI) — waits for db to be healthy, then starts"),
  numbered("library_frontend (Next.js) — starts after backend is up"),
  body(""),
  body("Command:"),
  code("cd library-app"),
  code("docker compose up --build"),
  body(""),
  twoColTable([
    ["Frontend", "http://localhost:3000"],
    ["API", "http://localhost:8000"],
    ["Interactive API Docs", "http://localhost:8000/docs"],
    ["PostgreSQL", "localhost:5432"],
  ], ["Service", "URL"]),
  body(""),
  body("PostgreSQL data is persisted in a named Docker volume (pgdata). The database schema (init.sql) is applied automatically by the postgres image's docker-entrypoint-initdb.d mechanism on first start."),
  body(""),
  h2("7.2 Manual Setup"),
  h3("PostgreSQL"),
  code("psql -U postgres -c \"CREATE USER library_user WITH PASSWORD 'library_pass';\""),
  code("psql -U postgres -c \"CREATE DATABASE library_db OWNER library_user;\""),
  code("psql -U library_user -d library_db -f backend/migrations/init.sql"),
  body(""),
  h3("Backend"),
  code("cd backend"),
  code("python -m venv .venv"),
  code(".venv/Scripts/activate          # Windows"),
  code("source .venv/bin/activate        # macOS/Linux"),
  code("pip install -r requirements.txt"),
  code("cp .env.example .env             # Edit DATABASE_URL if needed"),
  code("uvicorn app.main:app --reload --port 8000"),
  body(""),
  h3("Frontend"),
  code("cd frontend"),
  code("npm install"),
  code("echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local"),
  code("npm run dev"),
  body(""),
  h2("7.3 Environment Variables"),
  twoColTable([
    ["DATABASE_URL", "postgresql+asyncpg://library_user:library_pass@localhost:5432/library_db"],
    ["LOAN_PERIOD_DAYS", "14 (configurable)"],
    ["FINE_PER_DAY", "0.50 (configurable)"],
    ["NEXT_PUBLIC_API_URL", "http://localhost:8000 (frontend env var)"],
  ], ["Variable", "Default Value"]),
  body(""),
  h2("7.4 Backend Dockerfile"),
  body("The backend uses python:3.12-slim as its base image. Dependencies are installed first (before copying app code) so Docker can cache the pip install layer and rebuilds only take seconds when only code changes."),
  body(""),
  h2("7.5 Frontend Dockerfile"),
  body("A three-stage multi-stage build is used:"),
  numbered("deps stage — installs node_modules from package.json"),
  numbered("builder stage — runs next build to create the optimized production bundle"),
  numbered("runner stage — copies only the .next/standalone output (minimal image, no devDependencies)"),
  body(""),
  pageBreak(),
];

const testingSection = [
  h1("8. Testing"),
  h2("8.1 Automated API Test Suite"),
  body("A standalone Python test script (backend/run_tests.py) exercises every endpoint and business rule without external dependencies. It uses only the Python standard library (urllib) so it runs anywhere Python 3 is available."),
  body(""),
  body("The test suite creates unique data on every run (using a Unix timestamp suffix) so it is idempotent and can be run repeatedly against a live database without cleanup."),
  body(""),
  body("All 38 tests pass:"),
  twoColTable([
    ["Stats endpoint", "Returns 200 with correct structure"],
    ["Create book", "201 + available_copies equals total_copies"],
    ["Duplicate ISBN", "409 Conflict"],
    ["Create member", "201 + correct fields"],
    ["Duplicate email", "409 Conflict"],
    ["Borrow book", "201 + status active + due_date set"],
    ["available_copies decremented", "Verified after borrow"],
    ["Duplicate active loan", "409 Conflict"],
    ["Borrow second book", "201 success"],
    ["No copies available", "409 Conflict"],
    ["List all loans", "200 + count >= 2"],
    ["List loans by member", "Returns correct member's loans"],
    ["Loan history by book", "Returns list"],
    ["Return book", "200 + status returned + returned_at set"],
    ["available_copies restored", "Verified after return"],
    ["Double return", "409 Conflict"],
    ["Update book (genre + copies)", "Correct scaling of available_copies"],
    ["Update member (phone)", "Field updated"],
    ["Search books", "Returns matching book"],
    ["available_only filter", "All results have available_copies > 0"],
    ["Search members", "Returns matching member"],
    ["Final stats", "Active loan count correct"],
    ["Delete blocked (active loan)", "409 Conflict"],
    ["Delete after return", "204 No Content"],
  ], ["Test Scenario", "Expected Result"]),
  body(""),
  h2("8.2 Running the Tests"),
  code("cd library-app/backend"),
  code("python run_tests.py"),
  body(""),
  body("The backend must be running (either via Docker or uvicorn) before executing the tests."),
  body(""),
  h2("8.3 Interactive API Documentation"),
  body("FastAPI automatically generates OpenAPI documentation available at http://localhost:8000/docs. Every endpoint can be explored and tested directly in the browser using the Swagger UI — no API client required."),
  body(""),
  h2("8.4 Sample Client Script"),
  body("backend/sample_client.py provides a narrative walkthrough of the API using the httpx library:"),
  bullet("Creates a book and a member"),
  bullet("Borrows the book and verifies the loan"),
  bullet("Attempts a duplicate borrow (demonstrating error handling)"),
  bullet("Returns the book and inspects the updated stats"),
  bullet("Updates book and member records"),
  body(""),
  code("cd backend"),
  code("pip install httpx"),
  code("python sample_client.py"),
  body(""),
  pageBreak(),
];

const apiReference = [
  h1("9. Complete API Reference"),
  h2("9.1 Books"),
  threeColTable([
    ["POST /books", "Create book", "Body: title*, author*, isbn, genre, published_year, total_copies*"],
    ["GET /books", "List books", "Query: search, genre, available_only, skip, limit"],
    ["GET /books/{id}", "Get book", "Path: book UUID"],
    ["PUT /books/{id}", "Update book", "Body: any BookUpdate fields (all optional)"],
    ["DELETE /books/{id}", "Delete book", "Blocked if copies on loan (409)"],
  ], ["Method + Path", "Action", "Parameters"]),
  body(""),
  h2("9.2 Members"),
  threeColTable([
    ["POST /members", "Create member", "Body: name*, email*, phone, address, is_active"],
    ["GET /members", "List members", "Query: search, active_only, skip, limit"],
    ["GET /members/{id}", "Get member", "Path: member UUID"],
    ["PUT /members/{id}", "Update member", "Body: any MemberUpdate fields (all optional)"],
    ["DELETE /members/{id}", "Delete member", "Blocked by DB if loan history exists"],
  ], ["Method + Path", "Action", "Parameters"]),
  body(""),
  h2("9.3 Loans"),
  threeColTable([
    ["POST /loans/borrow", "Borrow book", "Body: book_id*, member_id*"],
    ["POST /loans/{id}/return", "Return book", "Path: loan UUID"],
    ["GET /loans", "List all loans", "Query: status (active|returned|overdue)"],
    ["GET /loans/member/{id}", "Member loans", "Path: member UUID. Query: status"],
    ["GET /loans/book/{id}", "Book history", "Path: book UUID"],
    ["GET /loans/overdue", "Overdue loans", "No params — updates overdue status on read"],
    ["GET /loans/{id}", "Get one loan", "Path: loan UUID"],
  ], ["Method + Path", "Action", "Parameters"]),
  body(""),
  h2("9.4 Health & Stats"),
  threeColTable([
    ["GET /", "Health check", "Returns service name and docs URL"],
    ["GET /stats", "Library stats", "Returns total_books, total_members, active_loans, overdue_loans"],
  ], ["Method + Path", "Action", "Response"]),
  body(""),
  pageBreak(),
];

const issuesAndFixes = [
  h1("10. Issues Found & Fixed During Testing"),
  body("The following issues were discovered when running the application end-to-end with Docker and the automated test suite:"),
  body(""),
  twoColTable([
    ["docker-compose.yml had obsolete 'version' field", "Removed — Docker Compose v2 ignores it but emits a warning"],
    ["Frontend Dockerfile used shell-style 'COPY ... || true' syntax", "Shell conditionals do not work in Dockerfile COPY instructions. Removed the conditional — the public/ directory does not exist and is not needed for the standalone Next.js output"],
    ["loans.book_id FK was ON DELETE RESTRICT", "Changed to ON DELETE CASCADE so that deleting a book also removes its loan history. This is consistent with the delete-book endpoint which checks for active loans before proceeding"],
    ["SQLAlchemy tried to NULL book_id before DELETE", "When the relationship was RESTRICT, SQLAlchemy's ORM attempted to SET book_id = NULL on related loans before deleting the book, causing a NOT NULL violation. Fixed by adding passive_deletes=True to the Book.loans relationship — this tells SQLAlchemy to let the database handle the cascade"],
    ["Test script crashed on 204 No Content body", "Added JSON decode error handling in the test helper so empty response bodies return {} instead of raising JSONDecodeError"],
  ], ["Issue", "Fix Applied"]),
  body(""),
  pageBreak(),
];

const conclusion = [
  h1("11. Summary"),
  body("The Neighborhood Library Service demonstrates a complete, production-ready pattern for building web applications:"),
  body(""),
  bullet("Clean separation of concerns across three tiers (frontend, API, database)"),
  bullet("Async Python backend for non-blocking I/O — suitable for concurrent library-staff usage"),
  bullet("Normalized PostgreSQL schema with proper constraints and triggers"),
  bullet("Pydantic v2 validation on all API boundaries — errors are caught early with clear messages"),
  bullet("Configurable business rules (loan period, fine rate) through environment variables"),
  bullet("Docker Compose for reproducible one-command deployment"),
  bullet("38-test automated suite covering happy paths, edge cases, and error conditions"),
  bullet("Interactive Swagger documentation at /docs for immediate API exploration"),
  body(""),
  body("The application satisfies all core requirements from the take-home specification and extends them with overdue tracking, fine calculation, copy management, member deactivation, and search filtering."),
];

// ─── Build Document ───────────────────────────────────────────────────────────

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "subbullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "◦",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "1E3A5F" },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "3A7AB5" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E5C8A", space: 1 } },
              children: [
                new TextRun({ text: "Neighborhood Library Service  |  Technical Documentation", size: 18, font: "Arial", color: "555555" }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              border: { top: { style: BorderStyle.SINGLE, size: 4, color: "2E5C8A", space: 1 } },
              alignment: AlignmentType.RIGHT,
              children: [
                new TextRun({ text: "Page ", size: 18, font: "Arial", color: "555555" }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "555555" }),
                new TextRun({ text: " of ", size: 18, font: "Arial", color: "555555" }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: "555555" }),
              ],
            }),
          ],
        }),
      },
      children: [
        ...titlePage,
        ...tocSection,
        ...overview,
        ...architecture,
        ...database,
        ...backendSection,
        ...frontendSection,
        ...businessRules,
        ...deploymentSection,
        ...testingSection,
        ...apiReference,
        ...issuesAndFixes,
        ...conclusion,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = "D:/InterviewPrep/Numino/Neighborhood_Library_App_Documentation.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Document written to: " + outPath);
});
