from unittest import TestCase

from bs4.element import Tag

from faint.scraper.spiders.bbcode import BBCodeLocation, to_bbcode
from faint.scraper.spiders.utils import get_soup

def wrap(html: str) -> Tag:
    return get_soup(f'<div>{html}</div>')

class BBCodeTestCase(TestCase):
    def assert_wrapped(self, bbcode: str, html: str, element: str, plural: bool = False,
            location: BBCodeLocation = BBCodeLocation.JOURNAL):
        self.assertEqual(
            bbcode,
            to_bbcode(wrap(html), location),
            f'{element} fail{"s" if not plural else ""} to convert correctly',
        )

class ConvertTagsTest(BBCodeTestCase):
    def test_b(self):
        self.assert_wrapped(
            '[b]bold[/b]',
            '<strong class="bbcode bbcode_b">bold</strong>',
            'Bold tag',
        )
    
    def test_i(self):
        self.assert_wrapped(
            '[i]italics[/i]',
            '<i class="bbcode bbcode_i">italics</i>',
            'Italics tag',
        )
    
    def test_u(self):
        self.assert_wrapped(
            '[u]underline[/u]',
            '<u class="bbcode bbcode_u">underline</u>',
            'Underline tag',
        )
    
    def test_s(self):
        self.assert_wrapped(
            '[s]strikethrough[/s]',
            '<s class="bbcode bbcode_s">strikethrough</s>',
            'Strikethrough tag',
        )
    
    def test_sup(self):
        self.assert_wrapped(
            '[sup]superscript[/sup]',
            '<sup class="bbcode bbcode_sup">superscript</sup>',
            'Superscript tag',
        )
    
    def test_sub(self):
        self.assert_wrapped(
            '[sub]subscript[/sub]',
            '<sub class="bbcode bbcode_sub">subscript</sub>',
            'Subscript tag',
        )
    
    def test_color(self):
        self.assert_wrapped(
            '[color=red]color[/color]',
            '<span class="bbcode" style="color: red;">color</span>',
            'Color tag',
        )
    
    def test_quoteWithoutAuthor(self):
        self.assert_wrapped(
            '[quote]quote[/quote]',
            '<span class="bbcode bbcode_quote">quote</span>',
            'Quote tag without author',
        )
    
    def test_quoteWithAuthor(self):
        self.assert_wrapped(
            '[quote=author]quote[/quote]',
            '<span class="bbcode bbcode_quote"><span class="bbcode_quote_name">author wrote:</span>quote</span>',
            'Quote tag with author',
        )
    
    def test_left(self):
        self.assert_wrapped(
            '[left]left[/left]',
            '<code class="bbcode bbcode_left">left</code>',
            'Left tag',
        )
    
    def test_center(self):
        self.assert_wrapped(
            '[center]center[/center]',
            '<code class="bbcode bbcode_center">center</code>',
            'Center tag',
        )
    
    def test_right(self):
        self.assert_wrapped(
            '[right]right[/right]',
            '<code class="bbcode bbcode_right">right</code>',
            'Right tag',
        )
    
    def test_url(self):
        self.assert_wrapped(
            '[url=/journal/833448]url[/url]',
            '<a class="auto_link named_url" href="/journal/833448">url</a>',
            'Relative URL tag',
        )
        self.assert_wrapped(
            '[url=https://www.furaffinity.net]url[/url]',
            '<a class="auto_link named_url" href="https://www.furaffinity.net">url</a>',
            'Absolute URL tag',
        )
    
    def test_nesting(self):
        self.assert_wrapped(
            '[b]bold [i]italics[/i][/b]',
            '<strong class="bbcode bbcode_b">bold <i class="bbcode bbcode_i">italics</i></strong>',
            'Nested tags',
            plural=True,
        )

