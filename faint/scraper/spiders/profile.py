from html import unescape
import json
from typing import Any, Optional

from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import SelectorList

from faint.scraper.spiders.bbcode import BBCodeLocation, to_bbcode
from faint.scraper.spiders.utils import cleave, format_date, get_direct_text, get_soup, normalize_url, not_class
from faint.scraper.items import GallerySubmission, ProfileSubmission, Shinies, ShinyDonation, Shout, Special, Supporter, UserProfile


class ProfileSpider:
    submission_data: dict[str, dict[str, Any]]

    def get_special(self, tag: SelectorList) -> Optional[Special]:
        if not (img := tag.css("img")):
            return None
        
        return Special(
            id=not_class(img, "inline").replace("-icon", "").replace("-logo", ""),
            img=normalize_url(img.attrib["src"]),
            title=img.attrib["title"],
        )
    
    def get_gallery_submissions(self, section: SelectorList) -> list[GallerySubmission]:
        submissions = []

        for figure in section.css("figure"):
            id = cleave(figure.attrib["id"])
            data = self.submission_data[id]
            img = figure.css("img")
            submissions.append(GallerySubmission(
                id=id,
                url=normalize_url(figure.css("a::attr(href)").get()),
                img=normalize_url(img.attrib["src"]),
                width=img.attrib["data-width"],
                height=img.attrib["data-height"],
                title=unescape(data["title"]),
                username=data["username"],
                time=format_date(get_soup(data["html_date"])["title"], self.parameters),
                rating=data["icon_rating"],
            ))
    
    def parse_profile(self, response: HtmlResponse):
        user_block = response.css("div.username")
        name_block = user_block.css("h2 span")
        username = username[1:] if (username := get_direct_text(name_block).strip())[0] in "~!∞" else username
        status = name_block.attrib["title"].split(": ")[-1].lower()
        special = self.get_special(name_block)
        fa_plus = special.id == "fa-plus" if special else False
        title, _, joined = get_direct_text(user_block.css("span.font-small")).strip().rpartition(" | ")
        title = title if title else None
        joined = format_date(joined.split(": ")[-1], self.parameters)
        avatar = normalize_url(response.css("img.user-nav-avatar").attrib["src"])

        profile_block = response.css("div.userpage-profile")
        profile = to_bbcode(profile_block, BBCodeLocation.PROFILE)

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
        self.submission_data = json.loads(submission_line.partition(" = ")[2][:-1])

        for section in response.css("section.userpage-left-column, section.userpage-right-column"):
            if not (header := section.css("div.section-header")):
                for container in section.css("div.comment_container"):
                    username = container.css("div.comment_username")
                    user.shouts.append(Shout(
                        username=get_direct_text(username),
                        special=self.get_special(username),
                        avatar=normalize_url(container.css("img.comment_useravatar").attrib["src"]),
                        time=format_date(container.css("span.popup_date").attrib["title"], self.parameters),
                        text=to_bbcode(container.css("div.comment_text"), BBCodeLocation.COMMENT),
                    ))
            
                break
            
            label = header.css("h2::text").get()
            bodies = section.css("div.section-body")
            body = bodies[0]

            if label == "Featured Submission":
                a = body.css("h2 a")
                href = a.attrib["href"]
                user.submission = ProfileSubmission(
                    id=href.split("/")[-2],
                    url=normalize_url(href),
                    img=normalize_url(body.css("img::attr(src)").get()),
                    title=get_direct_text(a),
                    rating=cleave(body.css("a::attr(class)").get())
                )
            elif label == "Gallery":
                user.gallery = self.get_gallery_submissions(section)
            elif label == "Favorites":
                user.favorites = self.get_gallery_submissions(section)
            elif label == f"{username}'s Top Supporters":
                top = [Supporter(
                    username=(img := div.css("img")).attrib["alt"],
                    url=normalize_url(div.css("a::attr(href)").get()),
                    avatar=normalize_url(normalize_url(img.attrib["src"])),
                ) for div in body.css("div.shinies-top-3-container > div")]
                plural = body.css("h2::text").get().split()[-1]
                user.shinies = shinies = Shinies(plural=plural if fa_plus else None, top=top)

                for donation_div in body.css("div.comment_container"):
                    shinies.recent.append((donation := ShinyDonation(supporter=Supporter(
                        username=(img := donation_div.css("img")).attrib["alt"],
                        url=normalize_url(donation_div.css("a::attr(href)").get()),
                        avatar=normalize_url(img.attrib["src"]),
                    ))))

                if fa_plus and len(parts := get_direct_text(donation_div.find("div", class_="name")).split()) == 5:
                    shinies.singular = parts[2]
                
                if (message := donation_div.css("div.comment_text::text").get()):
                    donation.message = message.strip()[1:][:-1]
            elif label.startswith(f"Send {username} "):
                if fa_plus:
                    script = body.css("script::text").get()
                    cost_line = next(l for l in script.splitlines() if "shinies_cost" in l)
                    shinies.price = cost_line.partition(" = ")[2][:-1]
                shinies.messages = len(body.css("div.shinies-input")) > 0
            elif label == "Recent Watchers":
                pass
            elif label == "Recently Watched":
                pass
            elif label == "Stats":
                pass
            elif label == "Recent Journal":
                pass
            elif label == "Badges":
                pass
            elif label == "User Profile":
                pass
            
        yield user