import unittest

from unittest.mock import MagicMock, patch
from pdf import PDF

class TestPDF(unittest.TestCase):
    @patch("pymupdf.open")
    def setUp(self, mock_open):
        mock_document = MagicMock()
        mock_page = MagicMock()
        mock_open.return_value = mock_page

        self.page_annotation = 0

        self.pdf = PDF("mock_pdf.pdf")
        self.pdf.doc = mock_document
        self.pdf.page = mock_page
        self.pdf.setup_page(0)

    def test_get_headers_for_page_with_toc(self):
        self.pdf.doc.get_toc = MagicMock(return_value=[
            [1, '1 Introduction', 29],
            [2, '1.1 What Is an Algorithm?', 31],
            [3, 'Exercises 1.1', 35],
            [2, '1.2 Fundamentals of Algorithmic Problem Solving', 37],
            [3, 'Understanding the Problem', 37],
            [3, 'Ascertaining the Capabilities of the Computational Device', 37],
            [1, '2 Evolution', 45],
            [2, '2.1 What is evolution', 50],
            [3, 'Exercises 2.1', 52],
            [2, '2.2 More evolution', 60],
            [3, 'Importance ofevolution', 65]
        ])

        self.pdf.setup_page(52)
        self.pdf.headers = [
            (0, 20, 50, 30, 'Exercises 2.1')
        ]
        result = self.pdf.get_headers_for_page()
        self.assertEqual(result, [
            (1, '2 Evolution'),
            (2, '2.1 What is evolution'),
            (3, 'Exercises 2.1')
        ])

    def test_get_headers_for_page_with_same_level(self):
        self.pdf.doc.get_toc = MagicMock(return_value=[
            [1, '1 Introduction', 29],
            [2, '1.1 What Is an Algorithm?', 31],
            [3, 'Exercises 1.1', 35],
            [3, 'Ecercises 1.2', 35],
            [3, 'Understanding the Problem', 37],
            [3, 'Ascertaining the Capabilities of the Computational Device', 37]
        ])

        self.pdf.page_no = 37
        self.pdf.headers = [
            (0, 10, 20, 30, "Understanding the Problem"),
            (40, 50, 60, 70, "Ascertaining the Capabilities of the Computational Device"),
        ]
        result = self.pdf.get_headers_for_page()
        self.assertEqual(result, [
            (1, '1 Introduction'),
            (2, '1.1 What Is an Algorithm?'),
            (3, 'Understanding the Problem'),
            (3, 'Ascertaining the Capabilities of the Computational Device')
        ])
            
    def test_get_headers_for_page_with_no_toc(self):
        self.pdf.doc.get_toc = MagicMock(return_value = [])
        self.pdf.setup_page(0)
        result = self.pdf.get_headers_for_page()
        self.assertEqual(result, [])
    
    def test_get_headers_for_page_same_page_different_level(self):
        self.pdf.doc.get_toc = MagicMock(return_value=[
            [1, 'Cover', 1], [1, 'Copyright Page', 4], [1, 'Title Page', 5], [1, 'Brief Contents', 7], [1, 'Contents', 9],
            [1, 'New to the Third Edition', 19], [1, 'Preface', 21], [1, 'Acknowledgments', 26],
            [1, '1 Introduction', 29], [2, '1.1 What Is an Algorithm?', 31], [3, 'Exercises 1.1', 35],
            [2, '1.2 Fundamentals of Algorithmic Problem Solving', 37], [3, 'Understanding the Problem', 37],
            [3, 'Ascertaining the Capabilities of the Computational Device', 37],
            [3, 'Choosing between Exact and Approximate Problem Solving', 39],
            [3, 'Algorithm Design Techniques', 39], [3, 'Designing an Algorithm and Data Structures', 40],
            [3, 'Methods of Specifying an Algorithm', 40], [3, 'Proving an Algorithm’s Correctness', 41],
            [3, 'Analyzing an Algorithm', 42], [3, 'Coding an Algorithm', 43], [3, 'Exercises 1.2', 45],
            [2, '1.3 Important Problem Types', 46], [3, 'Sorting', 47], [3, 'Searching', 48],
            [3, 'String Processing', 48], [3, 'Graph Problems', 49], [3, 'Combinatorial Problems', 49],
            [3, 'Geometric Problems', 50], [3, 'Numerical Problems', 50], [3, 'Exercises 1.3', 51],
            [2, '1.4 Fundamental Data Structures', 53], [3, 'Linear Data Structures', 53], [3, 'Graphs', 56],
            [3, 'Trees', 59], [3, 'Sets and Dictionaries', 63], [3, 'Exercises 1.4', 65], [3, 'Summary', 66],
            [1, '2 Fundamentals of the Analysis of Algorithm Efficiency', 69],
            [2, '2.1 The Analysis Framework', 70], [3, '\t', 71],
            [3, 'Units for Measuring Running Time', 72], [3, 'Orders of Growth', 73],
            [3, 'Worst-Case, Best-Case, and Average-Case Efficiencies', 75],
            [3, 'Recapitulation of the Analysis Framework', 78], [3, 'Exercises 2.1', 78],
            [2, '2.2 Asymptotic Notations and Basic Efficiency Classes', 80],
            [3, 'Informal Introduction', 80]
        ])
        self.pdf.page_no = 79
        self.pdf.headers = [(85.30199432373047, 338.47564697265625, 108.55281066894531, 352.42333984375, '2.2 Asymptotic Notations and Basic Efﬁciency Classes'),
                            (120.50799560546875, 506.0413818359375, 242.0565185546875, 517.99658203125, 'Informal Introduction')]

        result = self.pdf.get_headers_for_page()
        expected = [
            (1, "2 Fundamentals of the Analysis of Algorithm Efficiency"),
            (2, "2.2 Asymptotic Notations and Basic Efficiency Classes"),
            (3, "Informal Introduction")
        ]
        self.assertEqual(result, expected)

    def test_get_headers_for_page_02(self):
        self.pdf.doc.get_toc = MagicMock(return_value=[
            [1, '1 Introduction', 29],
            [2, '1.1 What Is an Algorithm?', 31],
            [3, 'Exercises 1.1', 35],
            [1, '2 fundamentals of the analysis of algorithm efficiency', 75],
            [2, '2.2 Asymptotic Notations and Basic Efficiency Classes', 67],
            [3, 'O-notation', 81]
        ])
        self.pdf.page_no = 80
        self.pdf.headers = [
            (120.50679779052734,323.791259765625,
             129.97531127929688, 335.7464599609375,
             'O-notation')
        ]

        result = self.pdf.get_headers_for_page()
        expected = [
            (1, '2 fundamentals of the analysis of algorithm efficiency'),
            (2, '2.2 Asymptotic Notations and Basic Efficiency Classes'),
            (3, 'O-notation'),
        ]
        self.assertEqual(result, expected)

    def test_get_headers_for_page_with_dummy_header(self):
        """This means there are no headers in the page"""
        self.pdf.doc.get_toc = MagicMock(return_value=[
            [1, '1 Introduction', 29],
            [2, '1.1 What Is an Algorithm?', 31],
            [3, 'Exercises 1.1', 35],
            [1, '2 fundamentals of the analysis of algorithm efficiency', 75],
            [2, '2.2 Asymptotic Notations and Basic Efficiency Classes', 67],
            [3, 'O-notation', 81]
        ])
        self.pdf.page_no = 90
        self.pdf.headers = []

        result = self.pdf.get_headers_for_page()
        expected = [
            (1, '2 fundamentals of the analysis of algorithm efficiency'),
            (2, '2.2 Asymptotic Notations and Basic Efficiency Classes'),
            (3, 'O-notation'),
        ]
        self.assertEqual(result, expected)


    ###################################################

    def run__extract_headers_test(self, text_spans, expected_headers):
        with patch.object(PDF, "_PDF__get_common_font_size", return_value=[10, 12, 14, 16, 18]) as mock_get_common_font_size, \
            patch.object(PDF, "_PDF__calculate_dynamic_threshold", return_value=14) as mock_calculate_dynamic_threshold, \
            patch.object(PDF, "_PDF__process_text_blocks") as mock_process_text_blocks:
        
            mock_process_text_blocks.side_effect = lambda callback: [callback(span) for span in text_spans]
            self.pdf._PDF__extract_headers()
            self.assertEqual(self.pdf.headers, expected_headers)

    def test__extract_headers(self,):
        text_spans = [
            {"bbox": (0, 0, 50, 10), "size": 15, "text": "Header1"},
            {"bbox": (0, 10, 50, 20), "size": 16, "text": "Subheader1"},
            {"bbox": (0, 20, 50, 30), "size": 15, "text": "Header2"},
            {"bbox": (0, 25, 50, 35), "size": 12, "text": "Content"},
            {"bbox": (0, 30, 50, 40), "size": 16, "text": "Subheader2"},
            {"bbox": (0, 31, 50, 41), "size": 16, "text": "Subheader3"}
        ]

        expected_headers = [
            (0, 0, 50, 10, 'Header1'),
            (0, 10, 50, 20, 'Subheader1'),
            (0, 20, 50, 30, 'Header2'),
            (0, 30, 50, 40, 'Subheader2'),
            (0, 31, 50, 41, "Subheader3")
        ]
        self.run__extract_headers_test(text_spans, expected_headers)

    def test__extract_headers_one_main_header_one_sub_header(self):
        text_spans = [
            {"bbox": (0, 0, 50, 10), "size": 18, "text": "Header1"},
            {"bbox": (0, 10, 50, 20), "size": 16, "text": "Subheader1"},
        ]

        expected_headers = [
            (0, 0, 50, 10, 'Header1'),
            (0, 10, 50, 20, 'Subheader1')
        ]

        self.run__extract_headers_test(text_spans, expected_headers)

    def test__extract_headers_one_sub_header_one_main_header(self):
        text_spans = [
            {"bbox": (0, 10, 50, 10), "size": 16, "text": "Subheader1"},
            {"bbox": (0, 0, 50, 20), "size": 18, "text": "Header1"},
        ]

        expected_headers = [
            (0, 10, 50, 10, 'Subheader1'),
            (0, 0, 50, 20, 'Header1')
        ]

        self.run__extract_headers_test(text_spans, expected_headers)

    def test__extract_headers_separated(self):
        text_spans = [
            {"bbox": (0, 0, 50, 10.3123), "size": 16, "text": "- "},
            {"bbox": (0, 10, 50, 10.3223), "size": 16, "text": "Main header"},
            {"bbox": (0, 10, 50, 14), "size": 15, "text": "Sub header"},
        ]

        expected_headers = [
            (0, 0, 50, 10.3123, "-  Main header"),
            (0, 10, 50, 14, "Sub header")
        ]

        self.run__extract_headers_test(text_spans, expected_headers)

    def test__extract_headers_separated_02(self):
        text_spans = [
            {"bbox": (0, 0, 50, 335.7464599609375), "size": 16, "text": "O"},
            {"bbox": (0, 10, 50, 335.7285461425781), "size": 16, "text": '-notation'}
        ]

        expected_headers = [
            (0, 0, 50, 335.7464599609375, "O -notation")
        ]

        self.run__extract_headers_test(text_spans, expected_headers)
    
    def test__extract_headers_no_headers(self):
        self.run__extract_headers_test([], [])

    ###################################################

    def test__process_text_block_valid(self):
        data_valid = [
            {"type": self.page_annotation,
             "lines": [{"spans": [{"text": "Span1"}, {"text": "Span2"}]}]},
            {"type": self.page_annotation, 
             "lines": [{"spans": [{"text": "Span3"}]}]},
        ]

        self.pdf.data = data_valid
        mock_callback = MagicMock()
        self.pdf._PDF__process_text_blocks(mock_callback)

        # 2 spans + 1 span
        self.assertEqual(mock_callback.call_count, 3)
        mock_callback.assert_any_call({"text": "Span1"})
        mock_callback.assert_any_call({"text": "Span2"})
        mock_callback.assert_any_call({"text": "Span3"})
    
    def test__proccess_text_block_invalid(self):
        self.pdf.data = [
            {"type": "other_type", 
             "lines": [{"spans": [{"text": "Invalid"}]}]}
        ]

        mock_callback = MagicMock()
        self.pdf._PDF__process_text_blocks(mock_callback)
        mock_callback.assert_not_called()

    def test__proccess_text_block_empty(self):
        self.pdf.data = []
        mock_callback = MagicMock()
        self.pdf._PDF__process_text_blocks(mock_callback)
        mock_callback.assert_not_called()

    ###################################################

    def run__extract_bold_italic_text(self, text_spans, expected):
        with patch.object(PDF, "_PDF__extract_highlight_text") as mock_extract_highlight_text, \
            patch.object(PDF, "_PDF__process_text_blocks") as mock_process_text_blocks:

            # Mock process_text_blocks to simulate spans
            def process_callback(callback):
                for span in text_spans:
                    callback(span)
            mock_process_text_blocks.side_effect = process_callback

            result = self.pdf._PDF__extract_bold_italic_text()
            self.assertEqual(result, expected)
            mock_process_text_blocks.assert_called_once()
            # Because highlight text is already set
            mock_extract_highlight_text.assert_not_called()

    def test__extract_bold_italic_text_valid(self):
        spans = [
            {"font": "BoldFont", "bbox": (0,0,10,10), "text": "BoldText"},
            {"font": "ItalicFont", "bbox": (15,15,25,25), "text": "ItalicText"},
            {"font": "RegularFont", "bbox": (30,30,40,40), "text": "RegularText"},
            {"font": "BoldItalicFont", "bbox": (50,50,60,60), "text": "BoldItalicText"}
        ]

        self.pdf.highlight_words = [
            (0,0,10,10, "BoldText"),
            (12,12,14,14, "RegularText"),
            (15,15,25,25, "ItalicText"),
            (50,50,60,60, "BoldItalicText")
        ]
        
        expected = [
            (0,0,10,10, "BoldText"),
            (15,15,25,25, "ItalicText"),
            (50,50,60,60, "BoldItalicText")
        ]
        
        self.run__extract_bold_italic_text(spans, expected)

    def test__extract_bold_italic_text_no_bold_italic(self):
        spans = [
            {"font": "BoldFont", "bbox": (0,0,10,10), "text": "BoldText"},
            {"font": "ItalicFont", "bbox": (15,15,25,25), "text": "ItalicText"},
            {"font": "RegularFont", "bbox": (30,30,40,40), "text": "RegularText"},
            {"font": "BoldItalicFont", "bbox": (50,50,60,60), "text": "BoldItalicText"}
        ]

        self.pdf.highlight_words = [
            (80,80,100,100, "RegularText01"),
            (120,120,130,130, "RegularText02"),
            (150,150,170,170, "RegularText03"),
        ]
        
        expected = []
        self.run__extract_bold_italic_text(spans, expected)
    
    def test__extract_bold_italic_text_no_headers(self):
        with patch.object(PDF, "_PDF__extract_highlight_text") as mock_extract_highlight_text, \
            patch.object(PDF, "_PDF__process_text_blocks") as mock_process_text_blocks:

            spans = [
                {"font": "BoldFont", "bbox": (0,0,10,10), "text": "BoldText"},
                {"font": "ItalicFont", "bbox": (15,15,25,25), "text": "ItalicText"},
                {"font": "RegularFont", "bbox": (30,30,40,40), "text": "RegularText"},
                {"font": "BoldItalicFont", "bbox": (50,50,60,60), "text": "BoldItalicText"}
            ]

            # Mock process_text_blocks to simulate spans
            def process_callback(callback):
                for span in spans:
                    callback(span)
            mock_process_text_blocks.side_effect = process_callback

            self.pdf.highlight_words = []
            self.pdf._PDF__extract_bold_italic_text()
            mock_process_text_blocks.assert_called_once()
            mock_extract_highlight_text.assert_called_once()

    ###################################################

    @patch.object(PDF, "_PDF__extract_headers")
    @patch.object(PDF, "_PDF__format_text")
    def test_get_headers(self, mock_format_text, mock_extract_headers):
        self.pdf.headers = ["Header 1", "Header 2", "Header 3"]
        mock_format_text.return_value = ["Formatted Header 1", "Formatted Header 2", "Formatted Header 3"]

        result = self.pdf.get_headers()
        expected = ["Formatted Header 1", "Formatted Header 2", "Formatted Header 3"]

        mock_extract_headers.assert_called_once()
        mock_format_text.assert_called_once()

        self.assertEqual(result, expected)

    ###################################################

    @patch.object(PDF, "_PDF__extract_bold_italic_text", return_value=None)
    def test_get_bol_italic_text_valid(self, mock_extract_bold_italic_text):
        self.pdf.bold_italic_text = [
            (0, 0, 10, 10, "BoldText"),
            (15, 15, 25, 25, "ItalicText"),
            (30, 30, 40, 40, "BoldItalicText")
        ]

        expected = ["BoldText", "ItalicText", "BoldItalicText"]
        result = self.pdf.get_bold_italic_text()

        mock_extract_bold_italic_text.assert_called_once()
        self.assertEqual(result, expected)

    def test_get_bol_italic_text_empty(self):
        self.pdf.bold_italic_text = []
        expected = []
        result = self.pdf.get_bold_italic_text()
        self.assertEqual([], [])

if __name__ == "__main__":
    unittest.main()