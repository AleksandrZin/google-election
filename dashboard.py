from flask import Flask
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc

import src.utils as utils

states, geo_df, tl_df = utils.load_all_data()
# Create dashboard
server = Flask(__name__)
app = Dash(name=__name__, server=server)
app.title = 'Election Dashboard'

# === DASHBOARD COMPONENTS ===
# Inputs
radio_buttons_style = {
    'width': "70%",
    'margin': '0 auto',
    'min-width': '300px',
    'max-width': '400px'
}
radio_header_class = 'text-primary text-center fs-4'
vertical_step_style = {'margin-top': '15px'}
center_object_style = {'margin-left': 'auto', 'margin-right': 'auto'}
right_step_style = {'margin-left': '30px'}

interest_input = [
    html.Div('Search Request:', className=radio_header_class),
    dbc.RadioItems(options=[{
        'label': 'Can I change my vote?',
        'value': 'Interest_1'
    }, {
        'label': 'Change vote presidential election',
        'value': 'Interest_2'
    }],
                   value='Interest_1',
                   style=radio_buttons_style,
                   id="result_tab_interest")
]

vote_input = [
    html.Div('Party:', className=radio_header_class),
    dbc.RadioItems(options=[{
        'label': 'Votes for Democrat, %',
        'value': 'Democrat'
    }, {
        'label': 'Votes for Republican, %',
        'value': 'Republican'
    }],
                   value='Democrat',
                   style=radio_buttons_style,
                   id="result_tab_vote")
]

map_input = html.Div(
    [
        dbc.RadioItems(id="map_input",
                       className="btn-group",
                       inputClassName="btn-check",
                       labelClassName="btn btn-outline-primary",
                       labelCheckedClassName="active",
                       options=[{
                           "label": "Search Term 1",
                           "value": "Interest_1"
                       }, {
                           "label": "Search Term 2",
                           "value": "Interest_2"
                       }, {
                           "label": "Votes for Democrat, %",
                           "value": "Democrat"
                       }, {
                           "label": "Votes for Republican, %",
                           "value": "Republican"
                       }],
                       value="Interest_1",
                       style=vertical_step_style | right_step_style),
    ],
    className="radio-group",
)


# Timeline tab
def timeline_tab():
    big_text = '''
    On November 5th 2024 the US presidential election took place. 
    Directly after it Google Trends show an increase of searches regarding a possibility of the vote change.
    Did search trends differ between red and blue states post-election? 
    We analyzed the popularity of two search terms: 'Can I change my vote?' (Search Term 1) and 'Change vote presidential election.' (Search Term 2)
    '''
    small_text = '''
    Interest in Google Trends represents the relative popularity of a term. 
    A score of 100 signifies the peak popularity during the time range.
    The data was downloaded in November 2024, so the timeline ends on November 13th, the latest day available at the time.
    '''
    child = dbc.Container([
        dbc.Row(
            dbc.Col([
                html.P(big_text, className='fs-5 text-center'),
                html.P(small_text, className='text-center')
            ],
                    lg=10,
                    md=12,
                    className='mx-auto')),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=utils.create_timeline_plot(),
                              style={
                                  'width': '100%',
                                  'height': '70vh',
                                  'min-hight': '400px',
                                  'min-width': '500px'
                              }),
                    className='mx-auto'))
    ],
                          style=vertical_step_style)
    return child


# Map tab
def map_tab():
    child = [
        html.P([
            html.Span("Search Term 1: ", className="text-primary fw-bolder"),
            "'Can I change my vote?'"
        ],
               style=vertical_step_style | right_step_style),
        html.P([
            html.Span("Search Term 2: ", className="text-primary fw-bolder"),
            "'Change vote presidential election.'"
        ],
               style=right_step_style), map_input,
        dbc.Container(dbc.Row(dbc.Col(
            dcc.Graph(id="map_graph",
                      style={
                          'height': '80vh',
                          'min-hight': '400px',
                          'min-width': '500px'
                      }),
            lg=10,
            md=12,
            align='center',
            className='mx-auto',
        ),
                              align='center'),
                      fluid=True)
    ]
    return child


QUESTION_LABELS = {
    "Interest_1": "Can I change my vote?",
    "Interest_2": "Change vote presidential election",
}


# Plain-language explanation of the results (collapsed by default).
# The body is filled in by result_tab_update so it matches the selected search term.
def plain_language_note():
    return dbc.Accordion(
        dbc.AccordionItem(html.Div(id="plain_language_note"),
                          title="What does this mean in plain words?"),
        start_collapsed=True,
        style=vertical_step_style)


