from unittest import TestCase

from bs4 import BeautifulSoup
from bs4.element import Tag

from faint.bbcode import to_bbcode

def wrap(html: str) -> Tag:
    return BeautifulSoup(f'<div>{html}</div>', 'lxml').contents[0]

class TestConvert(TestCase):
    def assert_wrapped(self, bbcode: str, html: str, msg: str):
        self.assertEqual(bbcode, to_bbcode(wrap(html)), msg)
    
    def test_tagB(self):
        self.assert_wrapped('[b]bold[/b]', '<strong class="bbcode bbcode_b">bold</strong>', 'Bold tag fails to format correctly')
    
    def test_tagI(self):
        self.assert_wrapped('[i]italics[/i]', '<i class="bbcode bbcode_i">italics</i>', 'Italics tag fails to format correctly')
    
    def test_tagU(self):
        self.assert_wrapped('[u]underline[/i]', '<u class="bbcode bbcode_u">underline</u>', 'Underline tag fails to format correctly')
    
    def test_tagS(self):
        self.assert_wrapped('[s]strikethrough[/s]', '<s class="bbcode bbcode_s">strikethrough</s>', 'Strikethrough tag fails to format correctly')
    
    def test_tagSup(self):
        self.assert_wrapped('[sup]superscript[/sup]', '<sup class="bbcode bbcode_sup">superscript</sup>', 'Superscript tag fails to format correctly')
    
    def test_tagSub(self):
        self.assert_wrapped('[sub]subscript[/sub]', '<sub class="bbcode bbcode_sub">subscript</sub>', 'Subscript tag fails to format correctly')