"""Plots for the report / demo video."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.lines import Line2D
import numpy as np

STYLE = {'HAZARD': ('^', '#d62728'), 'JUNCTION': ('s', '#1f77b4'), 'HOLE': ('X', '#111111'), 'WAYPOINT': ('o', '#2ca02c')}


def _draw_map(ax, world):
    img = np.where(world.wall, 0.25, 1.0)
    ax.imshow(img, cmap='gray', vmin=0, vmax=1, origin='lower', extent=[0, world.w, 0, world.h], zorder=0)
    ys, xs = np.nonzero(world.hole)
    for y, x in zip(ys, xs):
        ax.add_patch(plt.Rectangle((x * 0.25, y * 0.25), 0.25, 0.25, color='#b00020', alpha=0.45, zorder=1))
    for sx, sy, _ in world.heat:
        ax.plot(sx, sy, marker='*', ms=16, color='orange', mec='red', zorder=2)
    ex, ey = world.entrance
    ax.annotate('ENTRANCE', (ex, ey), (ex + 0.1, ey + 1.0), color='k', fontsize=7, arrowprops=dict(arrowstyle='->'))
    ax.set_xlim(0, world.w); ax.set_ylim(0, world.h); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([])


def _legend(ax):
    items = [Line2D([], [], color='#1f77b4', lw=1, label='true path'),
             Line2D([], [], color='#ff7f0e', lw=1, ls='--', label="Writer's own estimate")]
    for t, (m, c) in STYLE.items():
        items.append(Line2D([], [], marker=m, color='w', mfc=c, mec='k', ms=8, label=t))
    items.append(Line2D([], [], marker='*', color='w', mfc='orange', mec='red', ms=12, label='heat source'))
    ax.legend(handles=items, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=7, frameon=False)


def plot_run(world, hal, writer, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    _draw_map(ax, world)
    tp, ep = np.array(hal.true_path), np.array(hal.est_path)
    ax.plot(tp[:, 0], tp[:, 1], color='#1f77b4', lw=1, zorder=3)
    ax.plot(ep[:, 0], ep[:, 1], color='#ff7f0e', lw=1, ls='--', zorder=3)
    for b in world.beacons:
        m, c = STYLE[b['type']]
        ax.plot(b['true_x'], b['true_y'], marker=m, color=c, mec='k', ms=11, zorder=5)
        ax.annotate(str(b['id']), (b['true_x'], b['true_y']), (b['true_x'] + 0.12, b['true_y'] + 0.12),
                    fontsize=9, weight='bold', zorder=6)
    ax.set_title(f"Writer run - status: {writer.status} | {len(world.beacons)} beacons | path {writer.path_len:.0f} m")
    _legend(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def make_gif(world, hal, path, max_frames=140):
    tp = np.array(hal.true_path)
    stride = max(1, len(tp) // max_frames)
    idx = list(range(0, len(tp), stride)) + [len(tp) - 1]
    fig, ax = plt.subplots(figsize=(8, 5))
    _draw_map(ax, world)
    line, = ax.plot([], [], color='#1f77b4', lw=1.2, zorder=3)
    robot, = ax.plot([], [], 'o', color='#1f77b4', mec='k', ms=9, zorder=6)
    artists = []

    def update(k):
        i = idx[k]
        line.set_data(tp[:i + 1, 0], tp[:i + 1, 1])
        robot.set_data([tp[i, 0]], [tp[i, 1]])
        for (when, b) in hal.beacon_log:
            if when <= i and not any(a[0] == b['id'] for a in artists):
                m, c = STYLE[b['type']]
                pt, = ax.plot(b['true_x'], b['true_y'], marker=m, color=c, mec='k', ms=11, zorder=5)
                tx = ax.annotate(str(b['id']), (b['true_x'], b['true_y']), (b['true_x'] + 0.12, b['true_y'] + 0.12), fontsize=9, weight='bold')
                artists.append((b['id'], pt, tx))
        ax.set_title(f"Writer exploring - beacons dropped: {len(artists)}")
        return line, robot

    FuncAnimation(fig, update, frames=len(idx), blit=False).save(path, writer=PillowWriter(fps=15))
    plt.close(fig)
