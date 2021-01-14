"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import plotly.express as px
import pymongo
import numpy as np
from pymongo import MongoClient
import pandas as pd

import imdb
import datetime

from functions import *


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

cluster = MongoClient("mongodb+srv://Client:1234@cluster0.big8l.mongodb.net/Filmy?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs='CERT_NONE')
db = cluster["Filmy"]
ia = imdb.IMDb()


#---------------------------------------   CSS    --------------------------------------- 

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "3rem 2rem",
    #"background-color": "#f8f9fa",
    #"border" : "3px",
    #"border-color" : '#000000',
    "border":"2px #B149FA solid",
}




# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "3rem 1rem",
}




#---------------------------------------   Data    --------------------------------------- 


films = db.list_collection_names()
df_list = get_dataframe2(films,db)
rated_outputs_list = rating_calculator(df_list, films)

updated_dataframes = []
film_ratings = []

for n in rated_outputs_list:
    updated_dataframes.append(n[2])
    film_name = n[0]
    rejting = n[1]
    rejt_couple = [film_name, rejting]
    film_ratings.append(rejt_couple)

leaderbords_df = get_leaderboards_dataframe(film_ratings)

fav_section_list = get_favourite_section(updated_dataframes, films)
dominant_emotion_list = get_predominant_emotion(updated_dataframes, films)

imdb_dat_list = []
for n in films:
    imdb_data = get_imdb_score(n)
    imdb_dat_list.append(imdb_data)

avg_movement_list = get_average_movement(updated_dataframes,films)
distraction_time_list = get_distraction_time(updated_dataframes, films)

total_runtime = get_total_watchtime(updated_dataframes,films)
average_rating = get_average_rating(film_ratings)

#films = ["lalaland","twin_peaks","bromhilda"]
links = []
film_paths = []
film_tag_list = []
for film in films:
    film_path = str("/"+film)
    film_paths.append(film_path)
    film_tag = film.replace('_',' ')
    film_tag = film_tag.title()
    film_tag_list.append(film_tag)
    link = dbc.NavLink(film_tag, href=str("/"+film), active="exact", )
    
    links.append(link)
homelink = dbc.NavLink('Home', href=str("/"), active="exact", )
links.insert(0,homelink)
#print(links)

#for k in fi


#---------------------------------------   Functions    --------------------------------------- 

def card_func(name_of_film):
    for z in film_ratings:
        if z[0] == name_of_film:
            relevant_rating = z[1]

    for e in fav_section_list:
        if e[0] == name_of_film:
            relevant_start_time = e[1]
            relevant_lines = e[2]

    processed_relevant_lines = ""
    relevant_processing_lines = relevant_lines
    relevant_lines = list(dict.fromkeys(relevant_lines))

    for t in range(len(relevant_lines)):

        if relevant_lines[t] == 0:
            None
        else:
            processed_relevant_lines += str(relevant_lines[t])
    processed_relevant_lines = processed_relevant_lines.replace('<i>', '')
    processed_relevant_lines = processed_relevant_lines.replace('</i>',' ')

    for u in imdb_dat_list:
        if u[0] == name_of_film:
            relevant_imdb_rating = u[1]
            relevant_director = u[2]
            relevant_actors = u[3]
            relevant_link = u[4]
    
    
    
    #rating = dbc.Card(
    rating_content = dbc.CardBody(
            [
                html.H5('Your Rating', className="card-title"),
                html.H1(int(relevant_rating), className="card-subtitle"),
                html.P(),
                html.P(
                    "As calculated based on your expressions and movement while watching.",
                    className="card-text",
                ),
                
            ],
            
        ),
    #    style={"width": "18rem", "height" : "15rem", "color":"secondary"},
    #)

    rating = dbc.Card(rating_content, color="#09FE9E", outline=True, style={"width": "12rem", "height" : "15rem",}, className="greencard"),

    #fav_section = dbc.Card(
    fav_section_content = dbc.CardBody(
            [
                html.H5('Favourite Section', className="card-title"),
                html.H1('{} - {}'.format((datetime.timedelta(seconds = relevant_start_time)), (datetime.timedelta(seconds = relevant_start_time + 20))), className="card-subtitle"),
                html.P(),
                html.P(
                    processed_relevant_lines,
                    className="card-text",
                ),
                
            ]
        ),
    #    style={"width": "41rem", "height" : "15rem"},
    #)
    fav_section = dbc.Card(fav_section_content,  outline=True, style={"width": "41rem", "height" : "15rem"},className="greenoutline"),

    #imdb_data = dbc.Card(
    imdb_data_content = dbc.CardBody(
            [
                html.H5('IMDb Rating', className="card-title"),
                html.H1(relevant_imdb_rating, className="card-subtitle"),
                html.P(),
                html.P(dcc.Markdown(
                    '''**Directed by:** {}  // **Cast:** {}'''.format(relevant_director, relevant_actors),
                    className="card-text",
                )),
                #html.P(
                #    relevant_actors,
                #    className="card-text",
                #),
                
                dbc.CardLink("IMDb link", href= relevant_link),
            ]
        ),
    #    style={"width": "24rem", "height" : "15rem"},
    #)
    imdb_data = dbc.Card(imdb_data_content,  outline=True, style={"width": "24rem", "height" : "15rem"},className="greenoutline"),

    card = html.Div([
        dbc.Row([dbc.Col(rating,),
                 dbc.Col(fav_section,),
                 dbc.Col(imdb_data,),
        ],
        style={"margin-top": "2rem", }, 
        )
    ])
    return card


