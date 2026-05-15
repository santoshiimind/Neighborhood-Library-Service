import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')
fig.patch.set_facecolor('#F0F4F8')

# ── Docker Compose boundary ──────────────────────────────────────────────────
docker_box = FancyBboxPatch((1.2, 0.6), 13.6, 8.2,
    boxstyle="round,pad=0.15", linewidth=2,
    edgecolor='#2563EB', facecolor='#EFF6FF', zorder=0)
ax.add_patch(docker_box)
ax.text(8, 9.05, 'Docker Compose Environment', ha='center', va='center',
        fontsize=13, fontweight='bold', color='#1D4ED8')

# ── Helper: draw a component box ─────────────────────────────────────────────
def draw_box(x, y, w, h, title, subtitle_lines, bg, border, title_color='white'):
    box = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.1", linewidth=2,
        edgecolor=border, facecolor=bg, zorder=2)
    ax.add_patch(box)
    # title band
    title_band = FancyBboxPatch((x, y + h - 0.65), w, 0.65,
        boxstyle="round,pad=0.05", linewidth=0,
        edgecolor=border, facecolor=border, zorder=3)
    ax.add_patch(title_band)
    ax.text(x + w / 2, y + h - 0.32, title,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=title_color, zorder=4)
    for i, line in enumerate(subtitle_lines):
        ax.text(x + w / 2, y + h - 1.05 - i * 0.42,
                line, ha='center', va='center', fontsize=9,
                color='#374151', zorder=4)

# ── Browser (Client) ─────────────────────────────────────────────────────────
browser_box = FancyBboxPatch((0.1, 3.8), 1.5, 2.4,
    boxstyle="round,pad=0.1", linewidth=2,
    edgecolor='#6B7280', facecolor='#F9FAFB', zorder=2)
ax.add_patch(browser_box)
ax.text(0.85, 5.5, '[Browser]', ha='center', va='center', fontsize=9,
        color='#6B7280', zorder=4)
ax.text(0.85, 4.45, 'Client\nBrowser', ha='center', va='center',
        fontsize=10, fontweight='bold', color='#374151', zorder=4)

# ── Next.js Frontend ─────────────────────────────────────────────────────────
draw_box(2.2, 2.2, 3.6, 5.6,
    'Next.js 14 Frontend',
    ['Port 3000',
     'Pages:',
     '  /books',
     '  /members',
     '  /loans',
     'Tailwind CSS',
     'Fetch API (api.ts)'],
    '#ECFDF5', '#059669')

# ── FastAPI Backend ───────────────────────────────────────────────────────────
draw_box(6.8, 2.2, 3.6, 5.6,
    'FastAPI Backend',
    ['Port 8000',
     'Routers:',
     '  /books',
     '  /members',
     '  /loans',
     'Async SQLAlchemy',
     'Pydantic Schemas'],
    '#FFF7ED', '#EA580C')

# ── PostgreSQL ────────────────────────────────────────────────────────────────
draw_box(11.4, 2.2, 3.6, 5.6,
    'PostgreSQL',
    ['Port 5432',
     'Tables:',
     '  books',
     '  members',
     '  loans',
     'Alembic Migrations',
     'Persistent Volume'],
    '#F0F9FF', '#0284C7')

# ── Arrows ────────────────────────────────────────────────────────────────────
arrow_style = dict(arrowstyle='->', color='#374151', lw=2,
                   connectionstyle='arc3,rad=0.0')

def arrow(x1, y1, x2, y2, label='', rad=0.0, up=True):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#374151', lw=2,
                                connectionstyle=f'arc3,rad={rad}'))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        offset = 0.2 if up else -0.25
        ax.text(mx, my + offset, label, ha='center', va='center',
                fontsize=8, color='#4B5563',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor='none', alpha=0.8))

# Browser ↔ Frontend
arrow(1.6, 5.2, 2.2, 5.2, 'HTTP / HTTPS', rad=-0.0)
arrow(2.2, 4.8, 1.6, 4.8, rad=0.0)

# Frontend ↔ Backend (REST)
arrow(5.8, 5.2, 6.8, 5.2, 'REST API calls', rad=0.0)
arrow(6.8, 4.8, 5.8, 4.8, 'JSON responses', rad=0.0)

# Backend ↔ PostgreSQL
arrow(10.4, 5.2, 11.4, 5.2, 'SQL (async)', rad=0.0)
arrow(11.4, 4.8, 10.4, 4.8, 'Result sets', rad=0.0)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor='#ECFDF5', edgecolor='#059669', label='Frontend Layer'),
    mpatches.Patch(facecolor='#FFF7ED', edgecolor='#EA580C', label='Backend Layer'),
    mpatches.Patch(facecolor='#F0F9FF', edgecolor='#0284C7', label='Data Layer'),
    mpatches.Patch(facecolor='#EFF6FF', edgecolor='#2563EB', label='Docker Compose'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=9,
          framealpha=0.9, edgecolor='#D1D5DB')

# ── Title ─────────────────────────────────────────────────────────────────────
ax.set_title('Neighborhood Library App — High-Level Design (HLD)',
             fontsize=15, fontweight='bold', color='#111827', pad=12)

plt.tight_layout()
plt.savefig('D:/InterviewPrep/Numino/HLD/HLD_diagram.png',
            dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print("HLD diagram saved.")
