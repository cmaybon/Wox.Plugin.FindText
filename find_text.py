import tkinter
import pytesseract
import cv2
import PIL.ImageGrab
import PIL.Image
import PIL.ImageTk
import numpy


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
        self.root.wm_attributes("-transparentcolor", "#FF00FE")
        self.canvas = tkinter.Canvas(self.root, highlightthickness=0, bg=TRANSPARENT_COLOR_TARGET)
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.root.bind("<Key>", lambda x: self.on_any_key_pressed(x))
        self.root.bind("<FocusIn>", lambda x: self.on_focus_in(x))
        self.root.bind("<FocusOut>", lambda x: self.on_focus_out(x))

        self._images_cache = list()
        self._first_focus = True

    def search(self, target_text: str):
        self._images_cache.clear()

        screen_image = numpy.asarray(PIL.ImageGrab.grab())
        gray_scale = get_grayscale(screen_image)

        ocr_data = pytesseract.image_to_data(gray_scale, config="--oem 3 --psm 6", output_type=pytesseract.Output.DICT)
        target_indices = FindText.find_target_indices(ocr_data["text"], target_text)
        for index_group in target_indices:
            for i in index_group:
                (x, y, w, h) = (ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i])
                # Padding around rectangles to better fit text
                self.create_rectangle(x - 4, y - 2, x + w + 4, y + h + 2, outline="#00FF00", width=5)

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

        if "alpha" not in kwargs:
            self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

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
                if result.lower() == target_split[current_match_word_index].lower():
                    if target_text_split_len == 1:
                        indexes.append(tuple([i]))
                        continue
                    match_start = i
                    current_match_word_index += 1
        return indexes

    @staticmethod
    def hex_to_rgb(value: str) -> tuple:
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

    def on_any_key_pressed(self, event):
        self.close()

    def on_focus_in(self, event):
        self._first_focus = False

    def on_focus_out(self, event):
        if not self._first_focus:
            self.close()

    def close(self):
        self.root.destroy()