def graph_1(name_of_film):
    index = films.index(name_of_film)
    chosen_df = updated_dataframes[index]

    for q in dominant_emotion_list:
        if q[0] == name_of_film:
            relevant_dominant_emotions = q[1]

    for b in avg_movement_list:
        if b[0] == name_of_film:
            relevant_avg_movement = b[1]
        else:
            None

    for v in distraction_time_list:
        if v[0] == name_of_film:
            relevant_distraction_time = v[1]
        else:
            None

    #title_line = html.H1(film_tag)
    
    #dominant_emotion_card = dbc.Card(
    dominant_emotion_content = dbc.CardBody(
            [
                html.H5('Predominant Emotions', className="card-title"),
                html.H1("1.{}".format(relevant_dominant_emotions[0]), className="card-title"),
                html.H1("2.{}".format(relevant_dominant_emotions[1]), className="card-subtitle"),
                html.H1("3.{}".format(relevant_dominant_emotions[2]), className="card-sub-subtitle"),
                html.P(),
                html.P(
                    "As calculated based on your expressions and movement while watching.",
                    className="card-text",
                ),
                #dbc.CardLink("Card link", href="#"),
                #dbc.CardLink("External link", href="https://google.com"),
            ]
        ),
    #    style={"width": "18rem", "height" : "30rem"},
    #)
    dominant_emotion_card = dbc.Card(dominant_emotion_content, outline=True, style={"width": "18rem", "height" : "30rem"}, className="greencard"),

    #average_movement_card = dbc.Card(
    average_movement_content = dbc.CardBody(
            [
                html.H5('Distracted Time', className="card-title"),
                html.H1('{}'.format((datetime.timedelta(seconds = relevant_distraction_time))), className="card-subtitle"),
                #html.H4(relevant_distraction_time, className="card-title"),
                html.P('  '),
                html.P('  '),
                html.H5('Average Movement', className="card-title"),
                html.H1(round(relevant_avg_movement, 2), className="card-subtitle"),
                #html.H6(relevant_dominant_emotions[2], className="card-sub-subtitle"),
                html.P('  '),
                html.P('  '),
                html.P('  '),
                html.P('  '),
                html.P(
                    "Both distraction and movement influence your film rating.",
                    className="card-text",
                ),
                #dbc.CardLink("Card link", href="#"),
                #dbc.CardLink("External link", href="https://google.com"),
            ]
        ),
    #    style={"width": "18rem", "height" : "30rem"},
    #)
    average_movement_card = dbc.Card(average_movement_content, outline=True, style={"width": "18rem", "height" : "30rem"},className="greencard"),

    #----------------------- Graph1------------
    fig = px.scatter(chosen_df, x="timestamp", y="emotions", color = 'rating_seconds',
                title=str('Emotion Through Film'),
                 hover_name="text", log_x=False, size_max=150).update_layout(showlegend=True, title_x=0.5)

    card_graph = dbc.Card(
        dcc.Graph(
            id='my_bar', figure= fig), 
            body=True,  
            style={"width": "61rem", "height" : "30rem"}, className="blackoutline",
        ),
        

    #-------------------------Graph2----------
    fig2 = px.line(chosen_df, x="timestamp", y="movement", 
               hover_name="text")
    
    card_graph2 = dbc.Card(
        dcc.Graph(
            id='my_bar', figure= fig2), body=True,  
            style={"width": "61rem", "height" : "30rem"}, className="blackoutline",
        ),

    #------------------------ Graph3 -------------
    fig3 = px.bar(leaderbords_df, x='name', y='rating', title='Your Favourite Films', 
             hover_data=['rating'],  
             )

    card_graph3 = dbc.Card(
        dcc.Graph(
            id='my_bar', figure= fig3), body=True, className="blackoutline", 
            style={"width": "29rem", "height" : "30rem"},
        )

    #------------------------Graph4-----------------
    fig4 = px.scatter(chosen_df, x="timestamp", y="rating_seconds", color = 'emotions',
                  title=str('Amount of Enjoyment'),
                 hover_name="text", log_x=False, size_max=150).update_layout(showlegend=False, title_x=0.5)

    card_graph4 = dbc.Card(
        dcc.Graph(
            id='my_bar', figure= fig4), body=True, className="blackoutline",
            style={"width": "50rem", "height" : "30rem"},
        )

    data_body = html.Div([
        dbc.Row([dbc.Col(card_graph,),
                 dbc.Col(dominant_emotion_card,)
             ],
             style={"margin-top": "2rem", }, 
            ),
        dbc.Row([dbc.Col(average_movement_card,), 
                dbc.Col(card_graph2,),
             ],
             style={"margin-top": "2rem",}, 
            ),
        dbc.Row([dbc.Col(card_graph4,),
                 dbc.Col(card_graph3)
             
             ],
             style={"margin-top": "2rem",}, 
             ),
    ])

    #graph_card_1 = html.Div(card_graph)
    return data_body 


