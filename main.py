#!/usr/bin/env python3

import logging
import json
import argparse
import sys
from datetime import datetime

from pathlib import Path
from typing import TextIO
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

def page_is_duplicated(file: TextIO, text: str) -> bool:
    """Check if the line 'Page: X' is already in the text

    Args:
        file (TextIO): A file already open to be processed
        text (str): Text where duplicates are found

    Returns:
        bool: True if the 'Page: X' is duplocated, False othewise.
    """
    page_lines = {line.strip() for line in file if line.startswith("Page: ")}
    return any(page in text for page in page_lines)

def write_file(file: Path, text: str, page_no: int):
    """Create a new file if it doesn't exist or append the text to an existing file"""
    if not file.exists():
        logging.info(f"Markdown file '{file}' doesn't exist, creating file with PDF page {page_no}")

        final_text = f"""
---

# Created: {datetime.now().isoformat(timespec="seconds")}

---\n\n{text}"""

        file.write_text(final_text)
    else:
        with open(file, mode="r+", encoding="utf-8") as f:
            duplicated = page_is_duplicated(f, text)
            if duplicated:
                logging.info(f"Page {page_no} already exist. Skipping.")
            else:
                logging.info(f"Markdown file exist, using existing file '{file}' with PDF page {page_no}")
                f.write(text)

def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser(description="Process PDF highlighted text and generate markdown file")
    parser.add_argument("--config", help="JSON configuration file path", default="config.json")
    args = parser.parse_args()
    config = load_config(args.config)

    file_path = Path(config["pdf_path"]).expanduser()
    pdf = PDF(file_path)
    workspace = Path(config["markdown_workspace"]).expanduser()
    page_start, page_end = int(config["page_start"]), int(config["page_end"])
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

        subfolder = (bookname / headers_per_page[0][1]).expanduser()
        file = (subfolder / f"{headers_per_page[1][1]}.md").expanduser()

        create_folder(subfolder)
        write_file(file, text, page_no)

if __name__ == "__main__":
    main()
