# PDF417 Barcode Affixer for PDFs

This script processes a PDF file page by page, extracts the first line of text from each page, encodes that text into a **PDF417 barcode**, and affixes the barcode vertically along the left margin of the page. Optionally, it can mask (white out) a configurable portion of the left side of each page before inserting the barcode.

The output is a new PDF file with the barcodes applied.

---

## Features

- Extracts the **first textual line** from each PDF page
- Generates **PDF417 barcodes** with configurable security and layout
- Automatically retries barcode generation with different column counts
- Inserts the barcode **vertically (rotated −90°)** and centered on the page
- Optionally **masks (whites out)** a portion of the left side of each page
- Preserves original PDF pages and outputs a new file

---

## Requirements

Python 3.8+

### Python Dependencies

Install the required libraries:

```bash
pip install pymupdf pillow pdf417gen
