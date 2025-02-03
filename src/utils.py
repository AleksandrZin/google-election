import pandas as pd
import numpy as np
import json
import plotly.express as px
from scipy import stats


# Loading data
def load_all_data():
    # Loading data
    # Loading   GeoJSON files for the map plot
    with open('data/us-states.json') as f:
        states = json.load(f)

    geo_df = pd.read_csv("data/geo_df.csv")
    tl_df = pd.read_csv("data/tl_df.csv")

    tl_df = tl_df.melt(id_vars=['Date']).rename(columns={
        'variable': 'Question',
        'value': 'Interest'
    })
    return (states, geo_df, tl_df)


states, geo_df, tl_df = load_all_data()


# Creating plots
def create_timeline_plot():
    fig = px.line(tl_df,
                  x="Date",
                  y="Interest",
                  color="Question",
                  color_discrete_map={
                      "Interest_1": "#42dcc4",
                      "Interest_2": "#42DC77"
                  },
                  markers=True).add_vline(
                      x='2024-11-05',
                      line_dash="dash",
                  )
    fig.update_layout(legend=dict(orientation="h",
                                  yanchor="bottom",
                                  y=1.02,
                                  xanchor="right",
                                  x=1),
                      legend_title_text='Search term')

    new_names = {
        "Interest_1": "can i change my vote",
        "Interest_2": "change vote presidential election"
    }
    fig.for_each_trace(lambda t: t.update(name=new_names[t.name],
                                          legendgroup=new_names[t.name],
                                          hovertemplate=t.hovertemplate.
                                          replace(t.name, new_names[t.name])))
    return fig


def create_map_plot(column):
    if column == 'Democrat':
        color_scale = 'blues'
    elif column == 'Republican':
        color_scale = 'reds'
    elif column in ['Interest_1', 'Interest_2']:
        color_scale = 'mint'
    return px.choropleth_map(geo_df,
                             geojson=states,
                             locations='Abbreviation',
                             color=column,
                             map_style='carto-positron',
                             color_continuous_scale=color_scale,
                             range_color=(0, 100),
                             center={
                                 "lat": 42,
                                 "lon": -120
                             },
                             zoom=2.5,
                             opacity=0.6)


def create_scatter_plot(party, question):
    return px.scatter(geo_df,
                      x=party,
                      y=question,
                      color='Winner',
                      hover_data=['State', party, question]).update_layout(
                          showlegend=False,
                          xaxis_range=[0, 100],
                          yaxis_range=[0, 105],
                          yaxis_title="Interest",
                          xaxis_title=f"Votes for {party}, %")


def create_box_plot(question):
    return px.box(geo_df, x="Winner", y=question,
                  color="Winner").update_layout(showlegend=False,
                                                yaxis_title="Interest",
                                                xaxis_title="State's Winner")


# t-test
def ttest(question):
    int_dem = geo_df[geo_df.Winner == "Democrat"][question].dropna()
    int_rep = geo_df[geo_df.Winner == "Republican"][question].dropna()

    return (stats.ttest_ind(int_dem,
                            int_rep), np.mean(int_dem), np.mean(int_rep))
