# haunted-desktop

Quiet Halloween easter egg for a **Linux desktop that coworkers might see behind you on a meeting camera**.

Soft shadowy silhouettes (wisps, distant bats, floor shades, rare dim glowing eyes) occasionally drift across the screen at random intervals — low opacity, small, slow — then fade. Easy to miss if you aren’t looking. Not cartoonish, not jump-scare, not a screensaver loop.

## Art direction

- **Subtle / natural** — soft silhouettes, cool near-black, no face cutouts or flashy sprites  
- **Clearly haunted** — default opacity ~0.40, moderate size, spawns every ~1–4 minutes  
- **Non-destructive** — click-through overlay, no focus steal, **sound off**  
- **No tray spam** — CLI + optional systemd user unit only  

## Requirements

- Linux with a composited desktop  
- Python 3.10+  
- GTK 3 + PyGObject + Cairo:

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-cairo
```

### X11 vs Wayland

| | X11 | Wayland |
|---|-----|---------|
| Click-through | Reliable (Gdk input shape) | Best-effort |
| Always-on-top | Works | Usually works |

**Prefer X11** (or `GDK_BACKEND=x11`) so clicks never hit a silhouette.

## Install

```bash
git clone https://github.com/sbj-ee/haunted-desktop.git
cd haunted-desktop
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
haunted-desktop init-config
```

CLI aliases: `haunted-desktop` and `haunt`.

## Run

```bash
# One soft silhouette (smoke test)
haunted-desktop once
haunted-desktop once --creature shadow
haunted-desktop once --creature eyes

# Sparse background daemon
haunted-desktop start
haunted-desktop status
haunted-desktop stop          # kill switch
```

Config: `~/.config/haunted-desktop/config.toml`  
(Legacy `~/.config/haunt/config.toml` still loaded if present.)

Defaults are a visible haunt. Turn the dial if you want it quieter or denser:

- `spawn.interval_min_s` / `interval_max_s` (default 60–240s)  
- `creature.opacity` (default `0.40`)  
- `creature.scale_*`, `speed_*`  
- `sound.enabled` — keep `false`

Logs / PID: `~/.cache/haunted-desktop/`

## systemd --user (optional)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/haunted-desktop.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now haunted-desktop.service
systemctl --user stop haunted-desktop.service
```

Only useful inside a graphical session (`DISPLAY` set).

## License

MIT
