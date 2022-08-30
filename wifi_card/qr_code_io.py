import os
import unittest
from tempfile import mktemp

import qrcode

from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image


class QRCodeIO:
    """
    Decode a single qr code from a file.
    """

    def __init__(self, filename=None):
        self.filename = filename

        # init with highest error_correction
        self.error_correction = qrcode.constants.ERROR_CORRECT_H
        self.front_color = 'black'
        self.back_color = 'white'

    def decode(self):
        return self.decode_qr_code(self.filename)

    @staticmethod
    def decode_qr_code(filename):
        """
        Extract and decode a single QR code from a given file.
        A RuntimeError will be raised if not EXACTLY 1 code is found.
        """
        decoded = QRCodeIO.read_from_file(filename)

        results = len(decoded)
        if results == 0:
            raise RuntimeError("Error: cannot extract qr code from file")
        elif results > 1:
            raise RuntimeError("Error: multiple qr codes found in file")

        # exactly 1 code found
        return decoded[0].data.decode()

    @staticmethod
    def read_from_file(filename):
        decoded = decode(
            Image.open(filename),
            symbols=[ZBarSymbol.QRCODE]
        )
        return decoded

    def same_code_as_in(self, filename):
        """
        Check if two files contain the same qr code.
        """
        own = self.decode()
        other = self.decode_qr_code(filename)

        return own == other

    def write_png(self, content: str, filename_suffix='', box_size=3, border=None):
        """
        Write a  as QR code to a png file.

        The filename_suffix will be added to self.filename for the output file.

        Front and back colors are controlled with the instance variables
        front_color and back_color. If the back_color is transparent, the
        code is not readable with this class!
        """
        qr = self.generate_qr_code(content, box_size, border)

        img = qr.make_image(
            fill_color=self.front_color,
            back_color=self.back_color
        )
        img.save(self.filename + filename_suffix)

    def write_txt(self, content: str, filename_suffix='', box_size=3, border=None):
        """
        Write a  as QR code to a text file.

        The filename_suffix will be added to self.filename for the output file.
        """
        qr = self.generate_qr_code(content, box_size, border)

        with open(self.filename + filename_suffix, 'w') as io:
            qr.print_ascii(io, tty=False)

    def generate_qr_code(self, content: str, box_size=3, border=None):
        """
        Generate a QR code from text.

        The box_size parameter controls how many pixels each “box” of the QR code is.

        The border parameter controls how many boxes thick the border should be.
        The default is None, which sets it to box_size/2.
        """
        if border is None:
            border = box_size / 2

        qr = qrcode.QRCode(
            version=None,
            error_correction=self.error_correction,
            box_size=box_size,
            border=border
        )
        qr.add_data(content)
        qr.make(fit=True)

        return qr


class TestDecoding(unittest.TestCase):
    cert = "files/test_code.jpg"
    same = "files/test_code_different_border.jpg"
    diff = "files/different_test_code.jpg"

    def setUp(self) -> None:
        self.decoder = QRCodeIO(self.cert)

    def test_same_file(self):
        result = self.decoder.same_code_as_in(self.cert)
        self.assertTrue(result, 'same file yields different results')

    def test_same_qr_code(self):
        result = self.decoder.same_code_as_in(self.same)
        self.assertTrue(result, 'same qr code yields different results')

    def test_different_code(self):
        result = self.decoder.same_code_as_in(self.diff)
        self.assertFalse(result, 'different qr codes yield to same result')

    def test_cert_content(self):
        result = self.decoder.decode()
        self.assertEqual(result, 'test content')

    def test_different_content(self):
        decoder = QRCodeIO(self.diff)
        result = decoder.decode()
        self.assertEqual(result, 'different content')


class TestIO(unittest.TestCase):
    def setUp(self) -> None:
        self.file = mktemp()

    def tearDown(self) -> None:
        if os.path.isfile(self.file):
            os.remove(self.file)

    def test_read_png(self):
        expected = 'text'
        qr = QRCodeIO(self.file)
        qr.write_png(expected)

        result = qr.decode()

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
