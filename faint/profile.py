from html import unescape
import itertools
import json
from typing import Optional

from bs4.element import Tag
from httpx import Client

from .bbcode import to_bbcode
from .data import Badge, Contact, GallerySubmission, ProfileJournal, ProfileSubmission, Question, \
    Rating, Settings, Shinies, ShinyDonation, Shout, Special, Stats, Supporter, UserProfile, WatchInfo
from .util import cleave, FA_BASE, format_date, get_direct_text, get_page_soup, get_soup, \
    get_subtitle_num, normalize_url, not_class

def get_special(tag: Tag) -> Optional[Special]:
    if not (img := tag.img):
        return None
    
    return Special(
        id=not_class(img, "inline").replace("-icon", "").replace("-logo", ""),
        img=normalize_url(img["src"]),
        title=img["title"],
    )

def get_gallery_submissions(section: Tag, submission_data: dict[str, str], settings: Settings) -> list[GallerySubmission]:
    submissions = []

    for figure in section.find_all("figure"):
        sid = cleave(figure["id"])
        data = submission_data[sid]
        img = figure.img
        submissions.append(GallerySubmission(
            id=sid,
            url=normalize_url(figure.a["href"]),
            img=normalize_url(img["src"]),
            width=img["data-width"],
            height=img["data-height"],
            title=unescape(data["title"]),
            username=data["username"],
            time=format_date(get_soup(data["html_date"]).span["title"], settings),
            rating=data["icon_rating"],
        ))
    
    return submissions

def get_user_list(body: Tag) -> list[str]:
    if not (table := body.table):
        return []
    
    return [td.get_text() for td in table.find_all("td")]

