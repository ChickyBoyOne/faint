from scrapy import Request, Spider

from faint.util import FA_BASE


class UserSpider(Spider):
    name = 'user'
    
    def start_requests(self):
        yield Request(url=FA_BASE + f'/controls/settings/', callback=self.parse_settings, cookies=self.cookies)
    
    def parse_settings(self, response):
        print(type(response))