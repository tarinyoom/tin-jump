# Neon Leap

A pygame-ce vertical jumper inspired by Doodle Jump. Bounce up a route of 40 platforms to reach the summit flag, collecting energy shards along the way. Cyan platforms glow against a purple perspective laser grid, rotating rings, and pink landing bursts. Background animation follows a simulated 120 BPM pulse; no music or external assets are required. All artwork is drawn in code.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, activate with `.venv\Scripts\activate` instead.

Steer with **A/D** or **Left/Right**. Jumping is automatic whenever you land. Platforms allow you to jump through them from below, and the screen wraps horizontally. The camera follows your climb; falling below the screen ends the run. **R** restarts and **Escape** quits. Your best height is kept for the current session.

Edit `make_level()` to change the platform route. `LEVEL_STEPS`, `PLATFORM_GAP`, and the physics settings are near the top of `main.py`.
