import unittest
from skimage import io
import context
from pyamiimage.ami_ocr import TextBox, AmiOCR
from pyamiimage.ami_ocr import TextBox, AmiOCR
from resources import Resources # Asserting all images take time

Interactive = False
class TestTextBox:
    def setup_method(self, method):
        self.textbox = TextBox('hello world', [[10, 50], [40, 50]])

    def teardown_method(self, method):
        self.textbox = None

    def test_get_text(self):
        assert self.textbox.text == 'hello world'

    def test_set_text(self):
        self.textbox.set_text("hello peter")
        assert self.textbox.text == "hello peter" 

    def test_get_ranges(self):
        assert self.textbox.bbox.get_ranges() == [[10, 50], [40, 50]]

    def plot_bbox():
        pass

class TestAmiOCR:
    def setup_method(self, method):
        self.biosynth2 = Resources.BIOSYNTH2_RAW
        self.biosynth2_img = io.imread(self.biosynth2)
        self.biosynth2_ocr = AmiOCR(self.biosynth2)

    def teardown_method(self, method):
        self.biosynth2 = None
        self.img_ocr = None

    def test_words(self):
        words = self.biosynth2_ocr.get_words()
        # clean unbalanced quotes out of output
        words = AmiOCR.clean_all(words)
        assert len(words) == 56, f"words are {len(words)}"
        expected_textbox = TextBox("Glycolysis", [[405, 638], [1, 57]])
        assert words[0] == expected_textbox, f"{expected_textbox} and found: {words[0]}"
        # assert words[0:3] == [TextBox("Glycolysis", [[405, 638], [1, 57]]),
        #                      TextBox("Terpene", [[182, 349], [57, 99]]),
        #                      TextBox("Biosynthetic", [[140, 390], [111, 145]]),
        #                      # TextBox("Bethea", [[178, 329], [122, 200]]),
        #                      # TextBox("Acetyl-Co", [[606, 798], [149, 187]])], \
        #                      ], f"words and bounds are {words[0:3]}"
        assert words[0] == expected_textbox, f"{expected_textbox} and found: {words[0]}"
        print(f"temp {words[0:5]}")
        assert words[0:5] ==[TextBox("Glycolysis", [[405, 638], [1, 57]]),
                             TextBox("Terpene", [[182, 349], [53, 103]]),
                             TextBox("Biosynthetic", [[140, 390], [111, 145]]),
                             TextBox("Bethea", [[178, 329], [122, 200]]),
                             TextBox("Acetyl-Co", [[606, 798], [149, 187]])], f"words and bounds are {words[:5]}"
        """E       assert [Textbox(Glycolysis, [[405, 638], [1, 57]]),\n Textbox(Terpene, [[182, 349], [53, 103]]),\n Textbox(Biosynthetic, [[140, 390], [111, 145]]),\n Textbox(Bethea, [[178, 329], [122, 200]]),\n Textbox(Acetyl-Co, [[606, 798], [149, 187]])] ==
                          [Textbox(Glycolysis, [[405, 638], [1, 57]]),\n Textbox(Terpene, [[182, 349], [57, 99]]),\n Textbox(Biosynthetic, [[140, 390], [111, 145]]),\n Textbox(Bethea, [[178, 329], [122, 200]]),\n Textbox(Acetyl-Co, [[606, 798], [149, 187]])]
"""

    def test_phrases(self):
        phrases = self.biosynth2_ocr.get_phrases()
        assert len(phrases) == 59, f"phrases are {len(phrases)}"

    def test_groups(self):
        groups = self.biosynth2_ocr.get_groups()
        assert len(groups) == 59, f"groups are {len(groups)}"

    def test_clean(self):
        pass

    @unittest.skipUnless(Interactive, "interactive" )
    def test_plot_bbox_on_image(self):
        words = self.biosynth2_ocr.get_words()
        biosynth2_img_bboxes = AmiOCR.plot_bboxes_on_image(self.biosynth2_img, words)
        if self.interactive:
            io.imshow(biosynth2_img_bboxes)
            io.show()

