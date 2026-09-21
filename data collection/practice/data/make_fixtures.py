#!/usr/bin/env python3
"""Write the fixtures for the data collection worksheet.

Two listing pages, a robots.txt and a saved API response, all invented. The
traps are planted, so the worksheet's answers are known by construction:

  full title     only in the link's title attribute, the link text is cut
  rating         a class (rating-4), not text
  seats          "12 seats left", needs a regex
  price          missing on W-105 and W-113
  id             in data-id
  total          only in a <script> variable
  page 2         reachable only through rel="next"
"""
import json

W = [  # id, title, venue, rating, seats_left, fee, mode, date
    ("W-101", "Time series forecasting with statsmodels", "Research Park", 4, 12, 2500, "online", "2026-10-08"),
    ("W-102", "Pandas for tabular data at scale", "ICSR Hall", 5, 4, 1800, "in-person", "2026-10-09"),
    ("W-103", "Scraping public data without getting blocked", "Research Park", 3, 22, 2500, "online", "2026-10-10"),
    ("W-104", "Regular expressions for messy text fields", "ICSR Hall", 4, 9, 1200, "in-person", "2026-10-13"),
    ("W-105", "Missing data mechanisms and what they permit", "Research Park", 5, 0, None, "online", "2026-10-14"),
    ("W-106", "Outlier detection beyond the box plot", "DSAI Seminar Room", 3, 17, 1800, "in-person", "2026-10-15"),
    ("W-107", "Record linkage and deduplication", "ICSR Hall", 4, 6, 2500, "in-person", "2026-10-16"),
    ("W-108", "Matplotlib without the defaults", "Research Park", 5, 11, 1200, "online", "2026-10-17"),
    ("W-109", "SQL for people who already know pandas", "DSAI Seminar Room", 4, 31, 1800, "online", "2026-10-20"),
    ("W-110", "Version control for data projects", "ICSR Hall", 2, 25, 900, "in-person", "2026-10-21"),
    ("W-111", "Geospatial joins with GeoPandas", "Research Park", 4, 8, 2500, "online", "2026-10-22"),
    ("W-112", "Reproducible notebooks and why they break", "DSAI Seminar Room", 3, 14, 900, "in-person", "2026-10-23"),
    ("W-113", "Dashboards that survive a live demo", "Research Park", 5, 3, None, "online", "2026-10-24"),
    ("W-114", "APIs, pagination and rate limits", "ICSR Hall", 4, 19, 1800, "online", "2026-10-27"),
    ("W-115", "Feature stores for small teams", "DSAI Seminar Room", 2, 27, 1200, "in-person", "2026-10-28"),
    ("W-116", "Evaluating imputation against held-out truth", "Research Park", 5, 5, 2500, "online", "2026-10-29"),
    ("W-117", "Parquet, Arrow and the columnar file", "ICSR Hall", 4, 16, 1800, "in-person", "2026-10-30"),
    ("W-118", "Writing a data dictionary people read", "DSAI Seminar Room", 3, 21, 900, "online", "2026-10-31"),
]
MONTHS = {"10": "Oct", "11": "Nov"}

def cut(title, n=34):
    return title if len(title) <= n else title[:n].rstrip() + " …"

def card(w):
    wid, title, venue, rating, seats, fee, mode, date = w
    shown = f"{int(date[8:])} {MONTHS[date[5:7]]} {date[:4]}"
    price = f'      <span class="price">₹{fee:,}</span>\n' if fee else ""
    return (
f'''    <article class="workshop" data-id="{wid}" data-mode="{mode}">
      <h3 class="title"><a href="workshop_{wid}.html" title="{title}">{cut(title)}</a></h3>
      <p class="venue">IIT Madras · {venue}</p>
      <span class="rating rating-{rating}"></span>
      <span class="seats">{seats} seats left</span>
{price}      <time datetime="{date}">{shown}</time>
    </article>''')

HEAD = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Workshops · page {page}</title>
  {links}
</head>
<body>
  <h1>Upcoming workshops</h1>
  <section class="listing">
{cards}
  </section>
{nav}
  <script>
    var TOTAL_WORKSHOPS = {total};
    var PAGE_SIZE = 12;
  </script>
</body>
</html>
'''

def page(n, rows, links, nav):
    return HEAD.format(page=n, links=links, cards="\n".join(card(w) for w in rows),
                       nav=nav, total=len(W))

open("workshops.html", "w", encoding="utf-8").write(page(
    1, W[:12],
    '<link rel="next" href="workshops_page2.html"/>',
    '  <nav class="pager"><span>Page 1 of 2</span>'
    '<a class="next" href="workshops_page2.html">Next</a></nav>'))

open("workshops_page2.html", "w", encoding="utf-8").write(page(
    2, W[12:],
    '<link rel="prev" href="workshops.html"/>',
    '  <nav class="pager"><a class="prev" href="workshops.html">Previous</a>'
    '<span>Page 2 of 2</span></nav>'))

open("workshops_robots.txt", "w", encoding="utf-8").write(
'''User-agent: *
Crawl-delay: 5
Disallow: /admin/
Disallow: /register/
Allow: /

User-agent: GPTBot
Disallow: /
''')

api = {"meta": {"page": 1, "per_page": 18, "total": 18, "generated": "2026-09-21"},
       "results": [
           {"workshop_id": wid,
            "mode": mode,
            "fee_inr": fee,
            "seats": {"total": 40, "left": seats},
            "venue": {"campus": "IIT Madras", "room": venue},
            "starts_on": date}
           for wid, title, venue, rating, seats, fee, mode, date in W]}
json.dump(api, open("slots_api.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("wrote 4 fixtures,", len(W), "workshops")
