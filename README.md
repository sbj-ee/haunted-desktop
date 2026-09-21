# haunt

Halloween **haunted Linux desktop**: shadowy creatures (ghosts, bats, cats, spiders, creeping shadows) occasionally drift across your screen at random intervals, then vanish.

Non-destructive by design — click-through overlay, no focus steal, mute by default.

## Requirements

- Linux with a **composited** desktop (almost everything modern)
- **Python 3.10+**
- **GTK 3** + PyGObject + Cairo:

```bash
# Debian / Ubuntu / Protectli-style
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-cairo

# Fedora
sudo dnf install python3-gobject gtk3 python3-cairo
```

### X11 vs Wayland

| | X11 | Wayland |
|---|-----|---------|
| Click-through (input pass-through) | Reliable via Gdk input shape | Best-effort; some compositors still grab |
| Always-on-top popup | Works | Works on most compositors |

**Recommendation:** run under **X11** (or XWayland session) for the Halloween prank so clicks never hit a ghost. Set `GDK_BACKEND=x11` or `display.backend = "x11"` in config. Pure Wayland is usable but not guaranteed click-through.

## Install

```bash
git clone https://github.com/sbj-ee/haunt.git
cd haunt
python3 -m venv .venv
source .venv/bin/activate
# System GI modules: use --system-site-packages so venv sees apt PyGObject
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
haunt init-config
```

Or without venv (system packages only):

```bash
pip install --user -e .
# ensure ~/.local/bin is on PATH
```

## Run

```bash
# One creature, then exit (good smoke test)
haunt once
haunt once --creature bat

# Background daemon — random spawns
haunt start

# Status / kill switch
haunt status
haunt stop
```

Config: `~/.config/haunt/config.toml` (created by `haunt init-config`).

Useful knobs:

- `spawn.interval_min_s` / `interval_max_s` — how often the house feels haunted  
- `creature.set` — `ghost`, `bat`, `cat`, `spider`, `shadow`  
- `creature.opacity`, `speed_*`, `scale_*`, `lifetime_*`  
- `sound.enabled` — **false** by default (no audio in v0.1)

Logs: `~/.cache/haunt/haunt.log`  
PID: `~/.cache/haunt/haunt.pid`

## systemd --user (optional)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/haunt.service ~/.config/systemd/user/
# Fix ExecStart if haunt is not in ~/.local/bin
systemctl --user daemon-reload
systemctl --user enable --now haunt.service
systemctl --user stop haunt.service   # kill switch
```

Start this only inside a logged-in graphical session so `DISPLAY` is set (or use a desktop autostart `.desktop` instead).

## How it works

1. `haunt start` runs a GTK main loop and schedules the next spawn with a uniform random delay.
2. Each spawn opens a frameless, RGBA, always-on-top `POPUP` window and draws a Cairo silhouette.
3. The window’s **input shape** is set empty so mouse/touch pass through to apps below.
4. The creature drifts (with a light bob), fades, and the window destroys itself.

## Non-goals (v0.1)

- Sound / jump-scare audio  
- System tray icon (CLI + systemd are the toggles)  
- Windows / macOS  

## License

MIT
