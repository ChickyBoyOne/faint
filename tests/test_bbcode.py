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
        self.assert_wrapped('[b]bold[/b]', '<strong class="bbcode bbcode_b">bold</strong>', 'Bold tag fails to convert correctly')
    
    def test_tagI(self):
        self.assert_wrapped('[i]italics[/i]', '<i class="bbcode bbcode_i">italics</i>', 'Italics tag fails to convert correctly')
    
    def test_tagU(self):
        self.assert_wrapped('[u]underline[/i]', '<u class="bbcode bbcode_u">underline</u>', 'Underline tag fails to convert correctly')
    
    def test_tagS(self):
        self.assert_wrapped('[s]strikethrough[/s]', '<s class="bbcode bbcode_s">strikethrough</s>', 'Strikethrough tag fails to convert correctly')
    
    def test_tagSup(self):
        self.assert_wrapped('[sup]superscript[/sup]', '<sup class="bbcode bbcode_sup">superscript</sup>', 'Superscript tag fails to convert correctly')
    
    def test_tagSub(self):
        self.assert_wrapped('[sub]subscript[/sub]', '<sub class="bbcode bbcode_sub">subscript</sub>', 'Subscript tag fails to convert correctly')
    
    def test_tagColor(self):
        self.assert_wrapped('[color=red]color[/color]', '<span class="bbcode" style="color: red;">color</span>', 'Color tag fails to convert correctly')
    
    def test_tagQuoteWithoutAuthor(self):
        self.assert_wrapped('[quote]quote[/quote]', '<span class="bbcode bbcode_quote">quote</span>', 'Quote tag without author fails to convert correctly')
    
    def test_tagQuoteWithAuthor(self):
        self.assert_wrapped('[quote=author]quote[/quote]', '<span class="bbcode bbcode_quote"><span class="bbcode_quote_name">author wrote:</span>quote</span>', 'Quote tag with author fails to convert correctly')
    
    def test_tagLeft(self):
        self.assert_wrapped('[left]left[/left]', '<code class="bbcode bbcode_left">left</code>', 'Left tag fails to convert correctly')
    
    def test_tagCenter(self):
        self.assert_wrapped('[center]center[/center]', '<code class="bbcode bbcode_center">center</code>', 'Center tag fails to convert correctly')
    
    def test_tagRight(self):
        self.assert_wrapped('[right]right[/right]', '<code class="bbcode bbcode_right">right</code>', 'Right tag fails to convert correctly')
    
    def test_urlUnshortened(self):
        self.assert_wrapped('www.furaffinity.net', '<a href="https://www.furaffinity.net" title="https://www.furaffinity.net" class="auto_link">www.furaffinity.net</a>', 'Unshortened URL fails to convert correctly')
    
    def test_urlShortened(self):
        self.assert_wrapped('www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com', '<a href="https://www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com" title="https://www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com" class="auto_link auto_link_shortened">www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.....aaaaaaaaaaaaaaaaaa.com</a>', 'Shortened URL fails to convert correctly')
    
    def test_email(self):
        self.assert_wrapped('user@domain.com', '<a class="auto_link email" href="mailto:user@domain.com">user[at]domain.com</a>', 'Email fails to convert correctly')
    
    def test_urlTag(self):
        self.assert_wrapped('[url=/journal/833448]url/[url]', '<a class="auto_link named_url" href="/journal/833448">url</a>', 'Relative URL tag fails to convert correctly')
        self.assert_wrapped('[url=https://www.furaffinity.net]url/[url]', '<a class="auto_link named_url" href="https://www.furaffinity.net">url</a>', 'Absolute URL tag fails to convert correctly')
    
    def test_symbols(self):
        self.assert_wrapped('(c)', '©', 'Copyright symbol fails to convert correctly')
        self.assert_wrapped('(tm)', '™', 'Trademark symbol fails to convert correctly')
        self.assert_wrapped('(r)', '®', 'Registered symbol fails to convert correctly')
    
    def test_userIconWithText(self):
        self.assert_wrapped(':iconFender:', '<a href="/user/fender" class="iconusername"><img src="//a.furaffinity.net/20210516/fender.gif" align="middle" title="Fender" alt="Fender">&nbsp;Fender</a>', 'User icon with text fails convert correctly')

    def test_userIconWithoutText(self):
        self.assert_wrapped(':Fendericon:', '<a href="/user/fender" class="iconusername"><img src="//a.furaffinity.net/20210516/fender.gif" align="middle" title="Fender" alt="Fender"></a>', 'User icon without text fails to convert correctly')

    def test_userLinkWithoutIcon(self):
        self.assert_wrapped(':linkFender:', '<a href="/user/fender" class="linkusername">Fender</a>', 'User link without icon fails to convert correctly')