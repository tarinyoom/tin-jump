# Neon Leap

A pygame-ce vertical jumper inspired by Doodle Jump. Bounce up a route of 40 platforms to reach the summit flag, collecting energy shards along the way. Cyan platforms glow through three altitude-based visual acts: two facing white patch-mosaic heads with jump-triggered pulsing connections below height 1300, a blue color placeholder from 1300, and a plum color placeholder from 2600. Each head has a few hundred white patches covering approximately 70% of its silhouette. Twenty straight white lines connect patch centers; each bounce randomly highlights ten lines in brighter white, fading back to the baseline. Phases follow the maximum height of the current run and reset when you restart. No music or external assets are required. All artwork is drawn in code.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Run in a browser

After installing the dependencies above, run this from the project folder with the virtual environment activated:

```bash
python -m pygbag .
```

Open **http://localhost:8000**, wait for loading to finish, and click the game to start. The first load may take longer while the browser downloads the Python and pygame runtime. Keep the terminal running while playing; press **Ctrl+C** to stop the server. Restart the server after changing the game code.

`pygbag.ini` defines which project files and folders to exclude from the game package, including `.venv`, development files, and plans. Commit this configuration so everyone builds with the same exclusions. Generated files under `build/` are ignored by Git.

## Publish to itch.io with GitHub Actions

The `Publish to itch.io` workflow builds with the dependencies in `requirements.txt`, verifies `build/web.zip`, saves it as a GitHub artifact, and uploads it to the itch.io `html5` channel using Butler. Run it manually from GitHub's **Actions** tab or push a tag starting with `v` (for example, `v0.1.0`). Each run replaces the build on that channel.

Configure the following under the GitHub repository's **Settings → Secrets and variables → Actions**:

- Repository variable `ITCH_TARGET`: your itch.io username and project slug, such as `yourname/neon-leap`.
- Repository secret `BUTLER_API_KEY`: your Butler authentication key. Run `butler login` locally, then obtain the key from the itch.io [API keys settings](https://itch.io/user/settings/api-keys) with source `wharf`. See [Butler CI authentication](https://itch.io/docs/butler/login.html).

Create the itch.io project before running the workflow and choose **HTML** as its kind. After the first upload, edit the project and mark the `html5` upload as **This file will be played in the browser**. Butler requires this one-time setting on the site; see [Butler browser uploads](https://itch.io/docs/butler/pushing.html#html-playable-in-browser-games).

Choose **Embed in page**, start with a 600 by 760 viewport and adjust if the loader or canvas is clipped, and enable **Click to Play** and the **Fullscreen Button**. Leave **Mobile Friendly** off while the game uses keyboard controls. Add the description, controls, cover image, and screenshots, test the draft page, then set its visibility to **Public**. Subsequent workflow uploads update the game on the existing page.

## Controls and customization

Steer with **A/D** or **Left/Right**. Jumping is automatic whenever you land. Platforms allow you to jump through them from below, and the screen wraps horizontally. The camera follows your climb; falling below the screen ends the run. **R** restarts and **Escape** quits. Your best height is kept for the current session.

Edit `make_level()` to change the platform route. `LEVEL_STEPS`, `PLATFORM_GAP`, and the physics settings are near the top of `main.py`.

Customize `PHASE_HEIGHTS` and `PHASE_COLORS` near the top of `main.py` to adjust the visual acts.
