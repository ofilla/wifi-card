import unittest
import warnings

from warnings import warn, catch_warnings, filterwarnings
from .qr_card import QRCard


class WifiCard(QRCard):
    """
    WIFI-qr = “WIFI:” [type “;”] [trdisable “;”] ssid “;” [hidden “;”] [id “;”] [password “;”] [public-key “;”] “;”
    type = “T:” *(unreserved) ; security type
    trdisable = “R:” *(HEXDIG) ; Transition Disable value
    ssid = “S:” *(printable / pct-encoded) ; SSID of the network
    hidden = “H:true” ; when present, indicates a hidden (stealth) SSID is used
    id = “I:” *(printable / pct-encoded) ; UTF-8 encoded password identifier, present if the password has an SAE password identifier
    password = “P:” *(printable / pct-encoded) ; password, present for password-based authentication
    public-key = “K:” *PKCHAR ; DER of ASN.1 SubjectPublicKeyInfo in compressed form and encoded in “base64” as per [6], present when the network supports SAE-PK, else absent
    printable = %x20-3a / %x3c-7e ; semi-colon excluded
    PKCHAR = ALPHA / DIGIT / %x2b / %x2f / %x3d
    """

    WPA = 'WPA'
    WEP = 'WEP'
    OPEN = 'No encryption'

    def __init__(self, ssid: str, hidden=False, draw_border=True, width_used_by_qr_image=0.8):
        super().__init__(width_used_by_qr_image)
        self.shall_draw_border = draw_border

        self.type = self.WPA
        self.trdisable = ''
        self.ssid = ssid
        self.hidden = hidden
        self.password = ''
        self.public_key = ''
        self.id_printable = ''

    def make_card(self):
        self.add_qr_code(self.uri())

        self.add_bold_text_line("SSID")
        self.add_text_line(self.ssid)

        self.add_text_line('')
        self.add_bold_text_line("Password")
        self.add_text_line(self.password)

        self.add_text_line('')
        if self.type == self.WPA:
            self.add_bold_text_line("Encryption")
            self.add_text_line('WPA/WPA2')
        elif self.type == self.WEP:
            self.add_bold_text_line("Encryption")
            self.add_text_line('WEP')
        else:
            self.add_bold_text_line("No Encryption")

        if self.shall_draw_border:
            self.draw_border(self.font_size)

    def uri(self) -> str:
        uri = "WIFI:"

        if self._type():
            uri += f"T:{self.type};"
        if self.trdisable:
            uri += f"R:{self.trdisable};"
        uri += f"S:{self.ssid};"
        if self.hidden:
            uri += "H:true;"
        if self.id_printable:
            uri += f"I:{self.id_printable};"
        if self.password:
            uri += f"P:{self.password};"
        if self.public_key:
            uri += f"K:{self.public_key};"

        uri += ";"
        return uri

    def _type(self) -> bool:
        if self.type == self.WEP:
            warn("WEP is not implemented yet, it may be wrong")
        if self.type not in (self.OPEN, self.WEP, self.WPA):
            raise ValueError(f"only types ({(self.OPEN, self.WEP, self.WPA)}) are valid")
        return self.type != ""


class TestWifiCard(unittest.TestCase):
    ssid = 'SSID'

    def test_making_card_works(self):
        card = WifiCard(self.ssid, hidden=False)
        card.make_card()

    def test_uri_only_SSID(self):
        card = WifiCard(self.ssid)

        expected = "WIFI:T:WPA;S:SSID;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_hidden_position(self):
        card = WifiCard(self.ssid, hidden=True)
        card.id_printable = "ID"  # field after hidden

        expected = "WIFI:T:WPA;S:SSID;H:true;I:ID;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_type_WPA_position(self):
        card = WifiCard(self.ssid)
        card.type = WifiCard.WPA
        card.trdisable = "tr"  # field after type

        expected = "WIFI:T:WPA;R:tr;S:SSID;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_type_open(self):
        card = WifiCard(self.ssid)
        card.type = WifiCard.OPEN

        expected = f"WIFI:T:{WifiCard.OPEN};S:SSID;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_different_type(self):
        card = WifiCard(self.ssid)
        card.type = "No encryption"

        expected = "WIFI:T:No encryption;S:SSID;;"
        self.assertEqual(card.uri(), expected)

    def test_type_WEP_warns(self):
        card = WifiCard(self.ssid)
        card.type = "WEP"

        expected = "WIFI:T:WEP;S:SSID;;"
        self.assertWarns(
            UserWarning,
            card.uri
        )

    def test_uri_type_WEP_position(self):
        card = WifiCard(self.ssid)
        card.type = "WEP"

        expected = "WIFI:T:WEP;S:SSID;;"

        with warnings.catch_warnings():
            filterwarnings('ignore', category=UserWarning)
            result = card.uri()
        self.assertEqual(result, expected)

    def test_uri_trdisable_position(self):
        card = WifiCard(self.ssid)
        card.type = WifiCard.WPA  # field before trdisable
        card.trdisable = 'trhex'

        expected = "WIFI:T:WPA;R:trhex;S:SSID;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_id_position(self):
        card = WifiCard(self.ssid)
        card.hidden = True  # field before id
        card.id_printable = 'id'
        card.password = 'pw'  # field after id

        expected = "WIFI:T:WPA;S:SSID;H:true;I:id;P:pw;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_password_position(self):
        card = WifiCard(self.ssid)
        card.id_printable = 'id'  # field before password
        card.password = 'passwd'
        card.public_key = 'key'  # field after password

        expected = "WIFI:T:WPA;S:SSID;I:id;P:passwd;K:key;;"
        self.assertEqual(card.uri(), expected)

    def test_uri_public_key_position(self):
        card = WifiCard(self.ssid)
        card.password = 'passwd'  # field before public key
        card.public_key = 'key'

        expected = "WIFI:T:WPA;S:SSID;P:passwd;K:key;;"
        self.assertEqual(card.uri(), expected)


if __name__ == "__main__":
    unittest.main()
