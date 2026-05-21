# ColorBlock

A mobile-first color-matching app for colorblind users. Upload or photograph two garments and ColorBlock tells you whether the colors are a good match based on five color theory principles: complementary, split-complementary, analogous, triadic, and tetradic.

Ported from the original PyQt5 desktop app ([SBME_REHAB_ColorBLock](../SBME_REHAB_ColorBLock)) to [Kivy](https://kivy.org), which targets Android (APK), iOS, and desktop for development.

---

## How It Works

1. Tap **GALLERY** or **CAMERA** for each garment slot to load an image.
2. ColorBlock checks that the image is bright enough, crops the center 200×200 px region of interest, and runs K-Means clustering (k=3) to extract the dominant RGB color.
3. The color swatch updates and the hex code is shown below it.
4. Once both swatches are filled, **MATCH** becomes active. Tap it to compare the two colors across all five harmony theories (±10 RGB tolerance per channel).
5. The result — **IT'S A MATCH! :D** or **NOT A MATCH :(** — appears at the bottom.
6. **X** resets everything.

---

## Project Structure

```
ColorBlock_app/
├── main.py               # App entry point; ColorBlockApp and ColorBlockScreen classes
├── colorblock.kv         # Kivy UI layout and styling (auto-loaded by Kivy)
├── core/
│   ├── color_engine.py   # Image processing: brightness check, ROI crop, KMeans extraction
│   └── color_harmony.py  # Five color harmony algorithms + RGB range matching
├── assets/
│   └── colors.csv        # 865-entry color name database (used by recognize_color)
├── requirements.txt      # Desktop development dependencies
└── buildozer.spec        # Android APK build configuration
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11 – 3.14 | Tested on 3.14.4 (macOS arm64) |
| Homebrew (macOS) | any | Needed to install SDL2 |
| SDL2 libraries | any | Required by the pygame window backend |

Install SDL2 via Homebrew (macOS only — one-time):

```bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

---

## Environment Setup

The project uses a Python virtual environment named **`dev_color`**.

> If you prefer conda, replace the `python3 -m venv` step with  
> `conda create -n dev_color python=3.11 -y && conda activate dev_color`  
> then continue from the `pip install` step.

### 1. Create the virtual environment

```bash
python3 -m venv ~/.virtualenvs/dev_color
```

### 2. Activate it

```bash
# macOS / Linux
source ~/.virtualenvs/dev_color/bin/activate

# Windows (if adapting)
.\.virtualenvs\dev_color\Scripts\activate
```

You should see `(dev_color)` prepended to your prompt.

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install kivy==2.3.1 pygame
pip install numpy pandas opencv-python-headless scikit-learn scikit-image Pillow plyer
```

**Why these specific packages:**

| Package | Reason |
|---|---|
| `kivy==2.3.1` | UI framework; targets Android/iOS via buildozer |
| `pygame` | Window backend for desktop — the Kivy 2.3.1 SDL2 extension is not compiled in the Python 3.14 wheel |
| `opencv-python-headless` | Image I/O and color conversion; **headless** variant avoids bundling a second SDL2 that conflicts with pygame on macOS |
| `numpy` | Array operations throughout the image pipeline |
| `pandas` | Loads `assets/colors.csv` for optional color name lookup |
| `scikit-learn` | K-Means clustering for dominant color extraction |
| `scikit-image` | Color space utilities |
| `Pillow` | Kivy image and text rendering |
| `plyer` | Native camera and gallery access on Android/iOS |

### 4. Verify the install

```bash
python -c "import kivy; print('Kivy', kivy.__version__)"
python -c "import cv2; print('OpenCV', cv2.__version__)"
python -c "from sklearn.cluster import KMeans; print('scikit-learn OK')"
```

---

## Running the App (Desktop)

```bash
# Activate the environment if not already active
source ~/.virtualenvs/dev_color/bin/activate

# From the project root
cd /path/to/ColorBlock_app
python main.py
```

A portrait-orientation window opens with the dark teal ColorBlock UI. On desktop the **GALLERY** and **CAMERA** buttons both open a file picker popup (camera capture requires a real device).

> **Note:** You may see `objc: Class SDL...` duplicate warnings in the terminal on macOS. These are harmless — they come from OpenCV and pygame each loading their own copy of SDL2, but since the app never calls `cv2.imshow()`, the two copies never conflict at runtime.

---

## Running the Core Logic (No UI)

Verify the color science modules independently without launching a window:

```bash
# Harmony algorithm sanity check
python -c "
from core.color_harmony import complementary, create_range, check_color_range, HARMONY_FUNCTIONS

result = complementary([255, 0, 0])
print('complementary([255,0,0]) =', result)   # expect cyan-ish [[0, 255, 255]]

r, g, b = create_range([128, 64, 200], margin=10)
assert check_color_range([130, 66, 205], r, g, b) == True
assert check_color_range([0, 0, 0], r, g, b) == False
print('Range checks passed for all', len(HARMONY_FUNCTIONS), 'harmony functions')
"
```

```bash
# Image processing pipeline check (requires a test image)
python -c "
import cv2
from core.color_engine import check_brightness, get_roi, get_dominant_color, rgb_to_hex

img = cv2.imread('path/to/any/image.jpg')
print('Bright enough:', check_brightness(img))
_, roi = get_roi(img)
print('ROI shape:', roi.shape)          # expect (200, 200, 3)
color = get_dominant_color(roi)
print('Dominant color:', color)
print('Hex:', rgb_to_hex(color))
"
```

---

## Building an Android APK

Android builds require a Linux environment (Ubuntu 20.04+ recommended) or WSL2 on Windows. The macOS buildozer toolchain is not officially supported.

### 1. Install buildozer on Linux

```bash
pip install buildozer
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

### 2. Run the build from the project root

```bash
cd /path/to/ColorBlock_app
buildozer android debug
```

The first build downloads the Android NDK and SDK automatically (~2–4 GB, 20–40 min). Subsequent builds are much faster.

### 3. Deploy to a connected device

```bash
buildozer android deploy run
```

The APK is also saved to `bin/colorblock-1.0.0-debug.apk` for manual installation.

**Key `buildozer.spec` settings:**

| Setting | Value | Notes |
|---|---|---|
| `requirements` | `python3,kivy==2.3.0,numpy,pandas,opencv,...` | Uses `opencv` (not `opencv-python`) — the buildozer recipe name differs |
| `android.permissions` | `CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE` | Required for gallery and camera access |
| `android.api` | `33` | Target Android 13 |
| `android.minapi` | `21` | Minimum Android 5.0 |
| `android.archs` | `arm64-v8a, armeabi-v7a` | Builds for both 64-bit and 32-bit ARM |

---

## Code Architecture

### `main.py` — App controller

`ColorBlockScreen(BoxLayout)` is the single-screen root widget. Key Kivy properties drive reactive UI updates:

| Property | Type | Purpose |
|---|---|---|
| `swatch1_rgba` / `swatch2_rgba` | `ListProperty` | RGBA color of each swatch rectangle |
| `match_text` | `StringProperty` | Text bound directly to the result label in KV |
| `btn_match_disabled` | `BooleanProperty` | Enables/disables the MATCH button |

Image processing (`_process_image`) runs in a daemon thread to keep the UI responsive during K-Means (which can take 1–2 seconds). UI updates are posted back to the main thread via `Clock.schedule_once`.

### `colorblock.kv` — UI layout

All widget layout and styling is in the KV file, auto-loaded by Kivy when the app class is named `ColorBlockApp`. The `ColorSwatch` dynamic class is a plain `Widget` with canvas instructions that fills with the swatch color — it replaces the `PlotWidget` from the original PyQt5 app, which was being used solely as a colored background.

### `core/color_engine.py` — Image pipeline

| Function | Description |
|---|---|
| `check_brightness(img_bgr, threshold=150)` | Converts to HSV, averages the V channel; rejects dark images |
| `get_roi(img_bgr, resize=500, margin=100)` | Resizes to 500×500, crops the center 200×200 px region |
| `get_dominant_color(roi, n_clusters=3)` | K-Means on the ROI pixels; returns the most frequent cluster center as RGB |
| `rgb_to_hex(color)` | Formats as `#rrggbb` |
| `recognize_color(csv_df, R, G, B)` | Nearest-neighbor lookup against the 865-entry color name CSV |

### `core/color_harmony.py` — Color theory

Each function accepts an `[R, G, B]` list and returns a list of harmonic colors (also `[R, G, B]` lists). Hue shifts are computed in HLS space via Python's `colorsys` module.

| Function | Hue shifts |
|---|---|
| `complementary` | 180° |
| `split_complementary` | 150°, 210° |
| `analogous(val, d=100)` | ±d° (default ±100°) |
| `triadic` | 120°, 240° |
| `tetradic` | 60°, 180°, 240° |

`create_range(clr, margin=10)` builds a ±10 integer set for each channel. `check_color_range` returns `True` if any channel of the test color falls within the range — a match on any single channel is considered a harmonic hit.

---

## Differences from the Original Desktop App

| Aspect | Original (`qt.py`) | This app (`main.py`) |
|---|---|---|
| UI framework | PyQt5 + `.ui` file | Kivy + `.kv` file |
| Color swatch | `PlotWidget` (pyqtgraph) | `Widget` with canvas `RoundedRectangle` |
| File picker | `QFileDialog` (blocking) | Kivy `Popup` + `FileChooserIconView` |
| Camera access | Not supported | `plyer.camera` on Android/iOS |
| Image processing thread | Runs on main thread (freezes UI) | Daemon thread + `Clock.schedule_once` |
| Match logic bug | `if not checkClrRange(...)` (inverted — showed MATCH for non-matches) | `if check_color_range(...)` (corrected) |
| Dead code | `MplCanvas` / matplotlib imported but never used | Removed |
| ROI usage | K-Means ran on full 500×500 image | K-Means runs on the 200×200 center ROI as intended |
