import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

GREY, BLUE, GREEN = '#eeeeee', '#dbe8f5', '#d9ead3'
def box(ax, x, y, w, h, text, fc=GREY, ec='#333', fs=8.5, bold=False, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, weight='bold' if bold else 'normal')
def arrow(ax, p, q, ls='-', color='#222'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=1.3, color=color, ls=ls))

fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 20); ax.set_ylim(-0.6, 10.4); ax.axis('off')
# outer region
ax.add_patch(FancyBboxPatch((4.6, 0.8), 10.9, 7.9, boxstyle='round,pad=0.02,rounding_size=0.25', fc=BLUE, ec='#1f4e79', lw=1.7, ls='--'))
ax.text(10.05, 8.35, 'OUTSIDE NETWORK AREA', ha='center', fontsize=9.5, weight='bold', color='#1f4e79')
ax.text(10.05, 7.95, '(GPS, satellite time and communication exist here)', ha='center', fontsize=7.6, color='#1f4e79')
# writer log in
box(ax, 0.2, 5.6, 3.6, 1.7, 'WRITER robot\nreturns to the entrance\nand uploads its log', GREEN, bold=True, fs=8)
box(ax, 5.2, 5.6, 3.8, 1.7, '1  RECEIVE\ncheck + store the log', GREY, bold=True)
box(ax, 10.6, 5.6, 4.3, 1.7, '2  TRANSLATE\nprivate frame -> GPS', GREY, bold=True)
arrow(ax, (3.8, 6.45), (5.2, 6.45)); ax.text(4.5, 6.65, 'I3', ha='center', fontsize=9, weight='bold')
arrow(ax, (9.0, 6.45), (10.6, 6.45))
# GPS inputs
box(ax, 10.2, 9.0, 5.1, 1.1, 'GPS module: entrance position + GPS time\nBuilding bearing (source: OPEN)', '#ffffff', fs=7.6, ls='--')
arrow(ax, (12.75, 9.0), (12.75, 7.3))
# carry / brief
box(ax, 5.6, 2.9, 4.2, 1.7, '3  CARRY\nsend to the command post', GREY, bold=True)
box(ax, 10.9, 2.9, 4.2, 1.7, '4  BRIEF\nprepare the Executor’s\nmission plan', GREY, bold=True)
arrow(ax, (11.6, 5.6), (8.2, 4.6)); arrow(ax, (13.3, 5.6), (13.0, 4.6))
box(ax, 5.6, 1.1, 4.2, 1.0, 'store-and-forward queue', '#ffffff', fs=8, ls='--')
arrow(ax, (7.7, 2.9), (7.7, 2.1), ls='--')
# outputs
box(ax, 0.2, 2.9, 4.0, 1.7, 'COMMAND POST\nlive map', GREY, bold=True)
arrow(ax, (5.6, 3.75), (4.2, 3.75)); ax.text(4.9, 3.95, 'I4', ha='center', fontsize=9, weight='bold')
box(ax, 16.6, 2.9, 3.2, 1.7, 'EXECUTOR\nrobot', GREY, bold=True)
arrow(ax, (15.1, 3.75), (16.6, 3.75)); ax.text(15.85, 3.95, 'I5', ha='center', fontsize=9, weight='bold')
ax.text(10.05, 0.05, 'I3 = Writer log · I4 = GPS-referenced data for the map · I5 = briefing (mission, beacon chain, clock sync, trust rules)', ha='center', fontsize=7.6, style='italic')
ax.text(10.05, -0.45, 'Green = exists in the Python simulation (the Writer side). Grey = designed only: nothing in the Outside Network exists in code yet.', ha='center', fontsize=7.6, style='italic')
fig.tight_layout(); fig.savefig('/home/claude/netpdf/net_internal.png', dpi=170); plt.close(fig)
print('ok')
