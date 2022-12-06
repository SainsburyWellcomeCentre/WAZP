# Dash tutorial
# Full list of components here: https://dash.plotly.com/dash-core-components

from dash import Dash, html, dcc


app = Dash(__name__)

# First Div: dropdown, mulit-dropdown and radio items
# Second Div: checkboxes, text input, slider
app.layout = html.Div(
    [
        html.Div(
            children=[
                html.Label('Dropdown'),
                dcc.Dropdown(options=[{'label':'Albacete', 'value':'Albacete'},
                                      {'label':'Murcia', 'value':'Murcia'}, 
                                      {'label':'Soria', 'value':'Soria'}], value='Murcia'),
                html.Br(), # produces a line break in text
                html.Label('Multi-select dropdown'),
                dcc.Dropdown(options=[{'label':'Albacete', 'value':'Albacete'},
                                      {'label':'Murcia', 'value':'Murcia'}, 
                                      {'label':'Soria', 'value':'Soria'}], value=['Albacete','Murcia'], multi=True),
                html.Br(),
                html.Label('Radio items'),
                dcc.RadioItems(options=[{'label':'Albacete', 'value':'Albacete'},
                                      {'label':'Murcia', 'value':'Murcia'}, 
                                      {'label':'Soria', 'value':'Soria'}], value='Murcia')
        ], style ={'padding':10, 'flex':1}),
        html.Div(
            children=[
                html.Label('Checkboxes'),
                dcc.Checklist(options=[{'label':'Albacete', 'value':'Albacete'},
                                       {'label':'Murcia', 'value':'Murcia'}, 
                                       {'label':'Soria', 'value':'Soria'}], value=['Soria']),
                html.Br(),
                html.Label('Text input'),
                dcc.Input(value='MTL', type='text'),
                dcc.Slider(min=0, max=9, marks={i: f'Label {i}' if i==0 else f'{i}' for i in range(10)})
            ]
        )
    ]

)

if __name__=='__main__':
    app.run_server(debug=True)