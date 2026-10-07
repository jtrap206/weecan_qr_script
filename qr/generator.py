import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap


def generate_qr(data: str) -> QPixmap:
    """
    Generate a QR code from the supplied data
    and return it as a QPixmap that PySide6 can display.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    ).convert("RGB")

    qt_image = ImageQt(image)

    return QPixmap.fromImage(qt_image)