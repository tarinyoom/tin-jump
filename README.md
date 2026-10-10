# Little Leap

A tiny pygame-ce side-scroller with grassy platforms, coins, a checkpoint, and a finish flag. All artwork is drawn in code, so no assets are needed.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, activate with `.venv\Scripts\activate` instead.

Move with **A/D** or **Left/Right**. Jump with **Space**, **W**, or **Up**; release early for a shorter jump. **R** restarts and **Escape** quits. Reach the flag, collecting coins along the way. Falling respawns you at the latest checkpoint.

Edit `PLATFORM_LAYOUT` in `main.py` to change the level. Physics and window settings are near the top of that file. Uses the standard [pygame-ce API](https://pyga.me/docs/).
