"""
UML Sequence Diagram – Neighborhood Library App
Panel 1 (left):  Borrow a Book
Panel 2 (right): Return a Book + Fine Calculation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

plt.rcParams['font.family'] = 'DejaVu Sans'

W, H = 32, 24
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor('#0F172A')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis('off')

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = '#0F172A'
PANEL1  = '#1E293B'
PANEL2  = '#1A2744'
ACTOR   = '#334155'
CALL    = '#60A5FA'    # sync call arrow
RET     = '#34D399'    # return arrow
GUARD   = '#FBBF24'    # alt guard
ALT_BG  = '#1E3A5F'
OPT_BG  = '#27272A'
NOTE    = '#FEF3C7'
NOTEC   = '#92400E'
ACT_BOX = '#2563EB'

MONO = 'DejaVu Sans Mono'

# ── Title bar ─────────────────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.10, 23.25), 31.80, 0.62,
             boxstyle="square,pad=0", fc='#1D4ED8', ec='none'))
ax.text(16.0, 23.56,
        'Neighborhood Library App  —  UML Sequence Diagram  '
        '(Borrow a Book  &  Return a Book + Fine Calculation)',
        ha='center', va='center', fontsize=13.5,
        color='white', fontweight='bold')

# ═════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def panel_bg(x, y, w, h, color, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=color, ec='#334155', lw=1.5))
    ax.text(x + w/2, y + h - 0.30, label, ha='center', va='center',
            fontsize=11.5, fontweight='bold', color='#94A3B8')

def actor_head(x, y, label, sub='', color=ACTOR):
    """Participant box."""
    w, h = 2.20, 0.75
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                boxstyle="round,pad=0.08",
                                fc=color, ec='#60A5FA', lw=1.8, zorder=6))
    ax.text(x, y + 0.08, label, ha='center', va='center',
            fontsize=8.5, color='white', fontweight='bold', zorder=7)
    if sub:
        ax.text(x, y - 0.17, sub, ha='center', va='center',
                fontsize=7.0, color='#94A3B8', zorder=7)

def lifeline(x, y_top, y_bot):
    ax.plot([x, x], [y_bot, y_top - 0.38],
            color='#334155', lw=1.2, linestyle='--', zorder=2)

def activation(x, y_top, y_bot, color=ACT_BOX, w=0.18):
    ax.add_patch(FancyBboxPatch((x-w/2, y_bot), w, y_top-y_bot,
                                boxstyle="square,pad=0",
                                fc=color, ec='#93C5FD', lw=0.8, zorder=3))

def sync_msg(x1, x2, y, label, color=CALL, num=''):
    """Synchronous call arrow."""
    lbl = f'{num}. {label}' if num else label
    right = x2 > x1
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.6,
                                mutation_scale=10))
    mid = (x1 + x2) / 2
    ax.text(mid, y + 0.16, lbl, ha='center', va='center',
            fontsize=7.8, color=color, fontweight='bold',
            fontfamily=MONO, zorder=6,
            bbox=dict(fc=BG, ec='none', alpha=0.85, pad=0.06))

def ret_msg(x1, x2, y, label, color=RET, num=''):
    """Return arrow (dashed)."""
    lbl = f'{num}. {label}' if num else label
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3,
                                mutation_scale=9, linestyle='dashed'))
    mid = (x1 + x2) / 2
    ax.text(mid, y + 0.16, lbl, ha='center', va='center',
            fontsize=7.5, color=color, fontstyle='italic',
            fontfamily=MONO, zorder=6,
            bbox=dict(fc=BG, ec='none', alpha=0.85, pad=0.06))

def self_msg(x, y, label, color=CALL, num=''):
    """Self-call (small loop)."""
    lbl = f'{num}. {label}' if num else label
    ax.annotate('', xy=(x, y), xytext=(x + 0.9, y - 0.35),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3,
                                mutation_scale=9,
                                connectionstyle='arc3,rad=-0.4'))
    ax.plot([x, x+0.9, x+0.9], [y, y, y-0.35],
            color=color, lw=1.3)
    ax.text(x + 1.1, y - 0.17, lbl, ha='left', va='center',
            fontsize=7.6, color=color, fontfamily=MONO, zorder=6)

def alt_frame(x, y_top, w, h, guard_text, alt_y=None, alt_text=''):
    """Combined fragment: alt."""
    ax.add_patch(FancyBboxPatch((x, y_top-h), w, h,
                                boxstyle="square,pad=0",
                                fc=ALT_BG, ec=GUARD, lw=1.5, alpha=0.30, zorder=1))
    # corner tag
    ax.add_patch(FancyBboxPatch((x, y_top-0.38), 0.90, 0.38,
                                boxstyle="square,pad=0",
                                fc=GUARD, ec=GUARD, lw=0))
    ax.text(x+0.45, y_top-0.18, 'alt', ha='center', va='center',
            fontsize=8, color='#0F172A', fontweight='bold')
    # guard label
    ax.text(x+1.0, y_top-0.18, guard_text, ha='left', va='center',
            fontsize=8, color=GUARD, fontweight='bold')
    # divider and else label
    if alt_y is not None:
        ax.plot([x, x+w], [alt_y, alt_y], color=GUARD, lw=0.9,
                linestyle='--', alpha=0.7, zorder=5)
        ax.text(x+1.0, alt_y-0.18, alt_text, ha='left', va='center',
                fontsize=8, color=GUARD, fontstyle='italic')

def opt_frame(x, y_top, w, h, guard_text, label='opt'):
    ax.add_patch(FancyBboxPatch((x, y_top-h), w, h,
                                boxstyle="square,pad=0",
                                fc='#1F2937', ec='#6B7280', lw=1.2,
                                alpha=0.40, zorder=1))
    ax.add_patch(FancyBboxPatch((x, y_top-0.38), 0.90, 0.38,
                                boxstyle="square,pad=0",
                                fc='#4B5563', ec='#4B5563', lw=0))
    ax.text(x+0.45, y_top-0.18, label, ha='center', va='center',
            fontsize=8, color='white', fontweight='bold')
    ax.text(x+1.0, y_top-0.18, guard_text, ha='left', va='center',
            fontsize=8, color='#9CA3AF', fontstyle='italic')

def note_box(x, y, w, lines, fold=True):
    h = len(lines) * 0.32 + 0.20
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                fc='#FEF9C3', ec='#D97706', lw=1.2, zorder=5))
    if fold:
        ax.plot([x+w-0.30, x+w], [y+h, y+h-0.30], color='#D97706', lw=1.0, zorder=6)
        ax.add_patch(FancyBboxPatch((x+w-0.30, y+h-0.30), 0.30, 0.30,
                                    boxstyle="square,pad=0", fc='#FDE68A',
                                    ec='#D97706', lw=1.0, zorder=6))
    for i, line in enumerate(lines):
        ax.text(x+0.10, y+h-0.25-i*0.32, line, ha='left', va='center',
                fontsize=7.5, color=NOTEC, zorder=7)

def step_divider(y, label, color='#475569'):
    ax.plot([0.4, W-0.4], [y, y], color=color, lw=0.6, linestyle=':', alpha=0.5)
    ax.text(W/2, y+0.10, label, ha='center', va='center',
            fontsize=7.2, color=color, fontstyle='italic',
            bbox=dict(fc=BG, ec='none', pad=0.1), zorder=6)

# ═════════════════════════════════════════════════════════════════════════════
# PANEL 1 – BORROW A BOOK  (left half, x: 0.1 → 15.6)
# ═════════════════════════════════════════════════════════════════════════════
panel_bg(0.10, 0.10, 15.60, 22.90, PANEL1, 'Scenario 1:  Borrow a Book')

# Actors (x positions)
A  = dict(
    BR  = 1.40,   # Browser
    LP  = 3.40,   # LoansPage
    API = 5.40,   # api.ts
    LR  = 7.40,   # LoansRouter
    PY  = 9.30,   # Pydantic (LoanCreate)
    DB  = 11.20,  # AsyncSession
    PG  = 13.30,  # PostgreSQL
)
Y_ACT = 22.00    # actor y
Y_BOT =  0.50    # bottom of panel

actor_colors = {
    'BR':  '#374151', 'LP':  '#065F46', 'API': '#065F46',
    'LR':  '#92400E', 'PY':  '#3730A3', 'DB':  '#1E3A8A', 'PG': '#0C4A6E',
}
actor_labels = {
    'BR':  ('Browser',    ''),
    'LP':  ('LoansPage',  'Next.js'),
    'API': ('api.ts',     'fetch wrapper'),
    'LR':  ('LoansRouter','FastAPI'),
    'PY':  ('LoanCreate', 'Pydantic'),
    'DB':  ('AsyncSession','SQLAlchemy'),
    'PG':  ('PostgreSQL', ':5432'),
}
for k, (lbl, sub) in actor_labels.items():
    actor_head(A[k], Y_ACT, lbl, sub, color=actor_colors[k])
    lifeline(A[k], Y_ACT, Y_BOT)

# Activation boxes (x, y_top, y_bot)
activation(A['LP'],  21.50, 1.20, '#065F46')
activation(A['API'], 20.50, 2.00, '#059669')
activation(A['LR'],  19.50, 3.20, '#D97706')
activation(A['PY'],  18.80, 18.20, '#7C3AED', w=0.14)
activation(A['DB'],  14.60, 3.80, '#2563EB')
activation(A['PG'],  14.30, 4.10, '#0284C7')

# ── Message sequence ──────────────────────────────────────────────────────────
y = 21.30
sync_msg(A['BR'],  A['LP'],  y, 'click  "Borrow Book"  (select book + member)', num='1')
y -= 0.70
sync_msg(A['LP'],  A['API'], y, 'borrowBook({ book_id, member_id })', num='2')
y -= 0.70
sync_msg(A['API'], A['LR'],  y, 'POST /loans   body: { book_id, member_id }', num='3')
y -= 0.70
sync_msg(A['LR'],  A['PY'],  y, 'LoanCreate(book_id=…, member_id=…)', num='4')
y -= 0.60
ret_msg(A['PY'],   A['LR'],  y, ':LoanCreate  (validated)', num='5')

step_divider(y - 0.15, 'availability check')
y -= 0.55

sync_msg(A['LR'],  A['DB'],  y, 'select(Book).where(Book.id == book_id)', num='6')
y -= 0.60
sync_msg(A['DB'],  A['PG'],  y, 'SELECT * FROM books WHERE id = ?', num='7')
y -= 0.60
ret_msg(A['PG'],   A['DB'],  y, '{book row}', num='8')
y -= 0.60
ret_msg(A['DB'],   A['LR'],  y, 'book: Book  (ORM instance)', num='9')

# alt frame: book available?
alt_y_top = y - 0.10
alt_h     = 3.60
alt_div   = alt_y_top - 1.20    # [else] starts here
alt_frame(A['BR']-1.25, alt_y_top, A['PG']-A['BR']+2.5, alt_h,
          '[book.available == False]', alt_div, '[else]  book.available == True')

y -= 0.55
ret_msg(A['LR'],  A['API'],  y, 'HTTP 400  "Book not available"', num='10a', color='#F87171')
y -= 0.55
ret_msg(A['API'], A['LP'],   y, 'raise APIError', color='#F87171')
y -= 0.55
ret_msg(A['LP'],  A['BR'],   y, 'show error toast', color='#F87171')

step_divider(y - 0.15, 'book is available → create loan')
y -= 0.55

sync_msg(A['LR'], A['DB'],   y, 'db.add(Loan(book_id, member_id, borrowed_at=now()))', num='11')
y -= 0.65
sync_msg(A['LR'], A['DB'],   y, 'book.available = False', num='12')
y -= 0.65
sync_msg(A['DB'], A['PG'],   y, 'INSERT INTO loans …  +  UPDATE books SET available=false', num='13')
y -= 0.60
ret_msg(A['PG'],  A['DB'],   y, 'COMMIT  OK', num='14')
y -= 0.60
ret_msg(A['DB'],  A['LR'],   y, 'loan.id = {new_id}', num='15')
y -= 0.65
ret_msg(A['LR'],  A['API'],  y, 'HTTP 201  LoanOut  { id, book_id, member_id, borrowed_at }', num='16')
y -= 0.65
ret_msg(A['API'], A['LP'],   y, '{ loan }', num='17')
y -= 0.65
ret_msg(A['LP'],  A['BR'],   y, 'refresh loans list, disable Borrow button', num='18')

# Note: due_date
note_box(A['DB']-0.4, 2.50, 3.90,
         ['Note: due_date = borrowed_at + 14 days',
          'Overdue checked lazily on read (not stored)'])

# ═════════════════════════════════════════════════════════════════════════════
# PANEL 2 – RETURN A BOOK + FINE  (right half, x: 15.8 → 31.9)
# ═════════════════════════════════════════════════════════════════════════════
panel_bg(15.80, 0.10, 16.00, 22.90, PANEL2, 'Scenario 2:  Return a Book  +  Fine Calculation')

B = dict(
    BR  = 17.00,
    LP  = 19.10,
    API = 21.10,
    LR  = 23.10,
    LN  = 24.90,   # Loan ORM
    DB  = 26.80,
    PG  = 28.80,
)

actor_labels2 = {
    'BR':  ('Browser',    ''),
    'LP':  ('LoansPage',  'Next.js'),
    'API': ('api.ts',     'fetch wrapper'),
    'LR':  ('LoansRouter','FastAPI'),
    'LN':  ('Loan',       'ORM entity'),
    'DB':  ('AsyncSession','SQLAlchemy'),
    'PG':  ('PostgreSQL', ':5432'),
}
actor_colors2 = {
    'BR':  '#374151', 'LP':  '#065F46', 'API': '#065F46',
    'LR':  '#92400E', 'LN':  '#1D4ED8', 'DB':  '#1E3A8A', 'PG': '#0C4A6E',
}
for k, (lbl, sub) in actor_labels2.items():
    actor_head(B[k], Y_ACT, lbl, sub, color=actor_colors2[k])
    lifeline(B[k], Y_ACT, Y_BOT)

activation(B['LP'],  21.50, 1.40, '#065F46')
activation(B['API'], 20.50, 2.10, '#059669')
activation(B['LR'],  19.50, 3.00, '#D97706')
activation(B['LN'],  16.50, 15.10, '#1D4ED8', w=0.14)
activation(B['DB'],  14.80, 3.60, '#2563EB')
activation(B['PG'],  14.50, 3.90, '#0284C7')

y = 21.30
sync_msg(B['BR'],  B['LP'],  y, 'click  "Return"  (loan_id)', num='1')
y -= 0.70
sync_msg(B['LP'],  B['API'], y, 'returnBook(loan_id)', num='2')
y -= 0.70
sync_msg(B['API'], B['LR'],  y, 'PUT /loans/{id}/return', num='3')

step_divider(y - 0.20, 'fetch existing loan')
y -= 0.60

sync_msg(B['LR'],  B['DB'],  y, 'get(Loan, loan_id, options=[selectinload(book)])', num='4')
y -= 0.65
sync_msg(B['DB'],  B['PG'],  y, 'SELECT loans JOIN books WHERE loans.id = ?', num='5')
y -= 0.60
ret_msg(B['PG'],   B['DB'],  y, '{loan row + book row}', num='6')
y -= 0.60
ret_msg(B['DB'],   B['LR'],  y, 'loan: Loan  (ORM + eager-loaded book)', num='7')

# opt: already returned?
opt_y_top = y - 0.12
opt_frame(B['BR']-1.1, opt_y_top, B['PG']-B['BR']+2.3, 1.60,
          '[loan.returned_at is not None]')
y -= 0.50
ret_msg(B['LR'],   B['API'], y, 'HTTP 400  "Already returned"', color='#F87171', num='8a')
y -= 0.50
ret_msg(B['API'],  B['LP'],  y, 'show error', color='#F87171')
y -= 0.65

step_divider(y - 0.10, 'calculate fine (lazy, computed at return time)')
y -= 0.55

self_msg(B['LR'],  y,  'overdue_days = max(0, (now() − due_date).days)', num='9', color=GUARD)
y -= 0.80
self_msg(B['LR'],  y,  'fine_amount  = overdue_days × settings.FINE_PER_DAY', num='10', color=GUARD)

note_box(B['LR']+0.30, y-0.10, 5.80,
         ['FINE_PER_DAY loaded from Settings (env)',
          'due_date = borrowed_at + timedelta(days=14)',
          'fine = 0 if returned on time'])
y -= 1.10

step_divider(y - 0.10, 'persist return + release book')
y -= 0.55

sync_msg(B['LR'],  B['LN'],  y, 'loan.returned_at = datetime.utcnow()', num='11')
y -= 0.65
sync_msg(B['LR'],  B['LN'],  y, 'loan.fine_amount = fine_amount', num='12')
y -= 0.65
sync_msg(B['LR'],  B['LN'],  y, 'loan.book.available = True', num='13')
y -= 0.70
sync_msg(B['LR'],  B['DB'],  y, 'db.add(loan)  /  await db.commit()', num='14')
y -= 0.65
sync_msg(B['DB'],  B['PG'],  y, 'UPDATE loans SET returned_at=?, fine=?  +  UPDATE books SET available=true', num='15')
y -= 0.60
ret_msg(B['PG'],   B['DB'],  y, 'COMMIT  OK', num='16')
y -= 0.60
sync_msg(B['DB'],  B['LR'],  y, 'await db.refresh(loan)', num='17')
y -= 0.70
ret_msg(B['LR'],   B['API'], y, 'HTTP 200  LoanOut  { returned_at, fine_amount, is_overdue=False }', num='18')
y -= 0.65
ret_msg(B['API'],  B['LP'],  y, '{ updated loan }', num='19')
y -= 0.65
ret_msg(B['LP'],   B['BR'],  y, 'show fine amount, mark loan as returned', num='20')

# ── Legend ────────────────────────────────────────────────────────────────────
legend_items = [
    Line2D([0],[0], color=CALL,    lw=2.0, label='Synchronous call'),
    Line2D([0],[0], color=RET,     lw=1.5, ls='--', label='Return message'),
    Line2D([0],[0], color='#F87171', lw=1.5, ls='--', label='Error response'),
    Line2D([0],[0], color=GUARD,   lw=1.5, label='Guard / alt condition'),
    mpatches.Patch(fc=ALT_BG, ec=GUARD,   alpha=0.5, label='alt  (conditional)'),
    mpatches.Patch(fc='#1F2937', ec='#6B7280', alpha=0.6, label='opt  (optional)'),
    mpatches.Patch(fc=ACT_BOX, ec='#93C5FD', label='Activation box (executing)'),
]
leg = ax.legend(handles=legend_items, loc='lower center',
                fontsize=8.5, framealpha=0.15,
                edgecolor='#475569', ncol=7,
                bbox_to_anchor=(0.5, 0.001))
leg.get_frame().set_linewidth(1.2)
for text in leg.get_texts():
    text.set_color('#CBD5E1')

plt.savefig('D:/InterviewPrep/Numino/DLD/Sequence_Diagram.png',
            dpi=160, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Sequence Diagram saved.")
