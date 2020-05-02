# plotly figures
from visualization.comparison import *
from visualization.basic import *

# validation and file loading
from data import RussianRegionsParser
from models.validation import get_validation_results
import pandas as pd
import json

# dash framework
import flask
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# MAIN PARAMETERS ################
# Основные параметры
predictions = [
    pd.read_csv(".submissions/seir3.csv"),
    pd.read_csv(".submissions/seir2.csv"),
]
team_names = ["Gork", "Mork"]
start_date = "2020-04-27"
end_date = "2020-05-01"
##################################

# dash with flask
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)


# configuring our data parser
# конфигурация для парсера регионов - все файлы уже на месте
cfg_aux = {
    "regions": "./auxiliary_files/russia_regions.csv",
    "geojson": "./auxiliary_files/gadm36_RUS_1.json",
}
cfg_main = {
    "rospotreb_page": "https://www.rospotrebnadzor.ru/",
    "timeseries_page": "https://github.com/grwlf/COVID-19_plus_Russia/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_RU.csv",
    "rewrite": True,
    "root": "./",
}
parser = RussianRegionsParser({"rospotreb": cfg_main, "auxiliary": cfg_aux})


# getting our data
# загружаем свежие данные роспотребнадзора + общие данные по регионам
with open("./auxiliary_files/gadm36_RUS_1.json") as f:
    geodata = json.load(f)
summary = pd.read_csv("./auxiliary_files/russia_regions.csv").set_index("iso_code")
data = parser.load_data()

# evaluating the male scores
# выводим все скоры в одну таблицу, в другой оставляем только сам лидерборд
scores = get_validation_results(
    predictions, data, start_date, end_date, summary, custom_ids=team_names
)
lb = scores.reset_index().groupby("region_code").sum().mean().reset_index()
lb.columns = ["Participant", "Score"]
lb = lb.sort_values(by="Score").reset_index()
lb["index"] = lb["index"] + 1


# rendering the dash app
# отрисовываем то, что будет отображаться на сервере
app.layout = html.Div(
    [
        html.Div(
            [
                # header
                # шапка с обшей информацией
                html.H1("Leaderboard"),
                html.P(
                    f"Evaluating different forecasting techniques by predicting \
                the date range of {start_date} - {end_date}"
                ),
                html.P(
                    "Select participant id to update map and pie charts. \
                Click on a country region to display predictions."
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                # leaderboard table with simple scores graph
                # таблица лидеров и простенький график ошибок с линиями
                html.Div(
                    [
                        html.H3("Ratings table"),
                        html.P("User ratings are displayed here. Sum of \
                            Mean Absolute Log Errors by day."),
                        dash_table.DataTable(
                            id="leaderboard",
                            columns=[{"name": i, "id": i} for i in lb.columns],
                            data=lb.to_dict("records"),
                            page_size=8,
                        ),
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(
                            figure=plot_simple_difference(
                                scores,
                                group="date",
                                graph_type="scatter",
                                cumulative=True,
                            )
                        )
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                # regions map with dropdown menu
                # интерактивная карта регионов с меню выбора команды-участника
                html.Div(
                    [
                        html.H3("Region map"),
                        html.P("Regions are clickable."),
                        dcc.Graph(
                            id="region-map",
                            figure=plot_errors(
                                scores,
                                summary,
                                graph_type="map",
                                geodata=geodata,
                                height=300,
                            ),
                        ),
                    ],
                    className="ten columns",
                ),
                html.Div(
                    [
                        html.H3("Participant"),
                        dcc.Dropdown(
                            id="team-choice",
                            options=[{"label": x, "value": x} for x in team_names],
                        ),
                    ],
                    className="two columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                # pie graph for error shares and prediction scatter
                # граф с долями ошибок по регионам и сами предсказания
                html.Div(
                    [
                        dcc.Graph(
                            id="region-pie",
                            figure=plot_errors(scores, summary, graph_type="pie"),
                        )
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="region-preds",
                            figure=plot_predictions(predictions, team_names, data),
                        )
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
    ]
)

# updating the pie graph by the dropdown menu value
# обновляем доли ошибок по регионам для выбранного участника
@app.callback(Output("region-pie", "figure"), [Input("team-choice", "value")])
def update_pie(value):
    fig_pie = plot_errors(scores, summary, source_id=value, graph_type="pie")
    return fig_pie


# updating the map to show participant's scores
# обновляем скоры ошибок регионов на карте для выбранного участника
@app.callback(Output("region-map", "figure"), [Input("team-choice", "value")])
def update_map(value):
    fig_map = plot_errors(
        scores, summary, source_id=value, graph_type="map", geodata=geodata, height=300
    )
    return fig_map


# updating the region view to selected region
# обновляем предсказания по регионам для выбранного региона
@app.callback(Output("region-preds", "figure"), [Input("region-map", "clickData")])
def update_region(click_data):
    try:
        loc = click_data["points"][0]["location"]
        loc = summary[summary["geoname_code"] == loc].index[0]
        return plot_predictions(predictions, team_names, data, value=loc)
    except TypeError:
        return plot_predictions(predictions, team_names, data)


# Running the server
if __name__ == "__main__":
    # debug=True for debugging and use_reloader=False for
    # serving right out of a jupyter notebook
    # app.run_server(debug=True, use_reloader=False)
    app.run_server()
