from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json

def main():
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
    df_GT_can_map = load_map_df("data/raw/GT_map_can.csv")
    df_GT_president_map = load_map_df("data/raw/GT_map_president.csv")

    df_GT_can_timeline = load_timeline_df("data/raw/GT_timeline_can.csv")
    df_GT_president_timeline = load_timeline_df("data/raw/GT_timeline_president.csv")

    # Combining Data
    # Geographic Data
    df = df_election.join(df_GT_can_map.set_index("State"), on="State").rename(columns = {"Interest": "Interest_1"})
    df = df.join(df_GT_president_map.set_index("State"), on="State").rename(columns = {"Interest": "Interest_2"})
    df = df[["Abbreviation", "State", "Democrat", "Republican", "Interest_1", "Interest_2"]]

    df["Winner"] = df.apply(lambda x: "Republican" if x["Republican"] > x["Democrat"] else "Democrat", axis=1)
    # Time Series Data
    df_timeline = df_GT_can_timeline.rename(columns={"Interest": "Interest_1"}).join(df_GT_president_timeline.set_index("Date"), on="Date").rename(columns={"Interest": "Interest_2"})

    # Save Data
    df.to_csv("data/geo_df.csv", index=False)
    df_timeline.to_csv("data/tl_df.csv", index=False)

# functions for loading Goggle Trends Data
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