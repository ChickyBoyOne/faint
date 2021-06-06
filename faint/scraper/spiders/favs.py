from datetime import datetime

from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import Selector, SelectorList

from .utils import FA_BASE, cleave, format_date, normalize_url, not_class
from ..items import Favorite


class FavsSpider:
    def get_last_fav_time(self, response: HtmlResponse) -> datetime:
        return format_date(response.css("div.midsection span::attr(title)").get(), self.parameters)
    
    def get_page_favs(self, response: HtmlResponse) -> SelectorList:
        return response.css("figure[data-fav-id]")

    def get_fav_model(self, fav: Selector, time: datetime) -> Favorite:
        return Favorite(
            id=fav.attrib["data-fav-id"],
            time=time,
            sid=fav.attrib["id"].replace("sid-", ""),
            url=normalize_url(fav.css("a::attr(href)").get()),
            username=fav.attrib["data-user"].replace("u-", ""),
            rating=cleave(not_class(fav, "t-image")),
        )
    
    def get_fav_request(self, base: str, fav: Selector) -> Request:
        return Request(url=base + f"/{fav.attrib['data-fav-id']}/next", callback=self.parse_fav)

    def parse_favs(self, response: HtmlResponse, queue: list[str] = []):
        if not (favs := self.get_page_favs(response)):
            return
        
        base = "/".join(response.url.split("/")[:5])
        last_fav_time = self.get_last_fav_time(response)
        if (next_url := response.css("div.pagination a.right::attr(href)").get()):
            next_url = FA_BASE + next_url
        
        # Reverse chronological order - we're not there yet
        if self.parameters.before < last_fav_time:
            if next_url:
                yield Request(url=next_url, callback=self.parse_favs, cb_kwargs={"queue": favs[:-1]})
            else:
                for fav in favs[:-1]:
                    yield self.get_fav_request(base, fav)
            
            return
        
        for fav in queue:
            yield self.get_fav_request(base, fav)
        
        # We're all done - no more inside the range
        if self.parameters.after > last_fav_time:
            return
        
        yield self.get_fav_model(favs[0], last_fav_time)

        for fav in favs[:-1]:
            yield self.get_fav_request(base, fav)
        
        if next_url:
            yield Request(url=next_url, callback=self.parse_favs)
    
    def parse_fav(self, response: HtmlResponse):
        if self.parameters.before < (last_fav_time := self.get_last_fav_time(response)) \
                or self.parameters.after > last_fav_time:
            return
        
        yield self.get_fav_model(self.get_page_favs(response)[0], last_fav_time)
