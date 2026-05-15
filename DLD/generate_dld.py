"""
DLD Diagram – Neighborhood Library App
Swimlane layout: Client | Frontend | Backend Routers | Backend Core | Database
Bottom panel: Docker Compose services + Request lifecycle + Business logic
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

# ── Canvas setup ──────────────────────────────────────────────────────────────
plt.rcParams['font.family'] = 'DejaVu Sans'

fig = plt.figure(figsize=(28, 19))
fig.patch.set_facecolor('#EEF2F7')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 28)
ax.set_ylim(0, 19)
ax.axis('off')

# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    'client':   '#475569',
    'frontend': '#059669',
    'router':   '#D97706',
    'core':     '#7C3AED',
    'db':       '#0284C7',
    'docker':   '#4F46E5',
    'flow':     '#BE185D',
    'get':      '#16A34A',
    'post':     '#2563EB',
    'put':      '#D97706',
    'delete':   '#DC2626',
    'bg':       '#F8FAFC',
    'rule':     '#64748B',
}

# ── Swimlane x-boundaries ─────────────────────────────────────────────────────
SL = {
    'client':   (0.15, 2.65),
    'frontend': (2.80, 8.30),
    'routers':  (8.45, 14.60),
    'core':     (14.75, 19.50),
    'db':       (19.65, 27.80),
}
Y_LANES = (5.70, 18.20)   # swimlane content area
Y_HDR   = (17.35, 18.20)  # swimlane header row
Y_TITLE = 18.55

# ── Helper primitives ─────────────────────────────────────────────────────────
def rect(x, y, w, h, fc, ec, lw=1.6, zorder=2, radius=0.12):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad={radius}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder)
    ax.add_patch(p)

def header_rect(x, y, w, h, fc, ec):
    rect(x, y, w, h, fc, ec, lw=0, zorder=3, radius=0.08)

def txt(x, y, s, size=8.5, color='#1E293B', weight='normal',
        ha='left', va='center', zorder=5, style='normal'):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=zorder, fontstyle=style,
            fontfamily='DejaVu Sans Mono' if style == 'mono' else 'DejaVu Sans')

def component(x, y, w, h, title, color, bg, rows, row_h=0.38,
              title_fs=9, row_fs=8.2, dividers=None):
    """Draw a component card: coloured header + body rows."""
    rect(x, y, w, h, bg, color, lw=1.8)
    header_rect(x, y + h - 0.54, w, 0.54, color, color)
    txt(x + w/2, y + h - 0.27, title, size=title_fs,
        color='white', weight='bold', ha='center')
    dividers = dividers or []
    for i, row in enumerate(rows):
        ry = y + h - 0.82 - i * row_h
        if row == '---':
            ax.plot([x + 0.12, x + w - 0.12], [ry + 0.15, ry + 0.15],
                    color=color, lw=0.8, alpha=0.4, zorder=4)
        elif row.startswith('##'):
            txt(x + 0.15, ry, row[2:].strip(), size=7.5,
                color=color, weight='bold')
        elif row.startswith('GET '):
            txt(x + 0.15, ry, row[:3], size=7.5, color=C['get'],  weight='bold')
            txt(x + 0.65, ry, row[4:], size=7.5, color='#374151')
        elif row.startswith('POST '):
            txt(x + 0.15, ry, row[:4], size=7.5, color=C['post'], weight='bold')
            txt(x + 0.65, ry, row[5:], size=7.5, color='#374151')
        elif row.startswith('PUT '):
            txt(x + 0.15, ry, row[:3], size=7.5, color=C['put'],  weight='bold')
            txt(x + 0.65, ry, row[4:], size=7.5, color='#374151')
        elif row.startswith('DEL '):
            txt(x + 0.15, ry, row[:3], size=7.5, color=C['delete'], weight='bold')
            txt(x + 0.65, ry, row[4:], size=7.5, color='#374151')
        else:
            txt(x + 0.15, ry, row, size=row_fs, color='#374151')

def swimlane_bg(key, label, color):
    x0, x1 = SL[key]
    y0, y1 = Y_LANES
    # background
    rect(x0, y0, x1 - x0, y1 - y0, color + '0D', color, lw=2, zorder=0, radius=0.18)
    # header strip
    rect(x0, Y_HDR[0], x1 - x0, Y_HDR[1] - Y_HDR[0],
         color, color, lw=0, zorder=1, radius=0.10)
    txt((x0 + x1)/2, (Y_HDR[0] + Y_HDR[1])/2, label,
        size=10, color='white', weight='bold', ha='center')

def arrow(x1, y1, x2, y2, color='#64748B', lw=1.8, label='',
          rad=0.0, style='->', dashed=False):
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=f'arc3,rad={rad}',
                                linestyle=ls))
    if label:
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my + 0.18, label, ha='center', va='center',
                fontsize=7.5, color=color,
                bbox=dict(boxstyle='round,pad=0.18', fc='white',
                          ec='none', alpha=0.9), zorder=6)

def fk_line(x1, y1, x2, y2, color='#94A3B8'):
    ax.plot([x1, x2], [y1, y2], color=color, lw=1.4,
            linestyle='--', zorder=3)
    ax.plot(x2, y2, 'o', color=color, markersize=5, zorder=4)

# ═════════════════════════════════════════════════════════════════════════════
# TITLE
# ═════════════════════════════════════════════════════════════════════════════
rect(0.15, 18.30, 27.70, 0.55, '#1E293B', '#1E293B', lw=0, zorder=1, radius=0.12)
txt(14.0, 18.575,
    'Neighborhood Library App  —  Low-Level Design (DLD)',
    size=15, color='white', weight='bold', ha='center')

# ═════════════════════════════════════════════════════════════════════════════
# SWIMLANE BACKGROUNDS & HEADERS
# ═════════════════════════════════════════════════════════════════════════════
swimlane_bg('client',   'Client',                C['client'])
swimlane_bg('frontend', 'Frontend  (Next.js 14)', C['frontend'])
swimlane_bg('routers',  'Backend  —  Routers',    C['router'])
swimlane_bg('core',     'Backend  —  Core',        C['core'])
swimlane_bg('db',       'PostgreSQL  Database',    C['db'])

# ═════════════════════════════════════════════════════════════════════════════
# CLIENT
# ═════════════════════════════════════════════════════════════════════════════
x0 = SL['client'][0] + 0.15
component(x0, 13.6, 2.2, 3.35, 'Web Browser',
          C['client'], '#F8FAFC',
          ['User interface',
           'HTTP requests',
           'Renders JSON',
           'Port :3000',
           '---',
           'Interactions:',
           '  Search books',
           '  Borrow / Return',
           '  Manage members'],
          row_h=0.35)

component(x0, 6.1, 2.2, 7.25, 'User Actions',
          C['client'], '#F8FAFC',
          ['## CRUD Operations',
           '  View books list',
           '  Add a new book',
           '  Delete a book',
           '---',
           '  View members',
           '  Add member',
           '  Delete member',
           '---',
           '  Borrow a book',
           '  Return a book',
           '  View overdue loans',
           '  Check fine amount',
           '---',
           '## Search & Filter',
           '  Search by title',
           '  Search by author',
           '  Filter overdue'],
          row_h=0.37)

# ═════════════════════════════════════════════════════════════════════════════
# FRONTEND
# ═════════════════════════════════════════════════════════════════════════════
fx = SL['frontend'][0] + 0.18
fw = SL['frontend'][1] - SL['frontend'][0] - 0.36

# Pages
pw = (fw - 0.30) / 3
for i, (title, lines) in enumerate([
    ('books/page.tsx',
     ['BooksPage()',
      '---',
      'State:',
      '  books[]',
      '  loading',
      '  searchTerm',
      '---',
      'Actions:',
      '  fetchBooks()',
      '  handleAdd()',
      '  handleDelete()',
      '  handleSearch()']),
    ('members/page.tsx',
     ['MembersPage()',
      '---',
      'State:',
      '  members[]',
      '  loading',
      '  searchTerm',
      '---',
      'Actions:',
      '  fetchMembers()',
      '  handleAdd()',
      '  handleDelete()',
      '  handleSearch()']),
    ('loans/page.tsx',
     ['LoansPage()',
      '---',
      'State:',
      '  loans[]',
      '  overdueList[]',
      '  loading',
      '---',
      'Actions:',
      '  fetchLoans()',
      '  borrowBook()',
      '  returnBook()',
      '  checkOverdue()']),
]):
    px = fx + i * (pw + 0.15)
    component(px, 12.65, pw, 4.65, title,
              C['frontend'], '#F0FDF4', lines, row_h=0.34, title_fs=8.2)

# api.ts
component(fx, 6.10, fw, 6.25, 'src/lib/api.ts  —  Fetch Layer',
          '#0D9488', '#F0FDFA',
          ['## Books',
           'GET  /books                   → getBooks()',
           'GET  /books?search={q}        → searchBooks(q)',
           'GET  /books/{id}              → getBook(id)',
           'POST /books                   → createBook(data)',
           'PUT  /books/{id}              → updateBook(id, data)',
           'DEL  /books/{id}              → deleteBook(id)',
           '---',
           '## Members',
           'GET  /members                 → getMembers()',
           'POST /members                 → createMember(data)',
           'DEL  /members/{id}            → deleteMember(id)',
           '---',
           '## Loans',
           'GET  /loans                   → getLoans()',
           'GET  /loans/overdue           → getOverdueLoans()',
           'POST /loans                   → borrowBook(data)',
           'PUT  /loans/{id}/return       → returnBook(id)',
          ],
          row_h=0.345, title_fs=9, row_fs=7.8)

# ═════════════════════════════════════════════════════════════════════════════
# BACKEND – ROUTERS
# ═════════════════════════════════════════════════════════════════════════════
rx = SL['routers'][0] + 0.18
rw = (SL['routers'][1] - SL['routers'][0] - 0.54) / 3

# main.py
component(rx, 16.10, SL['routers'][1] - SL['routers'][0] - 0.36, 0.95,
          'app/main.py',
          C['router'], '#FFF7ED',
          ['FastAPI()  |  CORSMiddleware  |  include_router(books/members/loans)  |  lifespan: create_tables'],
          row_h=0.38, title_fs=8.5, row_fs=7.8)

for i, (title, lines) in enumerate([
    ('routers/books.py',
     ['GET  /books',
      'GET  /books/search',
      'GET  /books/{id}',
      'POST /books',
      'PUT  /books/{id}',
      'DEL  /books/{id}',
      '---',
      '## Dependencies',
      '  db: AsyncSession',
      '  Depends(get_db)',
      '---',
      '## Response',
      '  BookOut schema',
      '  List[BookOut]',
      '  HTTP 404 if missing']),
    ('routers/members.py',
     ['GET  /members',
      'GET  /members/{id}',
      'POST /members',
      'PUT  /members/{id}',
      'DEL  /members/{id}',
      '---',
      '## Dependencies',
      '  db: AsyncSession',
      '  Depends(get_db)',
      '---',
      '## Response',
      '  MemberOut schema',
      '  List[MemberOut]',
      '  HTTP 404 if missing',
      '  HTTP 409 on dup email']),
    ('routers/loans.py',
     ['GET  /loans',
      'GET  /loans/overdue',
      'POST /loans',
      'PUT  /loans/{id}/return',
      '---',
      '## Dependencies',
      '  db: AsyncSession',
      '  Depends(get_db)',
      '---',
      '## Business Logic',
      '  Check book available',
      '  Set borrowed_at=now()',
      '  Calc overdue on read',
      '  fine=days*FINE_PER_DAY',
      '  HTTP 400 if returned']),
]):
    component(rx + i * (rw + 0.18), 6.10, rw, 9.70,
              title, C['router'], '#FFF7ED',
              lines, row_h=0.525, title_fs=8.2)

# ═════════════════════════════════════════════════════════════════════════════
# BACKEND – CORE
# ═════════════════════════════════════════════════════════════════════════════
cx = SL['core'][0] + 0.18
cw = SL['core'][1] - SL['core'][0] - 0.36

component(cx, 14.65, cw, 2.20, 'app/schemas.py  (Pydantic v2)',
          C['core'], '#F5F3FF',
          ['BookBase       title, author, isbn, available',
           'BookCreate     BookBase  (in: POST /books)',
           'BookOut        BookBase + id  (response)',
           '---',
           'MemberBase     name, email, phone',
           'MemberCreate   MemberBase  (in: POST /members)',
           'MemberOut      MemberBase + id + joined_at',
           '---',
           'LoanCreate     book_id, member_id',
           'LoanOut        id, book, member, dates, fine, overdue'],
          row_h=0.175, title_fs=8.8)

component(cx, 11.35, cw, 3.00, 'app/models.py  (SQLAlchemy 2.0 ORM)',
          C['core'], '#F5F3FF',
          ['class Book(Base):',
           '  __tablename__ = "books"',
           '  loans = relationship(Loan, back_populates="book")',
           '---',
           'class Member(Base):',
           '  __tablename__ = "members"',
           '  loans = relationship(Loan, back_populates="member")',
           '---',
           'class Loan(Base):',
           '  __tablename__ = "loans"',
           '  book    = relationship(Book)',
           '  member  = relationship(Member)',
           '  @property overdue_days → int'],
          row_h=0.225, title_fs=8.8)

component(cx, 8.75, cw, 2.30, 'app/database.py  (Async Engine)',
          C['core'], '#F5F3FF',
          ['engine = create_async_engine(DATABASE_URL, echo=False)',
           'AsyncSessionLocal = async_sessionmaker(engine)',
           '',
           'async def get_db() → AsyncGenerator[AsyncSession]:',
           '    async with AsyncSessionLocal() as session: yield session',
           '',
           'Used as FastAPI Depends(get_db) in every router'],
          row_h=0.29, title_fs=8.8)

component(cx, 6.10, cw, 2.35, 'app/config.py  (pydantic-settings)',
          C['rule'], '#F8FAFC',
          ['class Settings(BaseSettings):',
           '  DATABASE_URL:  str   (postgresql+asyncpg://…)',
           '  FINE_PER_DAY:  float (default = 1.0)',
           '  CORS_ORIGINS:  list[str]',
           '',
           'settings = Settings()  # reads from .env / environment'],
          row_h=0.34, title_fs=8.8)

# ═════════════════════════════════════════════════════════════════════════════
# DATABASE – PostgreSQL
# ═════════════════════════════════════════════════════════════════════════════
dx = SL['db'][0] + 0.20
dw = SL['db'][1] - SL['db'][0] - 0.40

def db_table(x, y, w, h, name, cols):
    """ER-style table card with PK/FK badges."""
    rect(x, y, w, h, '#EFF6FF', C['db'], lw=2)
    header_rect(x, y + h - 0.52, w, 0.52, C['db'], C['db'])
    txt(x + w/2, y + h - 0.26, name,
        size=10, color='white', weight='bold', ha='center')
    # column separator line
    ax.plot([x + 0.10, x + w - 0.10], [y + h - 0.56, y + h - 0.56],
            color=C['db'], lw=0.8, alpha=0.5, zorder=4)
    rh = (h - 0.62) / len(cols)
    for i, (badge, col, ctype) in enumerate(cols):
        cy = y + h - 0.56 - (i + 0.58) * rh
        # badge
        bc = {'PK': '#1D4ED8', 'FK': '#D97706', 'UQ': '#059669', '': '#9CA3AF'}[badge]
        if badge:
            brect = FancyBboxPatch((x + 0.10, cy - 0.10), 0.36, 0.22,
                                   boxstyle="round,pad=0.03",
                                   fc=bc, ec='none', zorder=4)
            ax.add_patch(brect)
            txt(x + 0.28, cy + 0.01, badge, size=6.2, color='white',
                weight='bold', ha='center')
        txt(x + 0.55, cy, col, size=8.0, color='#1E293B', weight='bold' if badge == 'PK' else 'normal')
        txt(x + w - 0.12, cy, ctype, size=7.5, color='#6B7280', ha='right')

db_table(dx, 14.30, dw, 3.50, 'books', [
    ('PK', 'id',          'SERIAL'),
    ('',  'title',        'VARCHAR(255)  NOT NULL'),
    ('',  'author',       'VARCHAR(255)  NOT NULL'),
    ('UQ','isbn',         'VARCHAR(20)   UNIQUE'),
    ('',  'available',    'BOOLEAN       DEFAULT true'),
    ('',  'created_at',   'TIMESTAMP     DEFAULT now()'),
])

db_table(dx, 10.35, dw, 3.65, 'members', [
    ('PK', 'id',          'SERIAL'),
    ('',   'name',        'VARCHAR(255)  NOT NULL'),
    ('UQ', 'email',       'VARCHAR(255)  UNIQUE NOT NULL'),
    ('',   'phone',       'VARCHAR(20)'),
    ('',   'joined_at',   'TIMESTAMP     DEFAULT now()'),
    ('',   'is_active',   'BOOLEAN       DEFAULT true'),
])

db_table(dx, 6.10, dw, 3.95, 'loans', [
    ('PK', 'id',           'SERIAL'),
    ('FK', 'book_id',      'INT  REFERENCES books(id)'),
    ('FK', 'member_id',    'INT  REFERENCES members(id)'),
    ('',   'borrowed_at',  'TIMESTAMP  DEFAULT now()'),
    ('',   'returned_at',  'TIMESTAMP  NULLABLE'),
    ('',   'fine_amount',  'NUMERIC(10,2)  DEFAULT 0'),
    ('',   'due_date',     'TIMESTAMP  (borrowed_at + 14d)'),
])

# FK relationship lines (loans → books, loans → members)
# loans.book_id → books.id
fk_line(dx, 8.35, dx, 14.30, color='#F59E0B')
# loans.member_id → members.id
fk_line(dx + dw, 7.55, dx + dw, 10.35, color='#F59E0B')

# Alembic badge
rect(dx, 5.72, dw, 0.32, '#1E293B', '#1E293B', lw=0, radius=0.06)
txt(dx + dw/2, 5.88,
    'Alembic  |  migrations/versions/  |  alembic upgrade head',
    size=7.8, color='#CBD5E1', ha='center')

# ═════════════════════════════════════════════════════════════════════════════
# LAYER ARROWS  (horizontal, between swimlanes)
# ═════════════════════════════════════════════════════════════════════════════
# Browser → api.ts
arrow(SL['client'][1], 13.5, SL['frontend'][0], 13.5,
      C['client'], lw=1.8, label='HTTP :3000')

# api.ts → routers (REST JSON)
arrow(SL['frontend'][1], 10.0, SL['routers'][0], 10.0,
      C['router'], lw=2.0, label='REST / JSON')
arrow(SL['routers'][0], 9.4, SL['frontend'][1], 9.4,
      C['frontend'], lw=2.0, label='JSON response', dashed=True)

# routers → schemas (validation)
arrow(SL['routers'][1], 15.0, SL['core'][0], 15.0,
      C['core'], lw=1.8, label='validates')

# routers → models
arrow(SL['routers'][1], 12.5, SL['core'][0], 12.5,
      C['core'], lw=1.8, label='ORM query')

# models → db
arrow(SL['core'][1], 12.0, SL['db'][0], 12.0,
      C['db'], lw=2.0, label='AsyncSQL')
arrow(SL['db'][0], 11.4, SL['core'][1], 11.4,
      C['core'], lw=2.0, label='Result set', dashed=True)

# ═════════════════════════════════════════════════════════════════════════════
# BOTTOM PANEL  —  Docker Compose + Request Lifecycle + Business Logic
# ═════════════════════════════════════════════════════════════════════════════
rect(0.15, 0.18, 27.70, 5.35, '#1E293B', '#1E293B', lw=0, zorder=0, radius=0.18)
txt(14.0, 5.28,
    'Docker Compose Orchestration  &  Request Lifecycle  &  Business Logic',
    size=10.5, color='#94A3B8', weight='bold', ha='center')

# Docker service cards
def svc(x, y, w, h, name, lines, color):
    rect(x, y, w, h, color + '22', color, lw=2, radius=0.12)
    header_rect(x, y + h - 0.46, w, 0.46, color, color)
    txt(x + w/2, y + h - 0.23, name,
        size=8.8, color='white', weight='bold', ha='center')
    for i, line in enumerate(lines):
        txt(x + 0.15, y + h - 0.72 - i * 0.38,
            line, size=7.8, color='#CBD5E1')

svc(0.30, 0.32, 5.20, 4.80, 'frontend  (Docker service)',
    ['Image:    node:20-alpine',
     'Build:    ./frontend/Dockerfile',
     'Port:     3000:3000',
     'Env:      NEXT_PUBLIC_API_URL',
     'Depends:  backend (healthy)',
     '---',
     'CMD: npm run build',
     '     && npm start'],
    C['frontend'])

svc(5.75, 0.32, 5.80, 4.80, 'backend  (Docker service)',
    ['Image:    python:3.11-slim',
     'Build:    ./backend/Dockerfile',
     'Port:     8000:8000',
     'Env:      DATABASE_URL',
     '          FINE_PER_DAY=1.0',
     'Depends:  db (healthy)',
     'CMD: uvicorn app.main:app',
     '     --host 0.0.0.0 --port 8000'],
    C['router'])

svc(11.80, 0.32, 5.50, 4.80, 'db  (Docker service)',
    ['Image:    postgres:15-alpine',
     'Port:     5432:5432',
     'Env:      POSTGRES_DB',
     '          POSTGRES_USER',
     '          POSTGRES_PASSWORD',
     'Volume:   pg_data:/var/lib/postgresql',
     'Health:   pg_isready -U $user',
     'Restart:  unless-stopped'],
    C['db'])

# Request lifecycle
rl_x = 17.55
rect(rl_x, 0.32, 5.10, 4.80, '#0F172A', C['flow'], lw=1.8, radius=0.12)
header_rect(rl_x, 4.66, 5.10, 0.46, C['flow'], C['flow'])
txt(rl_x + 2.55, 4.89, 'Request Lifecycle',
    size=8.8, color='white', weight='bold', ha='center')

steps = [
    ('1', 'Browser  →  Next.js  (:3000)'),
    ('2', 'Page calls  api.ts  helper fn'),
    ('3', 'fetch()  →  FastAPI  (:8000)'),
    ('4', 'Router matches path + method'),
    ('5', 'Pydantic validates body'),
    ('6', 'ORM builds async SQL query'),
    ('7', 'AsyncSession executes on PG'),
    ('8', 'Rows  →  Pydantic Out schema'),
    ('9', 'JSON  →  frontend state'),
    ('10', 'React re-renders UI'),
]
for i, (n, step) in enumerate(steps):
    sy = 4.48 - i * 0.40
    ax.text(rl_x + 0.22, sy, n, fontsize=7.0, color=C['flow'],
            fontweight='bold', ha='center', va='center', zorder=5)
    txt(rl_x + 0.48, sy, step, size=7.8, color='#CBD5E1')

# Business logic
bl_x = 22.90
rect(bl_x, 0.32, 5.0, 4.80, '#0F172A', '#F59E0B', lw=1.8, radius=0.12)
header_rect(bl_x, 4.66, 5.0, 0.46, '#B45309', '#B45309')
txt(bl_x + 2.5, 4.89, 'Business Logic',
    size=8.8, color='white', weight='bold', ha='center')

bl_lines = [
    ('## Borrow Rule',     '#F59E0B'),
    ('book.available must be True',   '#CBD5E1'),
    ('sets book.available = False',   '#CBD5E1'),
    ('sets loan.borrowed_at = now()', '#CBD5E1'),
    ('',                              ''),
    ('## Overdue Detection',  '#F59E0B'),
    ('returned_at IS NULL',    '#CBD5E1'),
    ('AND now() > due_date',   '#CBD5E1'),
    ('due_date = borrowed_at', '#CBD5E1'),
    ('         + 14 days',     '#CBD5E1'),
    ('',                       ''),
    ('## Fine Calculation',  '#F59E0B'),
    ('days = (now()-due_date).days', '#CBD5E1'),
    ('fine = days * FINE_PER_DAY',   '#CBD5E1'),
    ('Lazy: computed on read',        '#94A3B8'),
]
for i, (line, color) in enumerate(bl_lines):
    if not line:
        continue
    weight = 'bold' if line.startswith('##') else 'normal'
    txt(bl_x + 0.20, 4.45 - i * 0.30,
        line.lstrip('#').strip(), size=7.6, color=color, weight=weight)

# ═════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═════════════════════════════════════════════════════════════════════════════
legend_items = [
    mpatches.Patch(fc='#F0FDF4', ec=C['frontend'], label='Frontend Layer'),
    mpatches.Patch(fc='#FFF7ED', ec=C['router'],   label='Routers (FastAPI)'),
    mpatches.Patch(fc='#F5F3FF', ec=C['core'],     label='Core (Schema/Model/DB)'),
    mpatches.Patch(fc='#EFF6FF', ec=C['db'],       label='PostgreSQL Tables'),
    Line2D([0],[0], color=C['get'],    lw=2.5, label='GET'),
    Line2D([0],[0], color=C['post'],   lw=2.5, label='POST'),
    Line2D([0],[0], color=C['put'],    lw=2.5, label='PUT'),
    Line2D([0],[0], color=C['delete'], lw=2.5, label='DELETE'),
    Line2D([0],[0], color='#F59E0B', lw=1.5, linestyle='--', label='FK relation'),
]
leg = ax.legend(handles=legend_items, loc='upper left',
                fontsize=8, framealpha=0.96,
                edgecolor='#CBD5E1', ncol=3,
                bbox_to_anchor=(0.002, 0.999))
leg.get_frame().set_linewidth(1.2)

# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig('D:/InterviewPrep/Numino/DLD/DLD_diagram.png',
            dpi=160, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("DLD diagram saved.")
