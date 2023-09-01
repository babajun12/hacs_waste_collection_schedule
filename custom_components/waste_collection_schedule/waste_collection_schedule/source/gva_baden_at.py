from datetime import datetime

import requests
from bs4 import BeautifulSoup
from waste_collection_schedule import Collection

TITLE = "GVA Baden"
DESCRIPTION = "Source for waste collection services Association of Municipalities in the District of Baden bei Wien, Austria"
URL = "https://baden.umweltverbaende.at/"
TEST_CASES = {
    "Test_001": {"region": "Pfaffstätten"},
    "Test_002": {"region": "Baden"},
    "Test_003": {"region": "Traiskirchen"},
    "Test_004": {"region": "Sooß"},
}
ICON_MAP = {
    "Restmüll": "mdi:trash-can",
    "Gelber Sack": "mdi:sack",
    "Altpapier": "mdi:package-variant",
    "Biotonne": "mdi:leaf",
}


class Source:
    def __init__(self, region):
        self._region = region

    def fetch(self):
        s = requests.Session()
        # get list of regions and weblinks
        r0 = s.get("https://baden.umweltverbaende.at/?kat=32")
        soup = BeautifulSoup(r0.text, "html.parser")
        table = soup.find_all("div", {"class": "col-sm-9"})
        entries = []
        for item in table:
            weblinks = item.find_all("a", {"class": "weblink"})
            for item in weblinks:
                # match weblink with region to get collection schedule
                if self._region in item.text:
                    r1 = s.get(f"https://baden.umweltverbaende.at/{item['href']}")
                    soup = BeautifulSoup(r1.text, "html.parser")
                    schedule = soup.find_all("div", {"class": "tunterlegt"})
                    for day in schedule:
                        txt = day.text.strip().split(
                            "   "
                        )  # this is not 3 space characters, the middle one is U+00a0
                        entries.append(
                            Collection(
                                date=datetime.strptime(txt[1], "%d.%m.%Y").date(),
                                t=txt[2],
                                icon=ICON_MAP.get(txt[2]),
                            )
                        )

        return entries
