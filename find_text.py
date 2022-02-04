import string
import tkinter

import pytesseract
import cv2
import PIL.ImageGrab
import PIL.Image
import PIL.ImageTk
import numpy
import pyautogui


TRANSPARENT_COLOR_TARGET = "#FF00FE"


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


class FindText:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=TRANSPARENT_COLOR_TARGET)
        # Done to be able to have the window be transparent but have opaque elements.
        # Using "-alpha" affects all the window and all children.
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR_TARGET)
        self.canvas = tkinter.Canvas(self.root, highlightthickness=0, bg=TRANSPARENT_COLOR_TARGET)
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.root.bind("<Key>", lambda x: self.on_any_key_pressed(x))
        self.root.bind("<Escape>", lambda x: self.on_cancel_key_pressed(x))
        self.root.bind("<FocusIn>", lambda x: self.on_focus_in(x))
        self.root.bind("<FocusOut>", lambda x: self.on_focus_out(x))

        self._images_cache = list()
        self._first_focus = True
        self._click_target_text_to_positions = dict()

    def search(self, target_text: str):
        self._images_cache.clear()

        screen_image = numpy.asarray(PIL.ImageGrab.grab())
        gray_scale = get_grayscale(screen_image)

        ocr_data = pytesseract.image_to_data(gray_scale, config="--oem 3 --psm 6", output_type=pytesseract.Output.DICT)
        target_indices = FindText.find_target_indices(ocr_data["text"], target_text)
        for i, index_group in enumerate(target_indices):
            for j in index_group:
                (x, y, w, h) = (ocr_data["left"][j], ocr_data["top"][j], ocr_data["width"][j], ocr_data["height"][j])
                # Padding around rectangles to better fit text
                x1 = x - 4
                y1 = y - 2
                x2 = x + w + 4
                y2 = y + h + 2
                rectangle_center = (x1 + ((x2 - x1) / 2), y1 + ((y2 - y1) / 2))
                self.create_rectangle(x - 4, y - 2, x2, y2, outline="#00FF00", width=5)
                click_target_text = self.get_click_target_text(i)
                self.draw_click_target_text(x2, y2, click_target_text)
                self._click_target_text_to_positions[click_target_text] = rectangle_center

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        """
        Create a rectangle with optional alpha kwarg.
        If alpha is provided draw the rectangle by creating a Pillow image
        as tkinter canvas shapes do not support alpha.
        """
        if "alpha" in kwargs:
            alpha = int(kwargs.pop("alpha") * 255)
            fill = kwargs.pop("fill")
            if fill.startswith("#"):
                fill = FindText.hex_to_rgb(fill)
            else:
                fill = self.root.winfo_rgb(fill)
            fill += (alpha,)
            image = PIL.Image.new("RGBA", (x2 - x1, y2 - y1), fill)
            image = PIL.ImageTk.PhotoImage(image)
            self._images_cache.append(image)
            self.canvas.create_image(x1, y1, image=image, anchor="nw")
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    @staticmethod
    def get_click_target_text(index: int):
        alphabet = string.ascii_lowercase.upper()
        alphabet_length = len(alphabet)
        result = ""
        while index >= alphabet_length:
            result += alphabet[0]
            index -= alphabet_length
        return result + alphabet[index]

    def draw_click_target_text(self, x, y, text: str):
        tkinter.Label(self.root, text=text, bg="orange", fg="black").place(x=x, y=y)

    @staticmethod
    def find_target_indices(ocr_text: list, target: str):
        target_split = target.split()
        target_text_split_len = len(target_split)
        indexes = list()

        match_start = None
        current_match_word_index = 0
        for i, result in enumerate(ocr_text):
            if match_start:
                if result.lower() == target_split[current_match_word_index].lower():
                    current_match_word_index += 1
                    if current_match_word_index == target_text_split_len:
                        indexes.append(tuple(range(match_start, i + 1)))
                        current_match_word_index = 0
                        match_start = 0
                else:
                    # indexes.append(tuple(range(match_start, i)))
                    current_match_word_index = 0
                    match_start = 0
            else:
                if result.lower().startswith(target_split[current_match_word_index].lower()):
                    if target_text_split_len == 1:
                        indexes.append(tuple([i]))
                        continue
                    match_start = i
                    current_match_word_index += 1
        return indexes

    @staticmethod
    def hex_to_rgb(value: str) -> tuple:
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    def on_any_key_pressed(self, event):
        if event.char not in string.ascii_lowercase:
            self.close()

        # Todo handle multiple character targets
        target = self._click_target_text_to_positions.get(event.char.upper())
        if target is None:
            self.close()
            return
        pyautogui.click(x=target[0], y=target[1])
        self.close()

    def on_focus_in(self, event):
        self._first_focus = False

    def on_focus_out(self, event):
        if not self._first_focus:
            self.close()

    def close(self):
        self.root.destroy()

    def on_cancel_key_pressed(self, event):
        self.close()
