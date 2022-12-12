import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1(children='This is the Home page'),

    html.Div(children='''
        This is the Home page content.
    '''),

])