def get_profile(client: Client, settings: Settings) -> UserProfile:
    soup = get_page_soup(client, f"{FA_BASE}/user/{settings.username}/")

    user_block = soup.find("div", class_="username")
    name_block = user_block.select_one("h2 span")
    username = username[1:] if (username := name_block.get_text().strip())[0] in "~!∞" else username
    status = name_block["title"].split(": ")[-1].lower()
    special = get_special(name_block)
    fa_plus = special.id == "fa-plus" if special else False
    title, _, joined = user_block.find("span", class_="font-small").get_text().strip().rpartition(" | ")
    title = title if title else None
    joined = format_date(joined.split(": ")[-1], settings)
    avatar = normalize_url(soup.find("img", class_="user-nav-avatar")["src"])

    profile_block = soup.find("div", class_="userpage-profile")
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

    script = soup.select_one("div#site-content > script").contents[0]
    submission_line = next(l for l in script.splitlines() if "submission_data" in l)
    submission_data = json.loads(submission_line.partition(" = ")[2][:-1])

    for section in soup.select("section.userpage-left-column, section.userpage-right-column"):
        if not (header := section.select_one("div.section-header")):
            for container in section.find_all("div", class_="comment_container"):
                username = container.find("div", class_="comment_username")
                user.shouts.append(Shout(
                    username=username.get_text(),
                    special=get_special(username),
                    avatar=normalize_url(container.find("img", class_="comment_useravatar")["src"]),
                    time=format_date(container.find("span", class_="popup_date").get_text(), settings),
                    text=to_bbcode(container.find("div", class_="comment_text")),
                ))
            
            continue

        label = header.h2.get_text()
        bodies = section.find_all("div", class_="section-body")
        body = bodies[0]
        
        if label == "Featured Submission":
            a = body.h2.a
            href = a["href"]
            user.submission = ProfileSubmission(
                id=href.split("/")[-2],
                url=normalize_url(href),
                img=normalize_url(body.img["src"]),
                title=a.get_text(),
                rating=cleave(body.a["class"][0]),
            )
        elif label == "Gallery":
            user.gallery = get_gallery_submissions(section, submission_data, settings)
        elif label == "Favorites":
            user.favorites = get_gallery_submissions(section, submission_data, settings)
        elif "'s Top Supporters" in label:
            top = [Supporter(
                    username=(img := div.img)["alt"],
                    url=normalize_url(div.a["href"]),
                    avatar=normalize_url(img["src"])
                ) for div in body.div.find_all("div", recursive=False)]
            plural = body.h2.get_text().split()[-1]
            user.shinies = shinies = Shinies(plural=plural if fa_plus else None, top=top)
            
            for donation in body.find_all("div", class_="comment_container"):
                shinies.recent.append(ShinyDonation(
                    supporter=Supporter(
                        username=(img := donation.img)["alt"],
                        url=normalize_url(donation.a["href"]),
                        avatar=normalize_url(img["src"]),
                    ),
                ))

                if fa_plus and len(parts := get_direct_text(donation.find("div", class_="name")).split()) == 5:
                    shinies.singular = parts[2]

                if (message := donation.find("div", class_="comment_text").get_text(strip=True)):
                    message = message[1:][:-1]
                    shinies.recent[-1].message = message
        elif "Send " in label:
            if fa_plus:
                script = body.script.contents[0]
                cost_line = next(l for l in script.splitlines() if "shinies_cost" in l)
                shinies.price = cost_line.partition(" = ")[2][:-1]
            shinies.messages = body.find("div", id="shinies-input") is not None
        elif label == "Recent Watchers":
            user.watchers = WatchInfo(
                num=get_subtitle_num(header),
                recent=get_user_list(body),
            )
        elif label == "Recently Watched":
            user.watched = WatchInfo(
                num=get_subtitle_num(header),
                recent=get_user_list(body),
            )
        elif label == "Stats":
            lines = itertools.chain.from_iterable(cell.get_text().strip().splitlines() for cell in body.find_all("div", class_="cell"))
            nums = [int(line.split(": ")[-1]) for line in lines]
            user.stats = Stats(**{field: value for field, value in zip(Stats.__fields__.keys(), nums)})
        elif label == "Recent Journal":
            link = header.a
            href = link["href"]
            user.journal = ProfileJournal(
                id=href.split("/")[-1],
                url=normalize_url(href),
                comments=get_subtitle_num(header),
                title=body.h2.get_text(),
                time=format_date(body.find("span", class_="popup_date")["title"], settings),
                text=to_bbcode(body.div),
            )
        elif label == "Badges":
            for badge in body.find_all("div", class_="badge"):
                img = badge.img
                user.badges.append(Badge(
                    id=cleave(badge["id"]),
                    name=not_class(badge, "badge"),
                    img=normalize_url(img["src"]),
                    title=img["title"],
                ))
        elif label == "User Profile":
            info = user.info

            if (submission := section.find("div", class_="section-submission")):
                url = submission.a["href"]
                info.submission = ProfileSubmission(
                    id=url.split("/")[-2],
                    url=normalize_url(url),
                    img=normalize_url(submission.img["src"]),
                    # Profile IDs must be of general rating: https://forums.furaffinity.net/threads/furaffinity-profile-id-photo-disabled.1623882/post-5664357
                    rating=Rating.GENERAL,
                )
            
            rows = section.find_all("div", class_="table-row")
            info.trades, info.commissions = [get_direct_text(row) == "Yes" for row in rows[:2]]
            for row in rows[2:]:
                info.questions.append(Question(
                    question=(question := row.strong.get_text()),
                    answer=to_bbcode(row) if question in [
                        "Favorite Artists",
                        "Favorite Site",
                    ] else get_direct_text(row),
                ))
            
            if (contacts := section.find("div", class_="user-contact")):
                for item in contacts.find_all("div", class_="user-contact-item"):
                    site = cleave(item.div.div["class"][0])
                    if (a := item.a):
                        info.contacts.append(Contact(
                            site=site,
                            id=a.get_text(),
                            url=a["href"],
                        ))
                    else:
                        info.contacts.append(Contact(
                            site=site,
                            id=get_direct_text(item.find("div", class_="user-contact-user-info")),
                            url=None,
                        ))
    
    return user