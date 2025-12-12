import fitz  # PyMuPDF
from PIL import Image
import pdf417gen
import io
import os
import sys

# ==============================
# CONFIG
# ==============================
BARCODE_SCALE = 4
SECURITY_LEVEL = 2
COLUMN_CANDIDATES = [4, 3, 2]

LEFT_MARGIN = 10
BARCODE_WIDTH_RATIO = 0.09

MASK_RATIO = 0.20  # 0.0 = none, 0.5 = left half, 1.0 = full page

# ==============================
# PDF417 GENERATION
# ==============================
def generate_pdf417_image(data: str) -> Image.Image:
    last_error = None
    for cols in COLUMN_CANDIDATES:
        try:
            codes = pdf417gen.encode(
                data,
                columns=cols,
                security_level=SECURITY_LEVEL
            )
            img = pdf417gen.render_image(codes, scale=BARCODE_SCALE)
            return img.convert("RGB")
        except ValueError as e:
            last_error = e
    raise RuntimeError("Unable to generate PDF417") from last_error

# ==============================
# FIRST LINE EXTRACTION
# ==============================
def get_first_line(page):
    blocks = page.get_text("blocks")
    if not blocks:
        return None

    blocks.sort(key=lambda b: (b[1], b[0]))

    for block in blocks:
        text = block[4].strip()
        if text:
            return text.splitlines()[0].strip()

    return None

# ==============================
# MAIN PROCESS
# ==============================
def process_pdf(input_pdf):
    doc = fitz.open(input_pdf)

    # Clamp mask ratio once
    mask_ratio = max(0.0, min(1.0, MASK_RATIO))

    for page_num, page in enumerate(doc, start=1):
        page_width = page.rect.width
        page_height = page.rect.height

        # --------------------------
        # MASK LEFT PORTION OF PAGE
        # --------------------------
        if mask_ratio > 0.0:
            mask_rect = fitz.Rect(
                0,
                0,
                page_width * mask_ratio,
                page_height
            )

            page.draw_rect(
                mask_rect,
                color=None,
                fill=(1, 1, 1),
                overlay=True
            )

        first_line = get_first_line(page)
        if not first_line:
            print(f"Page {page_num}: no text found")
            continue

        barcode_img = generate_pdf417_image(first_line)
        barcode_img = barcode_img.rotate(-90, expand=True)

        img_bytes = io.BytesIO()
        barcode_img.save(img_bytes, format="PNG")

        barcode_width = page_width * BARCODE_WIDTH_RATIO

        img_w, img_h = barcode_img.size
        scale = barcode_width / img_w
        barcode_height = img_h * scale

        y0 = (page_height - barcode_height) / 2

        insert_rect = fitz.Rect(
            LEFT_MARGIN,
            y0,
            LEFT_MARGIN + barcode_width,
            y0 + barcode_height
        )

        page.insert_image(
            insert_rect,
            stream=img_bytes.getvalue(),
            keep_proportion=True
        )

        print(f"Page {page_num}: masked ({mask_ratio}) and barcode affixed")

    output_pdf = os.path.splitext(input_pdf)[0] + "_updated.pdf"
    doc.save(output_pdf)
    doc.close()

    print(f"\nSaved: {output_pdf}")

# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 barcode_affix.py input.pdf")
        sys.exit(1)

    process_pdf(sys.argv[1])
