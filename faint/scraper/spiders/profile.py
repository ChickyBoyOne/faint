import json
from typing import Optional

from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import SelectorList

from faint.scraper.spiders.bbcode import to_bbcode
from faint.scraper.spiders.utils import FA_BASE, format_date, get_direct_text, get_text, normalize_url, not_class
from faint.scraper.items import Shout, Special, UserProfile


class ProfileSpider:
    def get_special(self, tag: SelectorList) -> Optional[Special]:
        if not (img := tag.css("img")):
            return None
        
        return Special(
            id=not_class(img, "inline").replace("-icon", "").replace("-logo", ""),
            img=normalize_url(img["src"]),
            title=img["title"],
        )
    
    def parse_profile(self, response: HtmlResponse):
        user_block = response.css("div.username")
        name_block = user_block.css("h2 span")
        username = username[1:] if (username := get_direct_text(name_block).strip()) else username
        status = name_block.attrib["title"].split(": ")[-1].lower()
        special = self.get_special(name_block)
        fa_plus = special.id == "fa-plus" if special else False
        title, _, joined = get_direct_text(user_block.css("span.font-small")).strip().rpartition(" | ")
        title = title if title else None
        joined = format_date(joined.split(": ")[-1], self.parameters)
        avatar = normalize_url(response.css("img.user-nav-avatar").attrib["src"])

        profile_block = response.css("div.userpage-profile")
        profile = to_bbcode(profile_block)

        user = UserProfile(
            username=username,
            status=status,
            special=special,
            title=title,
            joined=joined,
            avatar=avatar,
            profile=profile,
        )

        script = response.css("div#site-content > script::text").get()
        submission_line = next(l for l in script.splitlines() if "submission_data" in l)
        submission_data = json.loads(submission_line.partition(" = ")[2][:-1])

        for section in response.css("section.userpage-left-column, section.userpage-right-column"):
            if not (header := section.css("div.section-header")):
                for container in section.css("div.comment_container"):
                    username = container.css("div.comment_username")
                    user.shouts.append(Shout(
                        username=get_direct_text(username),
                        special=self.get_special(username),
                        avatar=normalize_url(container.css("img.comment_useravatar").attrib["src"]),
                        time=format_date(container.css("span.popup_date").attrib["title"], self.parameters),
                        text=to_bbcode(container.css("div.comment_text")),
                    ))
            
        yield user