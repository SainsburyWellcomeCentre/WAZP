# Dash tutorial

from dash import Dash, html, dcc


markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses [CommonMark](http://commonmark.org/), check out their [60 seconds tutorial](http://commonmark.org/help/)
*whoop whoop* 
'''

# initialise app
app = Dash(__name__)

# define layout
app.layout = html.Div([
    dcc.Markdown(children=markdown_text)
]) # Div is an html element that is a generic container for flow content, used to group content so that it can be styled easily

if __name__ == '__main__':
    app.run_server(debug=True)