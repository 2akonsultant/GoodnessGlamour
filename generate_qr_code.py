"""
Script to generate the static QR code image for the hero section
"""
import qrcode
from PIL import Image

# The URL that the QR code should link to
QR_CODE_URL = "https://virtualaisalon.onrender.com/"

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(QR_CODE_URL)
qr.make(fit=True)

# Create QR code image
img = qr.make_image(fill_color="black", back_color="white")

# Resize to a larger size for better quality (optional)
img = img.resize((400, 400), Image.Resampling.LANCZOS)

# Save the image
output_path = "client/public/qr-code.png"
img.save(output_path)

print(f"QR code generated successfully!")
print(f"URL: {QR_CODE_URL}")
print(f"Saved to: {output_path}")

