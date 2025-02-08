from typing import Final, Optional, Any

import unicodedata
import re

import pymupdf
import numpy as np

class PDF:
    """This class represents a PDF highlight extractor given a page"""

    # 5 is our threshold to determine if the words are separated
    # enough to consider them new lines this value can be adjusted as needed.
    VERTICAL_THRESHOLD: Final = 5

    def __init__(self, pdf_path: str):
        self.doc = pymupdf.open(pdf_path)
        self.page: Optional[pymupdf.Page] = None
        self.words: Optional[list] = None
        self.data: dict[Any, Any]

    def setup_page(self, page_no: int) -> None:
        """Setup the corresponding variables given a page"""
        self.page_no = page_no - 1
        self.page = self.doc[self.page_no]
        # Ascending y, then x to mantain the read order
        self.words = self.page.get_text("words", flags=pymupdf.TEXT_DEHYPHENATE, sort=True)
        self.data = self.page.get_text("dict")["blocks"]
        self.highlight_words: list[tuple] = []
        self.headers: list[tuple] = []
        self.bold_italic_text: list[tuple] = []
        self.headers_per_page: list[tuple[Any, ...]] = []

    def get_highlight_text(self) -> list[str]:
        """Get all highlight text from the pdf"""
        self.__extract_highlight_text()
        return self.__format_text(self.highlight_words)

    def get_headers(self) -> list[str]:
        """Get all the headers from the pdf"""
        self.__extract_headers()
        return self.__format_text(self.headers)

    def get_bold_italic_text(self) -> list[str]:
        """Get all the words that are bold/italic"""
        self.__extract_bold_italic_text()
        return [element[4] for element in self.bold_italic_text]

    def get_entire_text(self) -> list[str]:
        """Combine headers and highlight text and return it as a formated text"""
        if not self.highlight_words:
            self.__extract_highlight_text()

        if not self.headers:
            self.__extract_headers()

        final_text = []
        used_headers = set()
        for word in self.highlight_words:
            word_y = word[3]

            if self.headers:
                for header_index, header in enumerate(self.headers):
                    # Get the ranges between headers
                    header_y1 = self.headers[header_index][3]
                    # Avoid to get the last header
                    header_y2 = self.headers[header_index + 1][3] \
                        if header_index + 1 < len(self.headers) \
                        else float("inf")

                    # Insert the header if our highlight text corresponds to that header by
                    # checking the range between headers.
                    if header_index not in used_headers and header_y1 < word_y < header_y2:
                        new_value = "\n\n\n" + header[-1] + "\n\n\n"
                        final_text.append(header[:4] + (new_value,))
                        used_headers.add(header_index)
                        break

            final_text.append(word)

        return self.__format_text(final_text)
        # return "".join(self.__format_text(final_text))

    def get_headers_for_page(self) -> list[tuple[int, str]]:
        """
        Get all headers from te page.

        Having the next format [(level, title)]

        Returns:
            The root title of the header or and empty string if there is not a table
            of content by the PDF file.
        """
        table_of_content = self.doc.get_toc()

        if not self.headers:
            self.__extract_headers()

        if not table_of_content:
            return []
        level_titles = [
            (current_level, title)
            for current_level, title, page in table_of_content
            if page <= self.page_no + 1
        ]

        dummy_header = False
        # If the page doesn't have any headers, just add the last header found
        # to get the complete hierarchy
        if not self.headers:
            dummy_header = True
            # Just add dummy info for the coordinates, we only care the text
            self.headers.append((0,0,0,0,level_titles[-1][1]))

        pattern = r"[^\w\s.]"
        levels_to_add = set()
        for level, header in reversed(level_titles):
            header_clean = re.sub(pattern, "", header).strip()
            header_normalized_clean = unicodedata.normalize("NFKD", header_clean)

            for h in self.headers:
                h_clean = re.sub(pattern, "", h[4]).strip()
                h_normalized_clean = unicodedata.normalize("NFKD", h_clean)

                # Unicode to remove ligatures
                # if h_normalized_clean == header_normalized_clean:
                if h_normalized_clean in header_normalized_clean:
                    self.headers_per_page.append((level, header))
                    # For this header, save the father level that should be saved
                    levels_to_add.add(level - 1)
                    levels_to_add.discard(level)

                # Save the level father
                if level in levels_to_add:
                    self.headers_per_page.append((level, header))
                    levels_to_add.add(level - 1)
                    levels_to_add.discard(level)

        # Remove the dummy header when the page doesn't have any headers
        if dummy_header:
            self.headers = []

        self.headers_per_page = self.headers_per_page[::-1]
        return self.headers_per_page

    def plain_text_to_markdown(self) -> str:
        """Converts a plain text to markdown formt for headers and bold/italic"""
        if not self.highlight_words:
            self.__extract_highlight_text()

        if not self.bold_italic_text:
            self.__extract_bold_italic_text()

        if not self.headers_per_page:
            self.get_headers_for_page()

        if not self.headers:
            self.__extract_headers()

        pattern = r"[^\w\s.]"
        # Lets format the headers according to its level
        for level, header in self.headers_per_page:
            header_clean = re.sub(pattern, "", header).strip()
            normalized_header_clean = unicodedata.normalize("NFKD", header_clean)
            for i, h in enumerate(self.headers):
                h_clean = re.sub(pattern, "", h[4]).strip()
                normalized_h_clean = unicodedata.normalize("NFKD", h_clean)
                # Unicode to remove ligatures
                if normalized_h_clean == normalized_header_clean:
                    self.headers[i] = h[:4] + (f"{'#' * (level - 1)} {h[4]}",)

        used_headers = set()
        final_text = []
        for word in self.highlight_words:
            word_y = word[3]
            word_rect = pymupdf.Rect(word[:4])

            for bold_italic_word in self.bold_italic_text:
                bold_italic_rect = pymupdf.Rect(bold_italic_word[:4])

                if word_rect.intersects(bold_italic_rect):
                    word = word[:4] + (f"**_{word[4]}_**",)
                    break

            if self.headers:
                for header_index, header in enumerate(self.headers):
                    # Get the ranges between headers
                    header_y1 = self.headers[header_index][3]
                    # Avoid to get the last header
                    header_y2 = self.headers[header_index + 1][3] \
                        if header_index + 1 < len(self.headers) \
                        else float("inf")

                    # Insert the header if our highlight text corresponds to that header by
                    # checking the range between headers.
                    if header_index not in used_headers and header_y1 < word_y < header_y2:
                        new_value = "\n\n\n" + header[-1] + "\n\n\n"
                        final_text.append(header[:4] + (new_value,))
                        used_headers.add(header_index)
                        break

            final_text.append(word)

        return "".join(self.__format_text(final_text))

    def __adjust_rectangle(self, rect, margin=1.0):
        return pymupdf.Rect(
            rect.x0,
            rect.y0 + margin, # y inferior
            rect.x1,
            rect.y1 - margin  # y superior
        )

    def __calculate_dynamic_threshold(self, font_sizes: list[float]) -> np.float64:
        """ Calculate a dynamic threshold based on font size distribution. """
        threshold:np.float64 = 0.0
        if font_sizes:
            median_size = np.median(font_sizes)
            std_dev = np.std(font_sizes)
            threshold = median_size + std_dev
        return threshold

    def __get_common_font_size(self) -> list[float]:
        font_size = []

        def collect_font_size(span):
            font_size.append(span["size"])

        self.__process_text_blocks(collect_font_size)
        return font_size

    def __extract_bold_italic_text(self) -> list[tuple]:
        bold_italic_text = []

        def collect_bold_italic_text(span):
            font = span["font"].lower()
            if "bold" in font or "italic" in font:
                bold_italic_text.append((*span["bbox"], span["text"]))

        self.__process_text_blocks(collect_bold_italic_text)

        seen_words = set()
        if not self.highlight_words:
            self.__extract_highlight_text()

        for word in self.highlight_words:
            word_rect = pymupdf.Rect(word[:4])
            for bold_italic_word in bold_italic_text:
                bold_italic_rect = pymupdf.Rect(bold_italic_word[:4])

                if bold_italic_word not in seen_words and bold_italic_rect.intersects(word_rect):
                    new_word = bold_italic_word[:4] + (bold_italic_word[4].strip(),)
                    self.bold_italic_text.append(new_word)
                    seen_words.add(bold_italic_word)
                    break

        return self.bold_italic_text

    def __process_text_blocks(self, callback):
        for block in self.data:
            if block["type"] == pymupdf.PDF_ANNOT_TEXT:
                for line in block["lines"]:
                    for span in line["spans"]:
                        callback(span)

    def __get_all_last_words_in_block(self) -> list[tuple]:
        """Get all words that contains a point at the end of a line to know when a paragraph finish
        
        Returns:
            A list with format [(x0, y0, x1, y1, word, block_no, line_no, word_no)]"""
        # Find all the words that are at the end of the line with a ".",
        # save it as (word_index, word)

        if self.page is None or self.words is None:
            raise ValueError("Page is not setup. Call setup_page first.")

        last_words_block = [
            (len(line.split()) - 1, line.split()[-2], line.split()[-1])
            for line in self.page.get_text("text").split("\n")
            if line.endswith(".") and len(line.split()) > 1
        ]

        # Find in our last_words_block its index about where you can find the word it in the pdf
        l = []
        for i, word in enumerate(self.words):
            word_number = word[-1]
            previous_word = self.words[i-1][4]
            current_word = word[4]
            # We save also the previous word because you can find multiple times the same word.
            # saving its previous word is less likely to find the repeated word
            w = (word_number, previous_word, current_word)
            if w in last_words_block:
                l.append(word)
        return l

    def __get_indices_for_all_last_words_block(
            self,
            words: list[tuple],
            last_words_block: list[tuple]
        ) -> set[int]:
        """Get the indices for each word that marks when a paragraph finish
        
        Returns:
            A set of indices, these indices
        """
        last_words_seen = set()
        i, j = 0, 0

        # Let's find the indices where the word doesn't belong to its current paragrahp.
        while i < len(words):
            is_header = "\n" in words[i][4] or "\n" in words[i - 1][4]

            # Current word is in its paragraph
            if j < len(last_words_block) and words[i][3] <= last_words_block[j][3]:
                i += 1
                continue
            # Word is in another paragraph now
            if not is_header and j < len(last_words_block):
                last_words_seen.add(i-1)
                j += 1

            i += 1
        return last_words_seen

    def __sort_text(self, words: list[tuple]) -> list[tuple]:
        """Sort based on X position every single line of the words
            to make sure the order is correct
        """
        final_text = []
        current_line: list[tuple] = []
        previous_y = None

        # Sort completelly the words
        for word in words:
            word_y = word[3]

            # Entering the if it means we are in a new line.
            if previous_y is None or abs(word_y - previous_y) > self.VERTICAL_THRESHOLD:
                if current_line:
                    # Sort by x to preserve the order from left to right
                    current_line.sort(key=lambda w: w[0])
                    final_text.extend(current_line)
                    current_line = []

            previous_y = word_y
            current_line.append(word)

        # Add the last line
        if current_line:
            current_line.sort(key=lambda w: w[0])
            final_text.extend(current_line)

        return final_text

    def __format_text(self, words: list[tuple]) -> list[str]:
        """Format the highlighted text as faithfully as possible like you can find it on the PDF
        
        Args:
            words: Tuple with information [(x0,y0, x1,y1, "text", block_no, line_no, word_no)]

        Returns:
            List of string where each element is a line
        """
        final_text = []

        last_words_block = self.__get_all_last_words_in_block()
        words = self.__sort_text(words)
        last_words_seen = self.__get_indices_for_all_last_words_block(words, last_words_block)

        current_line: list[tuple] = []

        previous_y = None
        for i, word in enumerate(words):
            word_y = word[3]

            # Entering the if it means we are in a new line.
            if previous_y is None or abs(word_y - previous_y) > self.VERTICAL_THRESHOLD:
                if current_line:
                    temp_string = " ".join(e[4] for e in current_line)

                    # Just add a blank space when the text is continuous
                    if temp_string[-1] != "\n":
                        temp_string = temp_string + " "

                    # There are some incorrect words with the "\n\n" on the left, remove "\n\n"
                    if not any(temp_string.rstrip("\n") == header[4] for header in self.headers):
                        final_text.append(temp_string.replace("\n\n ", " "))
                    else:
                        final_text.append(temp_string)
                    current_line = []

            if i in last_words_seen:
                new_value = words[i][4] + "\n\n"
                word = word[:4] + (new_value,) + word[5:]

            previous_y = word_y
            current_line.append(word)

        # Add the last line
        if current_line:
            temp_string = " ".join(e[4] for e in current_line)
            # Just add a blank space when the text is continuous
            if temp_string[-1] != "\n":
                temp_string = temp_string + " "

            temp_string += "\n\n"
            # There are some incorrect words with the "\n\n" on the left, remove "\n\n"
            if not any(temp_string.rstrip("\n") == header[4] for header in self.headers):
                final_text.append(temp_string.replace("\n\n ", " "))
            else:
                final_text.append(temp_string)

            final_text.append(f"Page: {self.page_no + 1}")
            final_text.append("\n\n---\n\n")

        return final_text

    def __extract_highlight_text(self):
        self.highlight_words = []
        seen_words = set()

        if self.page is None or self.words is None:
            raise ValueError("Page is not setup. Call setup_page first.")

        for annot in self.page.annots(types=[pymupdf.PDF_ANNOT_HIGHLIGHT]):
            quad_coordinates = annot.vertices
            quad_count = len(quad_coordinates) // 4

            for i in range(quad_count):
                rect = pymupdf.Quad(quad_coordinates[i * 4 : i * 4 + 4]).rect
                rect = self.__adjust_rectangle(rect, 2.0)
                for word in self.words:
                    # Get (x0,y0), (x1,y1), word
                    word_key = word[:5]
                    if pymupdf.Rect(word[:4]).intersects(rect) and word_key not in seen_words:
                        self.highlight_words.append(word)
                        # Mark it as seen to avoid repeated words.
                        seen_words.add(word_key)

        # Sort by y and then x to preserve the word order.
        self.highlight_words.sort(key=lambda w: (w[3], w[0]))

    def __extract_headers(self) -> None:
        """
        Extract headers based on font size and position, merging text elements
        that belong to the same line into a single header.

        The function processes text spans, filters based on font size, and 
        merges headers that share similar Y positions.

        Returns:
            None. Updates self.headers with a list of tuples [(x0, y0, x1, y1, text)].
        """
        headers = []
        font_sizes = self.__get_common_font_size()
        threshold = self.__calculate_dynamic_threshold(font_sizes)

        def collect_headers(span):
            if span["size"] > threshold:
                header = (*span["bbox"], span["text"])
                headers.append(header)

        self.__process_text_blocks(collect_headers)
        # Sort by Y position
        # headers.sort(key=lambda h: h[3])

        # Maximum Y-position difference to merge headers when headers are broken
        # in multiple items
        threshold = 0.1
        if headers:
            current_header = headers[0]
            for header in headers[1:]:
                if abs(current_header[3] - header[3]) < threshold:
                    new_header = f"{current_header[4]} {header[4]}"
                    current_header = (*current_header[:4], new_header)
                else:
                    self.headers.append(current_header)
                    current_header = header
            # Append last header
            self.headers.append(current_header)
