"""
UML Class Diagram – Neighborhood Library App
Zones: Pydantic Schemas (left) | ORM Models (centre) | FastAPI Routers (right)
       Infrastructure (bottom centre)
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.lines import Line2D
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

W, H = 28, 23
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor('#F1F5F9')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis('off')

C = dict(
    orm    ='#1D4ED8',
    schema ='#059669',
    router ='#D97706',
    infra  ='#7C3AED',
    rel    ='#475569',
    dep    ='#94A3B8',
    inh    ='#374151',
)

# ── Primitives ────────────────────────────────────────────────────────────────
def hard_rect(x, y, w, h, fc, ec, lw=1.8, zorder=2):
    p = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder)
    ax.add_patch(p)

MONO = 'DejaVu Sans Mono'

def uml_class(x, y, w, stereotype, name, attrs, methods,
              color, bg='#FFFFFF'):
    """3-compartment UML class. Returns (x, y, w, total_height)."""
    RH   = 0.345
    HDR  = 0.70 if stereotype else 0.50
    AH   = max(len(attrs), 1) * RH + 0.18
    MH   = len(methods) * RH + 0.20 if methods else 0.0
    tot  = HDR + AH + MH

    # outer box
    hard_rect(x, y, w, tot, bg, color, lw=2.0)
    # header fill
    hard_rect(x, y + tot - HDR, w, HDR, color, color, lw=0)

    if stereotype:
        ax.text(x+w/2, y+tot-0.21, f'<<{stereotype}>>',
                ha='center', va='center', fontsize=7.5,
                color='white', fontstyle='italic', zorder=5)
    ax.text(x+w/2, y+tot-(HDR-0.13), name,
            ha='center', va='center', fontsize=10,
            color='white', fontweight='bold', zorder=5)

    att_top = y + tot - HDR
    for i, a in enumerate(attrs):
        bold = a.startswith('##')
        lbl  = a.lstrip('#').strip()
        ax.text(x+0.14, att_top - 0.19 - i*RH, lbl,
                ha='left', va='center', fontsize=7.8, zorder=5,
                fontweight='bold' if bold else 'normal',
                color='#0F172A', fontfamily=MONO)

    if methods:
        div = att_top - AH
        ax.plot([x+0.06, x+w-0.06], [div, div],
                color=color, lw=0.9, alpha=0.55, zorder=4)
        for i, m in enumerate(methods):
            bold = m.startswith('##')
            lbl  = m.lstrip('#').strip()
            ax.text(x+0.14, div - 0.19 - i*RH, lbl,
                    ha='left', va='center', fontsize=7.8, zorder=5,
                    fontweight='bold' if bold else 'normal',
                    fontstyle='italic' if not bold else 'normal',
                    color='#1E3A5F', fontfamily=MONO)

    return (x, y, w, tot)

def inheritance_arrow(x1, y1, x2, y2, color=C['inh']):
    """Open hollow-triangle inheritance arrow (child → parent)."""
    dx, dy  = x2-x1, y2-y1
    length  = (dx**2+dy**2)**0.5
    if length < 0.01:
        return
    ux, uy  = dx/length, dy/length
    TW, TH  = 0.22, 0.32          # triangle width/height
    px, py  = -uy*TW/2, ux*TW/2  # perpendicular
    bx = x2 - ux*TH
    by = y2 - uy*TH
    tri = Polygon([(x2,y2),(bx+px,by+py),(bx-px,by-py)],
                  fc='white', ec=color, lw=1.8, zorder=6)
    ax.add_patch(tri)
    ax.plot([x1, bx], [y1, by], color=color, lw=1.5, zorder=5)

def assoc_line(x1, y1, x2, y2, m1='1', m2='*', label='', color=C['rel']):
    """UML association with multiplicities."""
    ax.plot([x1,x2],[y1,y2], color=color, lw=1.8, zorder=3)
    def off(sx,sy,tx,ty, dist=0.28):
        dx,dy=tx-sx,ty-sy
        L=(dx**2+dy**2)**0.5 or 1
        return sx+dx/L*dist, sy+dy/L*dist+0.22
    if m1:
        ox,oy=off(x1,y1,x2,y2)
        ax.text(ox,oy, m1, ha='center', va='center', fontsize=10,
                fontweight='bold', color=color, zorder=6)
    if m2:
        ox,oy=off(x2,y2,x1,y1)
        ax.text(ox,oy, m2, ha='center', va='center', fontsize=10,
                fontweight='bold', color=color, zorder=6)
    if label:
        mx,my=(x1+x2)/2,(y1+y2)/2
        ax.text(mx,my+0.25, label, ha='center', va='center', fontsize=8,
                color=color, bbox=dict(fc='white',ec='none',alpha=0.9,pad=0.1), zorder=6)

def dep_arrow(x1,y1,x2,y2, label='', color=C['dep'], rad=0.0):
    """UML dependency: dashed open arrow."""
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3,
                                connectionstyle=f'arc3,rad={rad}',
                                linestyle='dashed'))
    if label:
        mx,my=(x1+x2)/2,(y1+y2)/2
        ax.text(mx,my+0.22, f'<<{label}>>', ha='center', va='center',
                fontsize=7.2, color=color, fontstyle='italic',
                bbox=dict(fc='white',ec='none',alpha=0.88,pad=0.1), zorder=6)

def zone_bg(x,y,w,h, label, color):
    hard_rect(x,y,w,h, color+'12', color, lw=1.5, zorder=0)
    ax.text(x+0.20, y+h-0.15, label, ha='left', va='top',
            fontsize=10, fontweight='bold', color=color, zorder=1)

# ═════════════════════════════════════════════════════════════════════════════
# TITLE
# ═════════════════════════════════════════════════════════════════════════════
hard_rect(0.15, 22.35, 27.70, 0.55, '#0F172A', '#0F172A', lw=0)
ax.text(14.0, 22.625,
        'Neighborhood Library App  —  UML Class Diagram',
        ha='center', va='center', fontsize=15,
        color='white', fontweight='bold')

# ═════════════════════════════════════════════════════════════════════════════
# ZONE BACKGROUNDS
# ═════════════════════════════════════════════════════════════════════════════
zone_bg(0.15,  1.00,  9.10, 21.10, 'Pydantic Schemas  (Request / Response DTOs)', C['schema'])
zone_bg(9.40,  6.50,  9.80, 15.60, 'ORM Models  (SQLAlchemy 2.0 Async)',           C['orm'])
zone_bg(9.40,  1.00,  9.80,  5.20, 'Infrastructure  (DB Engine + Config)',          C['infra'])
zone_bg(19.40, 1.00,  8.45, 21.10, 'FastAPI Routers  (Endpoint Handlers)',          C['router'])

# ═════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════

# ── BookBase ──────────────────────────────────────────────────────────────────
_, yb, _, hb = uml_class(
    0.35, 18.30, 8.60, 'BaseModel', 'BookBase',
    attrs=[
        '+ title:     str',
        '+ author:    str',
        '+ isbn:      Optional[str] = None',
        '+ available: bool          = True',
    ],
    methods=[], color=C['schema'], bg='#F0FDF4')

# ── BookCreate ────────────────────────────────────────────────────────────────
_, ybc, _, hbc = uml_class(
    0.35, 16.00, 4.20, 'schema', 'BookCreate',
    attrs=['(inherits BookBase)', '  no additional fields'],
    methods=[], color=C['schema'], bg='#DCFCE7')

# ── BookOut ───────────────────────────────────────────────────────────────────
_, ybo, _, hbo = uml_class(
    4.75, 15.50, 4.00, 'schema', 'BookOut',
    attrs=['(inherits BookBase)',
           '+ id:         int',
           '## Config',
           '  from_attributes = True'],
    methods=[], color=C['schema'], bg='#DCFCE7')

# Inheritance: BookCreate → BookBase
inheritance_arrow(0.35+4.20/2, ybc+hbc,
                  0.35+8.60/2, yb, C['schema'])
# Inheritance: BookOut → BookBase
inheritance_arrow(4.75+4.00/2, ybo+hbo,
                  0.35+8.60/2, yb, C['schema'])

# ── MemberBase ────────────────────────────────────────────────────────────────
_, ym, _, hm = uml_class(
    0.35, 12.80, 8.60, 'BaseModel', 'MemberBase',
    attrs=[
        '+ name:      str',
        '+ email:     EmailStr',
        '+ phone:     Optional[str] = None',
    ],
    methods=[], color=C['schema'], bg='#F0FDF4')

# ── MemberCreate ─────────────────────────────────────────────────────────────
_, ymc, _, hmc = uml_class(
    0.35, 10.80, 4.20, 'schema', 'MemberCreate',
    attrs=['(inherits MemberBase)', '  no additional fields'],
    methods=[], color=C['schema'], bg='#DCFCE7')

# ── MemberOut ────────────────────────────────────────────────────────────────
_, ymo, _, hmo = uml_class(
    4.75, 10.30, 4.00, 'schema', 'MemberOut',
    attrs=['(inherits MemberBase)',
           '+ id:         int',
           '+ joined_at:  datetime',
           '+ is_active:  bool',
           '## Config',
           '  from_attributes = True'],
    methods=[], color=C['schema'], bg='#DCFCE7')

inheritance_arrow(0.35+4.20/2, ymc+hmc,
                  0.35+8.60/2, ym,   C['schema'])
inheritance_arrow(4.75+4.00/2, ymo+hmo,
                  0.35+8.60/2, ym,   C['schema'])

# ── LoanCreate ───────────────────────────────────────────────────────────────
_, ylc, _, hlc = uml_class(
    0.35, 7.80, 4.20, 'schema', 'LoanCreate',
    attrs=['+ book_id:   int', '+ member_id: int'],
    methods=[], color=C['schema'], bg='#DCFCE7')

# ── LoanOut ──────────────────────────────────────────────────────────────────
_, ylo, _, hlo = uml_class(
    4.75, 6.50, 4.00, 'schema', 'LoanOut',
    attrs=['+ id:           int',
           '+ book_id:      int',
           '+ member_id:    int',
           '+ borrowed_at:  datetime',
           '+ returned_at:  Optional[datetime]',
           '+ fine_amount:  float',
           '+ is_overdue:   bool',
           '## Config',
           '  from_attributes = True'],
    methods=[], color=C['schema'], bg='#DCFCE7')

# ── Note band ─────────────────────────────────────────────────────────────────
hard_rect(0.35, 5.20, 8.60, 1.12, '#ECFDF5', C['schema'], lw=1.2)
ax.text(4.65, 5.76,
        'Pydantic v2  •  validates on instantiation  •  serialises to/from JSON\n'
        'Base schemas are reused → DRY principle  •  Config: from_attributes=True',
        ha='center', va='center', fontsize=7.8, color='#065F46',
        fontstyle='italic')

# ═════════════════════════════════════════════════════════════════════════════
# ORM MODELS  (centre)
# ═════════════════════════════════════════════════════════════════════════════

# ── Book ─────────────────────────────────────────────────────────────────────
_, yBk, _, hBk = uml_class(
    9.55, 17.00, 4.70, 'entity', 'Book',
    attrs=['+ id:         int         (PK)',
           '+ title:      str',
           '+ author:     str',
           '+ isbn:       Optional[str]   (UQ)',
           '+ available:  bool  = True',
           '+ created_at: datetime'],
    methods=['## Relationships',
             '+ loans: List[Loan]    back_populates="book"'],
    color=C['orm'], bg='#EFF6FF')

# ── Member ───────────────────────────────────────────────────────────────────
_, yMb, _, hMb = uml_class(
    14.45, 16.70, 4.70, 'entity', 'Member',
    attrs=['+ id:        int          (PK)',
           '+ name:      str',
           '+ email:     str          (UQ)',
           '+ phone:     Optional[str]',
           '+ joined_at: datetime',
           '+ is_active: bool  = True'],
    methods=['## Relationships',
             '+ loans: List[Loan]    back_populates="member"'],
    color=C['orm'], bg='#EFF6FF')

# ── Loan ─────────────────────────────────────────────────────────────────────
_, yLn, _, hLn = uml_class(
    11.30, 9.80, 5.10, 'entity', 'Loan',
    attrs=['+ id:           int    (PK)',
           '+ book_id:      int    (FK → books.id)',
           '+ member_id:    int    (FK → members.id)',
           '+ borrowed_at:  datetime  = now()',
           '+ returned_at:  Optional[datetime]',
           '+ fine_amount:  float     = 0.0'],
    methods=['## Relationships',
             '+ book:   Book    back_populates="loans"',
             '+ member: Member  back_populates="loans"',
             '## Properties',
             '+ overdue_days: int     @property',
             '+ is_overdue:   bool    @property'],
    color=C['orm'], bg='#EFF6FF')

# ── ORM Associations ─────────────────────────────────────────────────────────
# Book(1) --- Loan(*)
assoc_line(9.55+4.70/2, yBk,        # bottom of Book
           11.30+5.10/2, yLn+hLn,   # top of Loan
           m1='1', m2='*', label='borrows', color=C['rel'])

# Member(1) --- Loan(*)
assoc_line(14.45+4.70/2, yMb,
           11.30+5.10/2, yLn+hLn,
           m1='1', m2='*', label='makes', color=C['rel'])

# ── Base class note ───────────────────────────────────────────────────────────
hard_rect(9.55, 9.30, 9.60, 0.42, '#DBEAFE', C['orm'], lw=1.2)
ax.text(14.35, 9.52,
        'All models extend  DeclarativeBase  •  AsyncSession  •  selectinload for eager-loading',
        ha='center', va='center', fontsize=7.6, color='#1E3A8A', fontstyle='italic')

# ═════════════════════════════════════════════════════════════════════════════
# INFRASTRUCTURE
# ═════════════════════════════════════════════════════════════════════════════

_, yDB, _, hDB = uml_class(
    9.55, 3.80, 5.30, 'infrastructure', 'database.py',
    attrs=['+ engine: AsyncEngine',
           '+ AsyncSessionLocal: async_sessionmaker'],
    methods=['+ get_db() → AsyncGenerator[AsyncSession]',
             '  # FastAPI Depends() injection target'],
    color=C['infra'], bg='#F5F3FF')

_, yCfg, _, hCfg = uml_class(
    15.10, 3.80, 4.20, 'configuration', 'Settings',
    attrs=['+ DATABASE_URL:  str',
           '+ FINE_PER_DAY:  float = 1.0',
           '+ CORS_ORIGINS:  list[str]'],
    methods=['# reads .env via pydantic-settings'],
    color=C['infra'], bg='#F5F3FF')

_, yApp, _, hApp = uml_class(
    9.55, 1.20, 9.75, 'application', 'FastAPI  (main.py)',
    attrs=['+ app: FastAPI()',
           '+ middleware: CORSMiddleware'],
    methods=['+ include_router(books_router,   prefix="/books")',
             '+ include_router(members_router, prefix="/members")',
             '+ include_router(loans_router,   prefix="/loans")',
             '+ lifespan: create_all_tables()'],
    color=C['infra'], bg='#F5F3FF')

# ═════════════════════════════════════════════════════════════════════════════
# FASTAPI ROUTERS
# ═════════════════════════════════════════════════════════════════════════════

_, yBR, _, hBR = uml_class(
    19.55, 16.50, 8.10, 'router', 'BooksRouter',
    attrs=['## prefix = "/books"',
           '+ tags = ["books"]',
           '+ db: AsyncSession = Depends(get_db)'],
    methods=['+ list_books(search?:str) → List[BookOut]',
             '+ get_book(id:int)        → BookOut',
             '+ create_book(data:BookCreate) → BookOut',
             '+ update_book(id:int, data:BookCreate) → BookOut',
             '+ delete_book(id:int)     → None',
             '# raises HTTPException 404 if not found'],
    color=C['router'], bg='#FFFBEB')

_, yMR, _, hMR = uml_class(
    19.55, 11.00, 8.10, 'router', 'MembersRouter',
    attrs=['## prefix = "/members"',
           '+ tags = ["members"]',
           '+ db: AsyncSession = Depends(get_db)'],
    methods=['+ list_members()            → List[MemberOut]',
             '+ get_member(id:int)        → MemberOut',
             '+ create_member(data:MemberCreate) → MemberOut',
             '+ update_member(id:int, data:MemberCreate) → MemberOut',
             '+ delete_member(id:int)     → None',
             '# raises 409 on duplicate email'],
    color=C['router'], bg='#FFFBEB')

_, yLR, _, hLR = uml_class(
    19.55, 4.80, 8.10, 'router', 'LoansRouter',
    attrs=['## prefix = "/loans"',
           '+ tags = ["loans"]',
           '+ db: AsyncSession = Depends(get_db)'],
    methods=['+ list_loans()              → List[LoanOut]',
             '+ get_overdue_loans()       → List[LoanOut]',
             '+ borrow_book(data:LoanCreate) → LoanOut',
             '  # checks book.available, sets borrowed_at',
             '+ return_book(id:int)       → LoanOut',
             '  # calculates fine, sets returned_at',
             '# raises 400 if unavailable / already returned'],
    color=C['router'], bg='#FFFBEB')

# ── Router infra note ─────────────────────────────────────────────────────────
hard_rect(19.55, 2.00, 8.10, 2.60, '#FEF3C7', C['router'], lw=1.2)
ax.text(23.60, 3.50, 'Dependency Injection (FastAPI Depends)',
        ha='center', va='center', fontsize=8.5, fontweight='bold', color='#92400E')
ax.text(23.60, 3.15,
        'Each router receives  db: AsyncSession = Depends(get_db)',
        ha='center', va='center', fontsize=8, color='#78350F', fontfamily=MONO)
ax.text(23.60, 2.80,
        'Session is opened per-request, committed or rolled back,',
        ha='center', va='center', fontsize=7.8, color='#78350F')
ax.text(23.60, 2.48,
        'and automatically closed via async context manager.',
        ha='center', va='center', fontsize=7.8, color='#78350F')

# ═════════════════════════════════════════════════════════════════════════════
# CROSS-ZONE DEPENDENCY ARROWS
# ═════════════════════════════════════════════════════════════════════════════

# BooksRouter → Book (uses ORM)
dep_arrow(19.55, yBR + hBR*0.65, 9.55+4.70, yBk + hBk*0.60,
          label='uses', color=C['dep'], rad=-0.15)
# BooksRouter → BookCreate / BookOut
dep_arrow(19.55, yBR + hBR*0.35, 8.95, ybc + hbc*0.5,
          label='validates', color=C['schema']+'AA', rad=0.10)

# MembersRouter → Member
dep_arrow(19.55, yMR + hMR*0.65, 14.45+4.70, yMb + hMb*0.55,
          label='uses', color=C['dep'], rad=0.0)
# MembersRouter → MemberCreate
dep_arrow(19.55, yMR + hMR*0.3, 8.95, ymc + hmc*0.5,
          label='validates', color=C['schema']+'AA', rad=0.0)

# LoansRouter → Loan
dep_arrow(19.55, yLR + hLR*0.70, 11.30+5.10, yLn + hLn*0.55,
          label='uses', color=C['dep'], rad=0.15)
# LoansRouter → Book (availability check)
dep_arrow(19.55, yLR + hLR*0.80, 9.55+4.70, yBk + 0.4,
          label='checks available', color=C['dep'], rad=0.18)
# LoansRouter → LoanCreate
dep_arrow(19.55, yLR + hLR*0.35, 8.95, ylc + hlc*0.5,
          label='validates', color=C['schema']+'AA', rad=-0.05)

# All Routers → database.py
dep_arrow(19.55+8.10/2, yBR, 9.55+5.30/2, yDB+hDB,
          label='Depends(get_db)', color=C['infra']+'CC', rad=0.0)

# ═════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═════════════════════════════════════════════════════════════════════════════
legend_items = [
    mpatches.Patch(fc='#EFF6FF', ec=C['orm'],    label='ORM Entity  (SQLAlchemy)'),
    mpatches.Patch(fc='#F0FDF4', ec=C['schema'], label='Pydantic Schema  (DTO)'),
    mpatches.Patch(fc='#FFFBEB', ec=C['router'], label='FastAPI Router'),
    mpatches.Patch(fc='#F5F3FF', ec=C['infra'],  label='Infrastructure'),
    Line2D([0],[0], color=C['inh'], lw=1.8, label='Inheritance  (open △)'),
    Line2D([0],[0], color=C['rel'], lw=1.8, label='Association  1..*'),
    Line2D([0],[0], color=C['dep'], lw=1.3, ls='--', label='Dependency  (dashed →)'),
]
leg = ax.legend(handles=legend_items, loc='lower left',
                fontsize=8.2, framealpha=0.97,
                edgecolor='#CBD5E1', ncol=4,
                bbox_to_anchor=(0.003, 0.003))
leg.get_frame().set_linewidth(1.3)

plt.savefig('D:/InterviewPrep/Numino/DLD/Class_Diagram.png',
            dpi=160, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Class Diagram saved.")
