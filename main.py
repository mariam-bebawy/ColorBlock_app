import os
import threading
import tempfile

# On desktop macOS/Linux, the Kivy SDL2 extension may not be compiled;
# fall back to the pygame window backend when no explicit choice is set.
os.environ.setdefault("KIVY_WINDOW", "pygame")

import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

from core.color_engine import (
    check_brightness, get_roi, get_dominant_color,
    rgb_to_hex, load_colors_csv,
)
from core.color_harmony import HARMONY_FUNCTIONS, create_range, check_color_range


class ColorBlockScreen(BoxLayout):
    swatch1_rgba = ListProperty([0.882, 0.882, 0.882, 1])
    swatch2_rgba = ListProperty([0.882, 0.882, 0.882, 1])
    match_text = StringProperty("")
    btn_match_disabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._clr1 = []
        self._clr2 = []

    # ------------------------------------------------------------------
    # Image loading entry point
    # ------------------------------------------------------------------

    def open_image(self, slot, source):
        if platform in ("android", "ios"):
            self._open_native(slot, source)
        else:
            self._show_file_chooser(slot)

    def _open_native(self, slot, source):
        if source == "camera":
            try:
                from plyer import camera
                tmp = os.path.join(tempfile.gettempdir(), f"colorblock_{slot}.jpg")
                camera.take_picture(
                    filename=tmp,
                    on_complete=lambda path: self._on_files_selected([path], slot),
                )
            except Exception:
                self._show_file_chooser(slot)
        else:
            try:
                from plyer import filechooser
                filechooser.open_file(
                    on_selection=lambda sel: self._on_files_selected(sel, slot),
                    filters=[("Images", "*.jpg", "*.jpeg", "*.png", "*.webp")],
                )
            except Exception:
                self._show_file_chooser(slot)

    def _show_file_chooser(self, slot):
        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"],
            path=os.path.expanduser("~"),
        )
        btn = Button(
            text="Select",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=(0.008, 0.576, 0.545, 1),
        )
        content.add_widget(chooser)
        content.add_widget(btn)

        popup = Popup(
            title=f"Select Image {slot}",
            content=content,
            size_hint=(0.95, 0.9),
        )
        btn.bind(on_press=lambda _: self._on_files_selected(chooser.selection, slot, popup))
        popup.open()

    # ------------------------------------------------------------------
    # Image processing (runs in background thread)
    # ------------------------------------------------------------------

    def _on_files_selected(self, selection, slot, popup=None):
        if popup:
            popup.dismiss()
        if not selection:
            return
        path = selection[0]
        threading.Thread(
            target=self._process_image,
            args=(path, slot),
            daemon=True,
        ).start()

    def _process_image(self, path, slot):
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            Clock.schedule_once(lambda dt: self._show_error("Could not load image."))
            return

        if not check_brightness(img_bgr, threshold=150):
            Clock.schedule_once(lambda dt: self._show_brightness_warning())
            return

        _, roi = get_roi(img_bgr)
        dominant = get_dominant_color(roi, n_clusters=3)
        hex_str = rgb_to_hex(dominant)
        rgb_ints = [int(dominant[0]), int(dominant[1]), int(dominant[2])]
        rgba_kivy = [dominant[0] / 255, dominant[1] / 255, dominant[2] / 255, 1]

        def update_ui(dt):
            if slot == 1:
                self._clr1 = rgb_ints
                self.swatch1_rgba = rgba_kivy
                self.ids.hex_label_1.text = hex_str
            else:
                self._clr2 = rgb_ints
                self.swatch2_rgba = rgba_kivy
                self.ids.hex_label_2.text = hex_str
            self.btn_match_disabled = not (len(self._clr1) == 3 and len(self._clr2) == 3)

        Clock.schedule_once(update_ui)

    # ------------------------------------------------------------------
    # Match logic
    # ------------------------------------------------------------------

    def check_match(self):
        if len(self._clr1) != 3 or len(self._clr2) != 3:
            return
        for harmony_fn in HARMONY_FUNCTIONS:
            for candidate in harmony_fn(self._clr1):
                r_rng, g_rng, b_rng = create_range(candidate, margin=10)
                if check_color_range(self._clr2, r_rng, g_rng, b_rng):
                    self.match_text = "IT'S A MATCH! :D"
                    return
        self.match_text = "NOT A MATCH :("

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def clear(self):
        self._clr1 = []
        self._clr2 = []
        self.swatch1_rgba = [0.882, 0.882, 0.882, 1]
        self.swatch2_rgba = [0.882, 0.882, 0.882, 1]
        self.match_text = ""
        self.btn_match_disabled = True
        self.ids.hex_label_1.text = ""
        self.ids.hex_label_2.text = ""

    # ------------------------------------------------------------------
    # Error / warning popups
    # ------------------------------------------------------------------

    def _show_error(self, msg):
        Popup(
            title="Error",
            content=Label(text=msg),
            size_hint=(0.75, 0.3),
        ).open()

    def _show_brightness_warning(self):
        Popup(
            title="Image Too Dark",
            content=Label(
                text="Please use a brighter image\nor better lighting.",
                halign="center",
            ),
            size_hint=(0.75, 0.35),
        ).open()


class ColorBlockApp(App):
    def build(self):
        csv_path = os.path.join(os.path.dirname(__file__), "assets", "colors.csv")
        self.color_db = load_colors_csv(csv_path)
        return ColorBlockScreen()


if __name__ == "__main__":
    ColorBlockApp().run()