class ConvertTextTest(BBCodeTestCase):
    def test_newline(self):
        self.assert_wrapped(
            'one \ntwo\nthree',
            '\none <br>\ntwo<br>\nthree',
            'Newline',
        )
    
    def test_locations(self):
        self.assert_wrapped(
            'profile',
            '\n                profile            ',
            'BBCode with profile padding',
            location=BBCodeLocation.PROFILE,
        )
        self.assert_wrapped(
            'profile journal',
            '\n                \n                profile journal\n                            ',
            'BBCode with profile journal padding',
            location=BBCodeLocation.PROFILE_JOURNAL,
        )
        self.assert_wrapped(
            'comment',
            '\n            comment        ',
            'BBCode with comment padding',
            location=BBCodeLocation.COMMENT,
        )
        self.assert_wrapped(
            'submission',
            '\n                    submission\n                                    ',
            'BBCode with submission padding',
            location=BBCodeLocation.SUBMISSION,
        )
        self.assert_wrapped(
            'journal',
            'journal',
            'BBCode with journal padding',
            location=BBCodeLocation.JOURNAL,
        )

    def test_horizontalLine(self):
        self.assert_wrapped(
            '-----',
            '<hr class="bbcode bbcode_hr">',
            'Horizontal line',
        )

    def test_urlUnshortened(self):
        self.assert_wrapped(
            'www.furaffinity.net',
            '<a href="https://www.furaffinity.net" title="https://www.furaffinity.net" class="auto_link">www.furaffinity.net</a>',
            'Unshortened URL',
        )
    
    def test_urlShortened(self):
        self.assert_wrapped(
            'www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com',
            '<a href="https://www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com" title="https://www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com" class="auto_link auto_link_shortened">www.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.....aaaaaaaaaaaaaaaaaa.com</a>',
            'Shortened URL',
        )
    
    def test_email(self):
        self.assert_wrapped(
            'user@domain.com',
            '<a class="auto_link email" href="mailto:user@domain.com">user[at]domain.com</a>',
            'Email',
        )
    
    def test_symbols(self):
        for bbcode, symbol, name in [
            ('(c)', '©', 'copyright'),
            ('(tm)', '™', 'trademark'),
            ('(r)', '®', 'registered'),
        ]:
            self.assert_wrapped(
                bbcode,
                symbol,
                f'{name.capitalize()} symbol',
            )
        
    def test_smilies(self):
        for bbcode, class_ in [
            (':-p', 'tongue'),
            (';-)', 'wink'),
            (':-o', 'oooh'),
            (':-)', 'smile'),
            (':-(', 'sad'),
            *[(f':{smilie}:', smilie) for smilie in [
                'cool', 'evil', 'huh', 'whatever', 'angel', 'badhair',
                'lmao', 'cd', 'cry', 'idunno', 'embarrassed', 'gift',
                'coffee', 'love', 'isanerd', 'note', 'derp', 'sarcastic',
                'serious', 'sleepy', 'teeth', 'veryhappy', 'yellling',
                'zipped',
            ]],
        ]:
            self.assert_wrapped(
                bbcode,
                f'<i class="smilie {class_}"></i>',
                f'Smilie {bbcode}',
            )
    
    def test_userIconWithText(self):
        self.assert_wrapped(
            ':iconFender:',
            '<a href="/user/fender" class="iconusername"><img src="//a.furaffinity.net/20210516/fender.gif" align="middle" title="Fender" alt="Fender">&nbsp;Fender</a>',
            'User icon with text',
        )

    def test_userIconWithoutText(self):
        self.assert_wrapped(
            ':Fendericon:',
            '<a href="/user/fender" class="iconusername"><img src="//a.furaffinity.net/20210516/fender.gif" align="middle" title="Fender" alt="Fender"></a>',
            'User icon without text',
        )

    def test_userLinkWithoutIcon(self):
        self.assert_wrapped(
            ':linkFender:',
            '<a href="/user/fender" class="linkusername">Fender</a>',
            'User link without icon',
        )