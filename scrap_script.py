import argparse
import json

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Build processed data files for the dashboard.")
    parser.add_argument("--timeline-only", action="store_true",
                        help="only rebuild data/tl_df.csv (no Reuters scraping, geo_df.csv untouched)")
    args = parser.parse_args()

    if not args.timeline_only:
        build_geo_df()
    build_timeline_df()


def build_geo_df():
    # Imported here so the timeline-only run doesn't need the scraping dependencies
    from bs4 import BeautifulSoup
    import requests

    # Read the HTML
    URL = "https://www.reuters.com/graphics/USA-ELECTION/RESULTS/zjpqnemxwvx/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # Reading data from the web page
    tables = soup.find_all("table", class_="results-table")
    df_election = read_tables(tables)
    df_election = pd.DataFrame(df_election, columns = ["State", "Democrat", "Republican"])

    # Load dict with state abbreviations and full names
    with open('data/raw/state_short2long.json', 'r') as f:
        state_short2long = json.load(f)
    with open('data/raw/state_long2abr.json', 'r') as f:
        state_long2abr = json.load(f)

    df_election["State"] = df_election["State"].map(state_short2long)
    df_election["Abbreviation"] = df_election["State"].map(state_long2abr)

    # Loading Google Trends Data
    df_GT_can_map = load_map_df("data/raw/GT_2024/GT_region_can_US_2024-10-13_2024-11-13.csv")
    df_GT_president_map = load_map_df("data/raw/GT_2024/GT_region_president_US_2024-10-13_2024-11-13.csv")

    # Combining Data
    df = df_election.join(df_GT_can_map.set_index("State"), on="State").rename(columns = {"Interest": "Interest_1"})
    df = df.join(df_GT_president_map.set_index("State"), on="State").rename(columns = {"Interest": "Interest_2"})
    df = df[["Abbreviation", "State", "Democrat", "Republican", "Interest_1", "Interest_2"]]

    df["Winner"] = df.apply(lambda x: "Republican" if x["Republican"] > x["Democrat"] else "Democrat", axis=1)

    df.to_csv("data/geo_df.csv", index=False)


def build_timeline_df():
    # The 2024 export (downloaded in November 2024) is used on purpose: it is the data the
    # original analysis was done on. It ends on 2024-11-13 because no later data existed then.
    df_GT_can_timeline = load_timeline_df("data/raw/GT_2024/GT_timeline_can_US_2024-10-13_2024-11-13.csv")
    df_GT_president_timeline = load_timeline_df("data/raw/GT_2024/GT_timeline_president_US_2024-10-13_2024-11-13.csv")

    df_timeline = df_GT_can_timeline.rename(columns={"Interest": "Interest_1"}).join(df_GT_president_timeline.set_index("Date"), on="Date").rename(columns={"Interest": "Interest_2"})

    df_timeline.to_csv("data/tl_df.csv", index=False)


# functions for loading Goggle Trends Data
# 2024 exports: 3 junk header lines ("Category: ...", blank, column header)
def load_map_df(path):
    df = pd.read_csv(path, skiprows = 3, names=['State', 'Interest'])
    return df

def load_timeline_df(path):
    df = pd.read_csv(path, skiprows = 3, names=['Date', 'Interest'])
    return df

# functions for reading tables from the web page
def read_table(table):
    rows = table.find_all("tr")
    data = []
    for row in rows:
        clmns = row.find_all("td")
        if len(clmns) >= 3:
            data.append([clmns[0].text.strip(), float(clmns[1].text[:-1]), float(clmns[2].text[:-1])])
    return data

def read_tables(tables):
    data = []
    for table in tables:
        data += read_table(table)
    return data


if __name__ == "__main__":
    main()