def plain_language_text(question, pvalue, avg_dem, avg_rep):
    term = QUESTION_LABELS[question]
    sizes = utils.group_stats(question)["count"]
    n_dem, n_rep = sizes.get("Democrat", 0), sizes.get("Republican", 0)

    if round(avg_dem) == round(avg_rep):
        comparison = (f"red and blue states searched \"{term}\" about equally on average "
                      f"({avg_rep:.0f} vs {avg_dem:.0f}). ")
    elif avg_rep > avg_dem:
        comparison = (f"red states searched \"{term}\" more on average than blue states "
                      f"({avg_rep:.0f} vs {avg_dem:.0f}). ")
    else:
        comparison = (f"blue states searched \"{term}\" more on average than red states "
                      f"({avg_dem:.0f} vs {avg_rep:.0f}). ")
    comparison = comparison[0].upper() + comparison[1:]

    if pvalue > 0.05:
        heading = "The difference could be chance. "
        meaning = (
            "A difference this size could plausibly appear by chance, so we can't say red and "
            "blue states really searched differently. This also doesn't prove they searched the "
            f"same way. With only {n_dem} blue and {n_rep} red states, the test can miss small real "
            "differences. ")
    else:
        heading = "The difference is unlikely to be chance. "
        meaning = (
            "A difference this large would be unlikely if red and blue states really searched "
            "the same way. It doesn't tell us why they differ. ")
    return html.P([
        html.Strong(heading), comparison, meaning,
        "See the Caveats tab for more on the limits of this analysis."
    ], className="mb-0")


def describe_missing(question):
    missing = utils.missing_regions(question)
    if not missing:
        return "none"
    states = [s for s in missing if s != "District of Columbia"]
    parts = []
    if states:
        parts.append(f"{len(states)} state{'s' if len(states) != 1 else ''} "
                     f"({', '.join(sorted(states))})")
    if "District of Columbia" in missing:
        parts.append("the District of Columbia")
    return " and ".join(parts)


# Caveats tab: limitations and nuances of the research
def caveats_tab():
    sizes_1 = utils.group_stats("Interest_1")["count"]
    spread_2 = utils.group_stats("Interest_2")["std"]
    points = [
        [html.Strong("The scores are relative, not counts. "),
         "Google Trends rates each state from 0 to 100 by how popular a search was there "
         "compared with all searches in that state. A big state like California doesn't "
         "score higher just because more people live there."],
        [html.Strong("Some states are missing. "),
         "Where there were too few searches, Google doesn't report a score, so those states "
         "aren't included. Search Term 1: " + describe_missing("Interest_1") + ". "
         "Search Term 2: " + describe_missing("Interest_2") + "."],
        [html.Strong("The data is a snapshot from November 2024. "),
         "The search data covers October 13th to November 13th 2024 and was downloaded in "
         "November 2024, so it ends there. Interest in \"Can I change my vote?\" was still near "
         "its peak on the last day, so we don't see when it faded."],
        [html.Strong("Google Trends numbers change on re-download. "),
         "Google builds them from a sample of searches, so downloading the same query again "
         "gives somewhat different numbers, especially for rare searches."],
        [html.Strong("The two search terms aren't on the same scale. "),
         "Each term was downloaded separately and scaled to its own peak of 100, so a score of "
         "50 for one term can't be compared with 50 for the other."],
        [html.Strong("Vote figures may not be final. "),
         "Vote shares were collected from Reuters' results page and may differ slightly from "
         "the final certified results, that where not available."],
    ]
    analysis_points = [
        [html.Strong("A state's color doesn't tell us who searched. "),
         "Every state has voters from both parties, so a search from a red state could have "
         "come from a Democrat, and the other way round."],
        [html.Strong("Searching isn't necessarily regretting. "),
         "People search these phrases out of curiosity, because of news or social media posts, "
         "or to check the rules. A search doesn't necessarily mean someone wanted to change their vote."],
        [html.Strong("Correlation, not cause. "),
         "Even if red and blue states did search differently, this analysis couldn't say why."],
        [html.Strong("Why Welch's t-test. "),
         f"The red and blue groups differ in size (for Search Term 1, "
         f"{sizes_1.get('Republican', 0)} red vs {sizes_1.get('Democrat', 0)} blue states), "
         f"and their scores can be spread out differently (for Search Term 2, a standard "
         f"deviation of {spread_2.get('Democrat', float('nan')):.1f} in blue states vs "
         f"{spread_2.get('Republican', float('nan')):.1f} in red states). Welch's "
         "t-test doesn't assume both groups are equally spread, so it suits this data better "
         "than the standard t-test."],
    ]

    def bullet_list(items):
        return html.Ul([html.Li(p, className="mb-2") for p in items], className="fs-5")

    return dbc.Container(dbc.Row(dbc.Col([
        html.H4("About the data", className="text-primary"),
        bullet_list(points),
        html.H4("About the analysis", className="text-primary"),
        bullet_list(analysis_points),
    ], lg=8, md=12, className="mx-auto")),
                         style=vertical_step_style)


