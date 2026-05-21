# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

The virtual environment lives at `~/.virtualenvs/dev_color` (Python 3.14, no conda on this machine).

```bash
source ~/.virtualenvs/dev_color/bin/activate
```

## Running the App

```bash
python main.py
```

`KIVY_WINDOW=pygame` is set inside `main.py` via `os.environ.setdefault` — no env var needed at the shell. The Kivy 2.3.1 wheel for Python 3.14 on macOS does not compile the SDL2 extension, so pygame is the only working desktop window backend.

## Verifying Core Logic (No Window Required)

```bash
python -c "
from core.color_harmony import complementary, create_range, check_color_range
r,g,b = create_range([128,64,200], margin=10)
assert check_color_range([130,66,205], r,g,b) and not check_color_range([0,0,0], r,g,b)
print('OK')
"

python -c "
import cv2
from core.color_engine import check_brightness, get_roi, get_dominant_color
img = cv2.imread('path/to/image.jpg')
_, roi = get_roi(img)
assert roi.shape == (200, 200, 3)
print(get_dominant_color(roi))
"
```

## Android Build

Requires Linux or WSL2 — buildozer does not support macOS for Android targets.

```bash
pip install buildozer
buildozer android debug          # first run: ~40 min, downloads NDK/SDK
buildozer android deploy run     # deploy to connected device
```

The APK lands in `bin/`. Use `opencv` (not `opencv-python`) in `buildozer.spec` requirements — that is the recipe name recognized by buildozer.

## Architecture

There are two separate dependency sets: `requirements.txt` is for the desktop dev environment; `buildozer.spec` `requirements =` is for the Android build system. They are not the same format and must be maintained separately.

**Data flow:** `open_image()` → background thread → `cv2.imread` → `check_brightness` → `get_roi` (resize 500×500, crop center 200×200) → `get_dominant_color` (KMeans k=3 on ROI pixels) → `Clock.schedule_once` posts RGB back to main thread → swatch color and hex label update → MATCH enabled when both slots filled → `check_match()` iterates `HARMONY_FUNCTIONS`, calls `create_range` + `check_color_range` per candidate.

**UI binding model:** `ColorBlockScreen` (BoxLayout subclass) exposes `ListProperty` / `StringProperty` / `BooleanProperty` attributes that `colorblock.kv` binds to directly (e.g. `swatch1_rgba`, `match_text`, `btn_match_disabled`). The KV file is auto-loaded by Kivy because the app class is named `ColorBlockApp` → maps to `colorblock.kv`. Never access `self.ids` inside `__init__`; KV ids are only available after KV post-processing.

**Platform branching:** `open_image()` in `main.py` checks `kivy.utils.platform`. On `android`/`ios` it calls `plyer.camera` or `plyer.filechooser`; on everything else it opens a `FileChooserIconView` popup. The two code paths converge at `_on_files_selected`.

**`opencv-python-headless` is required** (not `opencv-python`). The full package bundles a second SDL2 dylib that conflicts with pygame's SDL2 on macOS, causing an immediate crash after the first rendered frame.

## Key Constraints

- `core/color_harmony.py` must stay free of cv2/numpy/sklearn imports — it is pure Python (`colorsys` only) so it can be tested without heavy dependencies.
- All UI mutations from background threads must go through `Clock.schedule_once(callback)`.
- `check_color_range` returns `True` when the color IS in range (a match). The original `qt.py` had this inverted (`if not checkClrRange` showed "MATCH") — do not reintroduce that bug.