def homepage():

    total_run_time_content = dbc.CardBody(
        [
            html.H5('Total Time Watched', className="card-title"),
            html.H1('{}'.format((datetime.timedelta(seconds = total_runtime))), className="card-subtitle"),
            html.P(),
            html.P(
                "Altogether you have watched {} minutes of film." .format(int(total_runtime/60)),
                className="card-text",
            ),
            
        ],
        
    ),
    #    style={"width": "18rem", "height" : "15rem", "color":"secondary"},
    #)

    total_run_time = dbc.Card(total_run_time_content, color="#09FE9E", outline=True, style={"width": "18rem", "height" : "15rem",}, className="blackcard"),

    average_rating_content = dbc.CardBody(
        [
            html.H5('Average Rating', className="card-title"),
            html.H1(int(average_rating), className="card-subtitle"),
            html.P(),
            html.P(
                "Your average rating for a film is {}" .format(average_rating),
                className="card-text",
            ),
            
        ],
        
    ),
    #    style={"width": "18rem", "height" : "15rem", "color":"secondary"},
    #)

    average_rating_card = dbc.Card(average_rating_content, color="#09FE9E", outline=True, style={"width": "18rem", "height" : "15rem",}, className="blackcard"),
    
    fig5 = px.bar(leaderbords_df, x='name', y='rating', title='Your Favourite Films', 
             hover_data=['rating'],  
             )

    card_graph5 = dbc.Card(
        dcc.Graph(
            id='my_bar', figure= fig5), body=True, className="blackoutline", 
            style={"width": "61rem", "height" : "31rem"},
        )

    graph_body = html.Div([
        dbc.Row(
            [dbc.Col(card_graph5,),     
             dbc.Col([
                dbc.Row(total_run_time),
                dbc.Row(average_rating_card, style={"margin-top": "1rem",}, ),


                ])
            
            ],
             style={"margin-top": "2rem",}, 
             ),
    ])

    #graph_card_1 = html.Div(card_graph)
    return graph_body




#---------------------------------------   HTML    --------------------------------------- 

sidebar = html.Div(
    [
        html.H1("My Films", className="side-title" ),
        html.Hr(className="side-line"),
        html.P(
            "Pick a logged film to show", #className="lead"
        ),
        dbc.Nav(
                links
            ,
            vertical=True,
            pills=True,
            #style=BUTTON_STYLE,
        ),
    ],
    style=SIDEBAR_STYLE,
)


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])




@app.callback(Output("page-content", "children",), [Input("url", "pathname")])
def render_page_content(pathname):
    
    if pathname in film_paths:
        chosen_film = pathname.replace('/', '')
        tag_index = films.index(chosen_film)
        relevant_tag = film_tag_list[tag_index]
        pathname = ''
        return html.Div(
            [
                html.H1(relevant_tag), 
                card_func(chosen_film), 
                graph_1(chosen_film),
            ]
        )
    elif pathname == "/":
        chosen_film = ''
        tag_index = None
        relevant_tag = ''
        pathname = ''

        return html.Div(
            [
                html.H1("Choose one of your films."), 
                homepage(), 
            ]
        )


    elif pathname == "":
        return html.H1("Choose one of your films.")
    #elif pathname == "/page-1":
    #    return html.P("This is the content of page 1. Yay!")
    #elif pathname == "/page-2":
    #    return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message

    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8888)