# Result tub
def result_tub():
    child = dbc.Container([
        dbc.Row([
            dbc.Col(interest_input, md=12, lg=6),
            dbc.Col(vote_input, md=12, lg=6)
        ]),
        dbc.Row(
            html.Div(id="result_tab_markdown",
                     className="fs-4 text-center",
                     style=vertical_step_style)),
        dbc.Row(dbc.Col(plain_language_note(), lg=8, md=12,
                        className="mx-auto")),
        dbc.Row([
            dbc.Col(dcc.Graph(id="scatter_graph"), lg=6, md=12),
            dbc.Col(dcc.Graph(id="box_graph"), lg=6, md=12)
        ], )
    ],
                          fluid=True)
    return child


# === MAIN LAYOUT ===
app.layout = dbc.Container([
    dbc.Row([
        html.Div('Post-Election Search Trends: Can Voters Change Their Minds?',
                 className="text-primary text-center fs-2",
                 style={'margin': '10px auto'})
    ]),
    dbc.Tabs([
        dbc.Tab(label="Timeline", children=timeline_tab()),
        dbc.Tab(label="Map", children=map_tab()),
        dbc.Tab(label="Result", children=result_tub()),
        dbc.Tab(label="Caveats", children=caveats_tab())
    ])
])


# === DASHBOARD INTERACTIVITY ===
# Map Update
@callback(Output("map_graph", "figure"), Input("map_input", "value"))
def map_tab_update(column):
    fig = utils.create_map_plot(column)
    return fig


# Result Update
@callback(Output("scatter_graph", "figure"), Output("box_graph", "figure"),
          Output("result_tab_markdown", "children"),
          Output("plain_language_note", "children"),
          Input("result_tab_interest", "value"),
          Input("result_tab_vote", "value"))
def result_tab_update(question, party):
    scatter_fig = utils.create_scatter_plot(party, question)
    box_fig = utils.create_box_plot(question)

    stats, avg_dem_int, avg_rep_int = utils.welch_ttest(question)
    div = html.Div(
        [
            html.P([
                "Average Interest in Blue States: ",
                html.Span(f"{avg_dem_int:.2f}",
                          className='text-info fw-bolder')
            ]),
            html.P([
                "Average Interest in Red States: ",
                html.Span(f"{avg_rep_int:.2f}",
                          className='text-danger fw-bolder')
            ]),
            html.P([
                "We tested the null hypothesis that the two samples have identical average values using Welch's t-test, which does not assume equal variances."
                # html.Span("Null hypothesis: ", className='fw-bold'),
                # "2 independent samples have identical average values. Identical variance of the populations is assumed."
            ]),
            html.P([
                "The p-value is the probability of seeing a difference in averages at least this large if red and blue states actually had the same average interest. "
                "If it is above 0.05, the observed difference could plausibly be due to chance, so we cannot conclude that a real difference exists, though this does not prove there is none."
            ]),
            html.P([
                "p-value: ",
                html.Span(f"{stats.pvalue:.3f}", className=" fw-bolder")
            ]),
            conclusion_div(stats.pvalue)
        ],
        className='fs-4')
    note = plain_language_text(question, stats.pvalue, avg_dem_int, avg_rep_int)
    return (scatter_fig, box_fig, div, note)


def conclusion_div(pvalue):
    significant = pvalue <= 0.05
    return html.P([
        html.Span("Conclusion: ", className="fw-bolder"),
        "The difference in average search interest between red and blue states ",
        html.Span("is " if significant else "is not ", className='fw-bold'),
        "statistically significant ",
        f"(p {'≤' if significant else '>'} 0.05)."
    ])


# Start the Dash server
if __name__ == "__main__":
    server.run(debug=True)
    # add host='0.0.0.0' to have access to the webpage on local network
