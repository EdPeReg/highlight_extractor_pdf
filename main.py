#!/usr/bin/env python3

import logging
import sys
from datetime import datetime

from pathlib import Path
from pdf import PDF

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

def create_folder(path: Path):
    if not path.exists():
        logging.info(f"Folder '{path}' doesn't exist, creating folder")
        path.mkdir(parents=True, exist_ok=True)

def write_file(file: Path, text: str, page_no: int):
    """Create a new file if it doesn't exist or append the text to an existing file"""
    if not file.exists():
        logging.info(f"Markdown file '{file}' doesn't exist, creating file with PDF page {page_no}")

        final_text = f"""
---
Created: {datetime.now().isoformat(timespec="seconds")}
---\n\n{text}"""

        file.write_text(final_text)
    else:
        logging.info(f"Markdown file exist, using existing file '{file}' with PDF page {page_no}")
        with open(file, mode="a", encoding="utf-8") as f:
            f.write(text)

def main():
    if len(sys.argv) < 5:
        logging.error("Arguments missing, expected " \
                      "<PDF file path> <markdown workspace> " \
                      "<page number start> <page number end>")
        sys.exit(1)

    file_path = Path(sys.argv[1]).expanduser()
    pdf = PDF(file_path)
    workspace = Path(sys.argv[2])
    page_start, page_end = int(sys.argv[3]), int(sys.argv[4])
    bookname = workspace / file_path.stem

    create_folder(bookname)
    for page_no in range(page_start, page_end):
        pdf.setup_page(page_no)
        pdf.get_headers()

        headers_per_page = pdf.get_headers_for_page()
        text = pdf.plain_text_to_markdown()

        if not text:
            logging.info(f"No text to process on page {page_no}. Skipping.")
            continue

        print(headers_per_page)
        subfolder1 = bookname / headers_per_page[0][1]
        file = (subfolder1 / f"{headers_per_page[1][1]}.md").expanduser()

        create_folder(subfolder1)
        write_file(file, text, page_no)

if __name__ == "__main__":
    main()
