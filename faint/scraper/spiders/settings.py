from datetime import timedelta, timezone

import dateparser
from pytz.exceptions import UnknownTimeZoneError
from scrapy import Request, Spider
from scrapy.crawler import CrawlerRunner
from scrapy.http.response.html import HtmlResponse
from twisted.internet import reactor

from .profile import ProfileSpider
from faint.util import FA_BASE, logger


class SettingsSpider(Spider):
    name = 'settings'
    
    def start_requests(self):
        yield Request(url=FA_BASE + f'/controls/settings/', callback=self.parse_settings, cookies=self.cookies)
    
    def parse_marker(self, marker: str, timezone: str):
        return dateparser.parse(marker, settings={
            'TIMEZONE': timezone,
            'RETURN_AS_TIMEZONE_AWARE': True,
        })
    
    def parse_settings(self, response: HtmlResponse):
        errors = []

        tz = response.css('select[name=timezone] option[selected]').attrib['value']
        negative, hours, minutes = tz[0] == '-', int(tz[1:3]), int(tz[3:5])
        tz = timedelta(hours=hours, minutes=minutes)
        if negative:
            tz = -tz
        if response.css('input[name=timezone_dst]').attrib.get('checked', ''):
            if tz.seconds // 60 // 60 == 23:
                tz = -timedelta(hours=11, minutes=60 - (tz.seconds // 60 % 60))
            else:
                tz += timedelta(hours=1)
        tz = timezone(tz).tzname(None)

        try:
            dateparser.parse('1970-01-01', date_formats=['%Y-%m-%d'], locales=['en-US'],
                settings={'TO_TIMEZONE': self.to_timezone})
        except UnknownTimeZoneError:
            errors.append(f'{self.to_timezone} is not a valid timezone! Please choose one from this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones')

        if not (after := self.parse_marker(self.after, tz)):
            errors.append(f'{self.after} is not a valid date/time!')
        if not (before := self.parse_marker(self.before, tz)):
            errors.append(f'{self.before} is not a valid date/time!')
        
        if errors:
            for error in errors:
                logger.error(error)
            return
        
        if not any([self.gallery, self.scraps, self.folders, self.favs]):
            self.profile = True
        
        settings = {
            'cookies': self.cookies,
            'username': self.username,
            'timezone': tz,
            'to_timezone': self.to_timezone,
            'after': after,
            'before': before,
        }
        runner = CrawlerRunner()
        if self.profile:
            runner.crawl(ProfileSpider, **settings)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())