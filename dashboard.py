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
    On November 5th 2025 the US presidential election took place. 
    Directly after it Google Trends show an increase of searches regarding a possibility of the vote change.
    Did search trends differ between red and blue states post-election? 
    We analyzed the popularity of two search terms: 'Can I change my vote?' (Search Term 1) and 'Change vote presidential election.' (Search Term 2)
    '''
    small_text = '''
    Interest in Google Trends represents the relative popularity of a term. 
    A score of 100 signifies the peak popularity during the time range.
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
        dbc.Tab(label="Result", children=result_tub())
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
          Input("result_tab_interest", "value"),
          Input("result_tab_vote", "value"))
def result_tab_update(question, party):
    scatter_fig = utils.create_scatter_plot(party, question)
    box_fig = utils.create_box_plot(question)

    stats, avg_dem_int, avg_rep_int = utils.ttest(question)
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
                "We tested the null hypothesis that the two samples have identical average values, assuming equal variances."
                # html.Span("Null hypothesis: ", className='fw-bold'),
                # "2 independent samples have identical average values. Identical variance of the populations is assumed."
            ]),
            html.P([
                "If p-value is bigger than 0.05 there is a good probability, that the difference in average, that we observed, occurred by chance."
            ]),
            html.P([
                "p-value: ",
                html.Span(f"{stats.pvalue:.3f}", className=" fw-bolder")
            ]),
            conclusion_div(stats.pvalue)
        ],
        className='fs-4')
    return (scatter_fig, box_fig, div)


def conclusion_div(pvalue):
    if pvalue > 0.05:
        return html.P([
            html.Span("Conclusion: ", className="fw-bolder"), "There is ",
            html.Span("no ", className='fw-bold'),
            "statistically significant reason to assume the difference in Google searches between red and blue states."
        ])
    else:
        return html.P([
            html.Span("Conclusion: ", className="fw-bolder"), "There ",
            html.Span("is ", className='fw-bold'),
            "statistically significant reason to assume the difference in Google searches between red and blue states."
        ])


# Start the Dash server
if __name__ == "__main__":
    server.run(debug=True)
    # add host='0.0.0.0' to have access to the webpage on local network
