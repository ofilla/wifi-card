import argparse

from .wifi_card import WifiCard

parser = argparse.ArgumentParser()

parser.add_argument(
    'SSID',
    help="SSID of the network"
)
parser.add_argument(
    '--output', '-o',
    help="save card in this file"
)
parser.add_argument(
    '--show', '-s',
    action='store_true',
    help="show resulting card"
)
parser.add_argument(
    '--hidden',
    action='store_true',
    help="indicate a hidden (stealth) SSID is used"
)
parser.add_argument(
    '--type', '-t',
    choices=(WifiCard.WPA, WifiCard.WEP, WifiCard.OPEN),
    default=WifiCard.WPA,
    help="encryption type - WEP untested (default: WPA)"
)
parser.add_argument(
    '--password', '-p',
    default='',
    help='password for access'
)


if __name__ == "__main__":
    args = parser.parse_args()
    card = WifiCard(args.SSID, args.hidden)

    card.type = args.type
    card.password = args.password

    card.make_card()

    if args.output is not None:
        card.save(args.output)
    if args.show:
        card.show()
