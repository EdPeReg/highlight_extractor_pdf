
# Notes

- Somehow if we have something like this `My text\n\n\n`, the method `rstrip()` was causing issues removing the `\n`, introducing a subtle bug where the last header didn't have the correct amount of `\n`
- There could be some cases where there is a new paragraph when there isn't, like for example in the same paragraph at the end of the line there is a word with a dot, all text next to that word will be in a new paragraph.
- If we want to detect headers that have the same size but they are bold and have a words threshold, it partially works, for example:

`if span["size"] > threshold or "bold" in font and len(font.split()) < self.WORDS_THRESHOLD:`

This works but if the paragraph has this situation where we have the next text, the phrase **IT’S POSSIBLE FOR** will be taken as a header:

> **IT’S POSSIBLE FOR** a person to have an overwhelming number of things to do and still function productively with a clear head and a positive sense of relaxed control. That’s a great way to live and work, at elevated levels of...



# TODO

- [x] Get headers
- [x] Get highlight text
- [x] Give format to the text
- [x] Put the highlighted text to the corresponding title if applies.
- [x] There are some lines there are shown with only a few words, like 1 or 2 words, it looks ugly.
- [x] There are sometimes that a line enters an extra line and it is in the same paragraph
- [] Maybe an improvemenet can be done when formatting the entire text for `get entire text()`, instead of checking all the words, just check the firstword of the parabraph and assume all words after the first word, belongs to the paragraph, in that way we avoid analazing all words that are in the same Y
- [] Maybe the functions `__format_text()` and `get_entire_text()` can be one function
- [x] It would be nice to have also the main headings and subheadings.
- [] Check how to format the headers correctly, should I format the headers since the beggining? or afterwards?
- [x] To get when the words are bold, italic and so on, format them, curretnly is only plain text.
- [] It only appends, if I get the page 42 and then 41, the md file will have the incorrect order, should be first 41 and then 42
- [x] It would be great if I can do it within a range of pages instead going for each page manually
- [x] Convert ~ to the corresponding value in the file path

# TODO TEST

- [x] TEST: Highlighted text match
- [x] TEST: What if the header text I don't have any remarcado? Does the header is displayed?
- [x] TEST: When header is at the beggining.
- [x] TEST: When header is not at the beggining.
- [x] TEST: When a last header doesn't have highlight text, it shouldn't be printed, you can use From book.pdf page 53, the header Example 1.11 should not be printed because.
- [x] TEST: 1 Encabezado principal y un sub Encabezado, page 79 book2.pdf
- [x] TEST: un sub encabezado solo, page 72 book2.pdf
- [x] TEST: varios sub encabezados solos , book2.pdf page 49
- [x] TEST: 1 encabezado principal nada mas, page 69 book2.pdf
- [x] TEST: 1 subencabezado y un encabezado principal page 46 book.pdf
- [x] Test for `get_headers_for_page_with_toc()`
- [x] Test for `__extract_headers()`
- [x] Test for `__process_text_blocks()`
- [x] Test for `__extract_bold_italic_text()`

# TODO BUGS

- [x] BUG: For book3.pdf page 31, there is no header but it returns ["I"], it is because the top there
 is a red line that in reality is a I, it doesn't always happen. Fixed by checking the text is inside its header range.
- [x] BUG: For page 41 for book2 the first word from the highlight text is not shown.
- [x] BUG: There are some headers that have extra space between the header and its paragraph, book2.pdf page 49
- [x] BUG: Page 39 book2.pdf, the first sentence is all pegado.
- [x] BUG: Page 39 book2.pdf, if the higlight text is almost at the end of the paragraph, the Y and X distace thinks it is a new paragraph and puts the text in a new paragraph.
- [] BUG: Page 39 book2.pdf, you can find "poly- gons" instead of "polygons"
- [x] BUG: Page 38 book.pdf, if there is no point in a word, it is printed incorrectly
- [x] BUG: Following the dot approach for paragraphs, text is not formatted correctly when there is not a dot.
- [x] BUG: Some words, specially bold words were not sorted correctly, solved. 
- [x] BUG: Book3.pdf page42, the title doesn't appear.
- [x] BUG: Book3.pdf page 37 text is not formatted correctly.
- [x] BUG: Book2.pdf page 41 text is not formatted correctly.
- [x] BUG: Book3.pdf page42, last text is not formatted correctly.
- [] BUG: Book2.pdf page 52, the first line is not formatted correctly because there are multiple lines with dot above the hgihlight text.
- [] BUG: Book2.pdf page 68 Main header is not formatted correctly
- [] BUG: The .md file is not created in the corresponding workspace folder

# References

- Copilot
- ChatGPT
- [Extract highlighted text](https://github.com/pymupdf/PyMuPDF/issues/318) 
- [Pymupdf documentation](https://pymupdf.readthedocs.io/en/latest/index.html)
- [Highlight words example](https://github.com/jdipper/studyhelpers/blob/main/hextract.py)
- [Textbox extraction](https://github.com/pymupdf/PyMuPDF-Utilities/tree/master/textbox-extraction)
- [Get highlighted portion](https://github.com/pymupdf/PyMuPDF/discussions/2381)
- [PDF tools](https://github.com/pastydev/cmdict/blob/88e6f19d1fd5ea4bdd87b0b06a9d3230ce1eac94/src/cmdict/pdf_tools.py#L20)
- [How to decode pdf stream](https://stackoverflow.com/questions/27997930/how-to-decode-a-pdf-stream)
- [Data extraction from pf](https://stackoverflow.com/questions/27997930/how-to-decode-a-pdf-stream)
- [Why identifying paragraph is very hard](https://github.com/pymupdf/PyMuPDF/discussions/3133)