# Neon Leap

A pygame-ce vertical jumper inspired by Doodle Jump. Bounce up a route of 40 platforms to reach the summit flag, collecting energy shards along the way. Cyan platforms glow through three altitude-based visual acts: two facing wireframe heads with jump-triggered pulsing connections below height 1300, a blue color placeholder from 1300, and a plum color placeholder from 2600. Each bounce activates a different set of connections, with light packets traveling between the heads. Phases follow the maximum height of the current run and reset when you restart. No music or external assets are required. All artwork is drawn in code.

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

Customize `PHASE_HEIGHTS` and `PHASE_COLORS` near the top of `main.py` to adjust the visual acts.
