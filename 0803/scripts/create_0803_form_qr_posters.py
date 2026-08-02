#!/usr/bin/env python3
"""Create scannable 0803 pre-test and post-test QR posters from the 0709 art."""

from pathlib import Path

from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import ERROR_CORRECT_H


OUTPUT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ASSETS = OUTPUT_ROOT.parent / "0709" / "assets"
OUTPUT_ASSETS = OUTPUT_ROOT / "assets"

POSTERS = (
    {
        "reference": "0709前測.png",
        "output": "0803前測.png",
        "url": "https://forms.gle/kXpa4pfufEP6ANqR9",
        "panel": (211, 717, 1395, 1910),
    },
    {
        "reference": "0709後測.png",
        "output": "0803後測.png",
        "url": "https://forms.gle/dpswWBt58qd64CfC6",
        "panel": (211, 717, 1395, 1910),
    },
)


def make_qr(url: str) -> Image.Image:
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=24,
        border=4,
    )
    code.add_data(url)
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB")


def create_poster(spec: dict[str, object]) -> None:
    source = REFERENCE_ASSETS / str(spec["reference"])
    destination = OUTPUT_ASSETS / str(spec["output"])
    left, top, right, bottom = spec["panel"]  # type: ignore[misc]

    poster = Image.open(source).convert("RGB")
    # Restore the poster background, then retain only the QR code's own quiet zone.
    background_color = poster.getpixel((left - 30, top - 30))
    ImageDraw.Draw(poster).rectangle((left, top, right, bottom), fill=background_color)

    qr = make_qr(str(spec["url"]))
    panel_width = right - left
    panel_height = bottom - top
    qr_x = left + (panel_width - qr.width) // 2
    qr_y = top + (panel_height - qr.height) // 2
    poster.paste(qr, (qr_x, qr_y))
    poster.save(destination, format="PNG", optimize=True)


def main() -> None:
    OUTPUT_ASSETS.mkdir(parents=True, exist_ok=True)
    for poster in POSTERS:
        create_poster(poster)


if __name__ == "__main__":
    main()
