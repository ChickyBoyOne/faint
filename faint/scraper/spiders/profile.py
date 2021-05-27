from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse

from faint.util import FA_BASE


class ProfileSpider(Spider):
    name = 'profile'

    def start_requests(self):
        yield Request(url=FA_BASE + f'/user/{self.username}/', callback=self.parse_profile, cookies=self.cookies)
    
    def parse_profile(self, response: HtmlResponse):
        pass