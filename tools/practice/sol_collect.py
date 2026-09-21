import re, requests, pandas as pd
from bs4 import BeautifulSoup
URL = "http://127.0.0.1:8777/data/"

def show(tag, v):
    print(f"@@{tag}"); print(repr(v)); print("@@end")

page1 = requests.get(URL + "workshops.html")
show("q1", (page1.status_code, page1.headers["Content-Type"]))

soup = BeautifulSoup(page1.text, "html.parser")
cards = soup.select("article.workshop")
show("q2", len(cards))

q3 = cards[0].select_one("h3.title a")["title"]
show("q3", q3)
print("link text was:", repr(cards[0].select_one("h3.title a").text))

def rating(card):
    return int(card.select_one("span.rating")["class"][1].split("-")[1])
show("q4", [rating(c) for c in cards])

q5 = sum(int(re.search(r"(\d+)\s+seats", c.select_one("span.seats").text).group(1))
         for c in cards)
show("q5", q5)

q6 = int(re.search(r"TOTAL_WORKSHOPS\s*=\s*(\d+)", page1.text).group(1))
show("q6", q6)

def parse_page(html):
    s = BeautifulSoup(html, "html.parser")
    rows = []
    for c in s.select("article.workshop"):
        price = c.select_one("span.price")
        rows.append({
            "id": c["data-id"],
            "title": c.select_one("h3.title a")["title"],
            "mode": c["data-mode"],
            "rating": int(c.select_one("span.rating")["class"][1].split("-")[1]),
            "seats_left": int(re.search(r"(\d+)", c.select_one("span.seats").text).group(1)),
            "price": price.text.strip() if price else None,
            "starts_on": c.select_one("time")["datetime"],
        })
    nxt = s.select_one("nav.pager a.next")
    return rows, (nxt["href"] if nxt else None)

rows, nxt = parse_page(page1.text)
while nxt:
    rows_more, nxt = parse_page(requests.get(URL + nxt).text)
    rows += rows_more
all_ws = pd.DataFrame(rows)
show("q7", all_ws.shape)

q8 = all_ws.loc[all_ws["price"].isna(), "id"].tolist()
show("q8", q8)

api = requests.get(URL + "slots_api.json").json()
slots = pd.json_normalize(api["results"])
print(list(slots.columns))
q9 = slots.groupby("mode")["seats.left"].sum()
show("q9", q9)

from urllib.robotparser import RobotFileParser
rp = RobotFileParser()
rp.parse(requests.get(URL + "workshops_robots.txt").text.splitlines())
q10 = (rp.can_fetch("my-scraper", "/workshop/W-101"),
       rp.can_fetch("my-scraper", "/register/W-101"),
       rp.can_fetch("GPTBot", "/workshop/W-101"),
       rp.crawl_delay("my-scraper"))
show("q10", q10)
