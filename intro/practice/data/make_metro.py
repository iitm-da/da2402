#!/usr/bin/env python3
"""Write metro_daily.csv and metro_stations.csv for the pandas worksheet.

Synthetic. Station names are real, the numbers are not. Seeded, so re-running
reproduces the file the worksheet answers were computed from.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260921)

STATIONS = [
    # station, line, zone, opened, interchange
    ("Washermanpet",   "Blue",  1, "2016-05-14", False),
    ("Chennai Central","Blue",  1, "2015-06-29", True),
    ("Government Estate","Blue",1, "2015-06-29", False),
    ("Thousand Lights","Blue",  1, "2015-06-29", False),
    ("Teynampet",      "Blue",  2, "2015-06-29", False),
    ("Saidapet",       "Blue",  2, "2015-06-29", False),
    ("Guindy",         "Blue",  2, "2015-06-29", False),
    ("Alandur",        "Blue",  3, "2015-06-29", True),
    ("Airport",        "Blue",  3, "2015-06-29", False),
    ("Egmore",         "Green", 1, "2016-05-14", False),
    ("Nehru Park",     "Green", 1, "2016-05-14", False),
    ("CMBT",           "Green", 2, "2016-05-14", True),
    ("Koyambedu",      "Green", 2, "2015-06-29", False),
    ("Arumbakkam",     "Green", 2, "2015-06-29", False),
    ("Vadapalani",     "Green", 2, "2015-06-29", False),
    ("Ashok Nagar",    "Green", 3, "2015-06-29", False),
    ("Ekkattuthangal", "Green", 3, "2015-06-29", False),
    ("St Thomas Mount","Green", 3, "2015-06-29", False),
]

# Weekday footfall scale per station, in thousands of entries.
BASE = {
    "Chennai Central": 24.0, "Alandur": 18.5, "CMBT": 17.0, "Egmore": 15.5,
    "Guindy": 14.0, "Airport": 12.5, "Koyambedu": 11.5, "Vadapalani": 10.5,
    "Saidapet": 9.5, "Thousand Lights": 8.5, "Teynampet": 8.0,
    "Ashok Nagar": 7.5, "St Thomas Mount": 7.0, "Arumbakkam": 6.5,
    "Nehru Park": 6.0, "Washermanpet": 5.5, "Ekkattuthangal": 5.0,
    "Government Estate": 4.0,
}
FARE = {1: 22.0, 2: 32.0, 3: 44.0}      # mean ticket value by zone

stations = pd.DataFrame(STATIONS, columns=["station", "line", "zone", "opened", "interchange"])
dates = pd.date_range("2025-01-01", "2025-06-30", freq="D")

rows = []
for d in dates:
    weekend = d.dayofweek >= 5
    # a slow January, a March peak, monsoon-free months flat
    season = {1: 0.93, 2: 0.98, 3: 1.08, 4: 1.02, 5: 1.00, 6: 0.96}[d.month]
    for st, line, zone, _, inter in STATIONS:
        scale = BASE[st] * 1000 * season * (0.62 if weekend else 1.0)
        entries = int(rng.normal(scale, scale * 0.09))
        # exits track entries but never match them exactly
        exits = int(entries * rng.normal(1.0, 0.05))
        fare = FARE[zone] * rng.normal(1.0, 0.03)
        rows.append((d.date().isoformat(), st, max(entries, 0), max(exits, 0),
                     round(entries * fare, 2)))

daily = pd.DataFrame(rows, columns=["date", "station", "entries", "exits", "fare_collected"])
daily.to_csv("metro_daily.csv", index=False)
stations.to_csv("metro_stations.csv", index=False)
print(daily.shape, stations.shape)
