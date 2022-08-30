from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from .qr_code_io import QRCodeIO

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)


class QRCard:
    color_mode = 'RGB'
    width = 650  # 5.5 cm
    height = 1004  # 8.5 cm
    font_size = 30

    _font = "/usr/share/vlc/skins2/fonts/FreeSans.ttf"
    _font_bold = "/usr/share/vlc/skins2/fonts/FreeSansBold.ttf"

    def __init__(self, width_used_by_qr_image=0.8):
        self.image = Image.new(
            self.color_mode,
            size=(self.width, self.height),
            color=COLOR_WHITE
        )
        self.width_used_by_qr_image = width_used_by_qr_image
        self.font = ImageFont.truetype(
            self._font,
            self.font_size
        )
        self.font_bold = ImageFont.truetype(
            self._font_bold,
            self.font_size
        )
        relative_offset = (1 - self.width_used_by_qr_image) / 2
        self.offset_for_elements = int(self.width * relative_offset)

        self.written_rows = 0

    def show(self):
        """Show image."""
        self.image.show()

    def add_qr_code(self, content):
        """Add QR code (image) to card."""
        qr_io = QRCodeIO()
        qr_code = qr_io.generate_qr_code(
            content,
            box_size=5,
            border=0
        )

        self.add_qr_code_object(qr_code)

    def add_qr_code_object(self, qr_code):
        """Add QR code (image) to card."""
        width = int(self.width * self.width_used_by_qr_image)
        img = qr_code.make_image().get_image()
        img = img.resize((width, width), resample=Resampling.BOX)

        self.image.paste(
            img,
            (self.offset_for_elements, self.offset_for_elements)
        )

    def save(self, filename):
        self.image.save(filename)

    def add_bold_text_line(self, title):
        height = self._calc_text_position()

        draw = ImageDraw.Draw(self.image, self.color_mode)
        draw.text(
            (self.offset_for_elements, height),
            title,
            COLOR_BLACK,
            font=self.font_bold
        )

    def add_text_line(self, content):
        height = self._calc_text_position()
        draw = ImageDraw.Draw(self.image, self.color_mode)
        draw.text(
            (self.offset_for_elements, height),
            content,
            COLOR_BLACK,
            font=self.font
        )

    def _calc_text_position(self):
        row_number = self.written_rows
        height = self.width + self.font_size * row_number
        self.written_rows += 1
        return height

    def draw_border(self, size):
        """Return ImageOps with border around image."""
        draw = ImageDraw.Draw(self.image, self.color_mode)
        draw.rectangle(
            (0, 0, self.width, self.height),
            outline=COLOR_BLACK,
            width=size
        )

