from build import build, load_outputs
O = load_outputs("out_collect.txt")
# Q1 is captured against the local test server; the course repo is served by
# raw.githubusercontent, which labels an .html file text/plain.
O["q1"] = "(200, 'text/plain; charset=utf-8')"

INTRO = """# Practice · data collection

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Ten questions against four files served over HTTP. Each question names a variable. Put your result
in that variable and run the cell. The worked answer sits under **Answer**. Click it open once you
have tried.

**The pages.** A two-page workshop listing, its robots.txt and a saved API response, written for
this worksheet. They live in the course repository and are fetched over the network, so `requests`
does real work and no outside site has to stay up.

- `workshops.html`, `workshops_page2.html`: 18 workshop cards, 12 on the first page
- `workshops_robots.txt`: the crawl rules
- `slots_api.json`: the same 18 workshops as a JSON API response

The full title, the rating, the seat count and the total are each stored somewhere other than the
card's visible text. There is a question on each.
"""

SETUP = """import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/data%20collection/practice/data/"

print(URL)"""

Q = [
 dict(title="Fetching the page", out="q1",
      task="Fetch `workshops.html` into `page1` with `requests`. Report the status code and the\n`Content-Type` header the server sends back. Note what the server calls the file.",
      shape="a tuple `(status_code, content_type)`.",
      stub='page1 = ...   # your answer\nq1 = ...\nq1',
      solution='page1 = requests.get(URL + "workshops.html")\nq1 = (page1.status_code, page1.headers["Content-Type"])\nq1'),
 dict(title="Counting the cards", out="q2",
      task="Parse `page1` with BeautifulSoup and count the workshop cards on it. A card is an\n`article` carrying class `workshop`.",
      shape="an `int`.",
      solution='soup = BeautifulSoup(page1.text, "html.parser")\ncards = soup.select("article.workshop")\nq2 = len(cards)\nq2'),
 dict(title="The full title", out="q3",
      task="The first card's link text is cut short with an ellipsis. The full title sits on the link\nitself. Report it.",
      shape="a `str`.",
      solution='q3 = cards[0].select_one("h3.title a")["title"]\nq3'),
 dict(title="Rating from the class name", out="q4",
      task="A card's rating is held as the second class on `span.rating`, written `rating-4`. Pull the\nnumber out for all 12 cards on page 1, in page order.",
      shape="a list of 12 ints.",
      solution='def rating(card):\n    return int(card.select_one("span.rating")["class"][1].split("-")[1])\n\nq4 = [rating(c) for c in cards]\nq4'),
 dict(title="Seat count from the card text", out="q5",
      task="`span.seats` reads `12 seats left`. Total the seats left across page 1.",
      shape="an `int`.",
      solution='q5 = sum(int(re.search(r"(\\d+)\\s+seats", c.select_one("span.seats").text).group(1))\n         for c in cards)\nq5'),
 dict(title="TOTAL_WORKSHOPS in a script block", out="q6",
      task="The page declares `TOTAL_WORKSHOPS` inside a `<script>` block, out of reach of a CSS\nselector. Read it with a regex over the response text.",
      shape="an `int`.",
      solution='q6 = int(re.search(r"TOTAL_WORKSHOPS\\s*=\\s*(\\d+)", page1.text).group(1))\nq6'),
 dict(title="Following the next link", out="q7",
      task="Page 1 links to page 2 through `nav.pager a.next`, and page 2 has no such link. Parse both\npages into one DataFrame with columns `id`, `title`, `mode`, `rating`, `seats_left`, `price`,\n`starts_on`, leaving `price` as `None` where a card has none. Report its shape.",
      shape="a tuple `(rows, columns)`.",
      solution='''def parse_page(html):
    s = BeautifulSoup(html, "html.parser")
    rows = []
    for c in s.select("article.workshop"):
        price = c.select_one("span.price")
        rows.append({
            "id": c["data-id"],
            "title": c.select_one("h3.title a")["title"],
            "mode": c["data-mode"],
            "rating": int(c.select_one("span.rating")["class"][1].split("-")[1]),
            "seats_left": int(re.search(r"(\\d+)", c.select_one("span.seats").text).group(1)),
            "price": price.text.strip() if price else None,
            "starts_on": c.select_one("time")["datetime"],
        })
    nxt = s.select_one("nav.pager a.next")
    return rows, (nxt["href"] if nxt else None)


rows, nxt = parse_page(page1.text)
while nxt:
    more, nxt = parse_page(requests.get(URL + nxt).text)
    rows += more

all_ws = pd.DataFrame(rows)
q7 = all_ws.shape
q7'''),
 dict(title="Cards with no price", out="q8",
      task="Two of the 18 cards carry no `span.price`. Report their ids, using the frame from Q7.",
      shape="a list of 2 strings.",
      solution='q8 = all_ws.loc[all_ws["price"].isna(), "id"].tolist()\nq8'),
 dict(title="The JSON API", out="q9",
      task="`slots_api.json` holds the same 18 workshops under `results`, with `seats` and `venue`\nnested one level down. Flatten the records and total the seats left per mode.",
      shape="a Series indexed by mode.",
      solution='api = requests.get(URL + "slots_api.json").json()\nslots = pd.json_normalize(api["results"])\n\nq9 = slots.groupby("mode")["seats.left"].sum()\nq9'),
 dict(title="What robots.txt permits", out="q10",
      task="Read `workshops_robots.txt` with `urllib.robotparser` and answer four things: may\n`my-scraper` fetch `/workshop/W-101`, may it fetch `/register/W-101`, may `GPTBot` fetch\n`/workshop/W-101`, and what crawl delay applies to `my-scraper`.",
      shape="a tuple of three bools and a number.",
      solution='''from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.parse(requests.get(URL + "workshops_robots.txt").text.splitlines())

q10 = (rp.can_fetch("my-scraper", "/workshop/W-101"),
       rp.can_fetch("my-scraper", "/register/W-101"),
       rp.can_fetch("GPTBot", "/workshop/W-101"),
       rp.crawl_delay("my-scraper"))
q10'''),
]
for q in Q:
    q["output"] = O[q["out"]]

build(dict(colab_path="data%20collection/practice/data_collection_worksheet.ipynb",
           intro=INTRO, setup=SETUP, questions=Q),
      "/mnt/e/iitm course/da2402-26/data collection/practice/data_collection_worksheet.ipynb")
