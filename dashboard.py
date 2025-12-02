import json

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load JSON file into a DataFrame
with open('mtcms-prod-response.json') as f:
    data = json.load(f)


# Load JSON file into a DataFrame
with open('mtcms-stag-response.json') as f:
    data_prod = json.load(f)


# Load DataFrame
df = pd.DataFrame(data)
df['videoURL'] = df['videoURLs'].apply(lambda x: x[0]['videoURL'] if x else None)
df['expired'] = pd.to_datetime(df['expired'])
df['year'] = df['expired'].dt.year

# Group by year for bar chart
expired_per_year = df.groupby('year').agg(
    count=('videoURL', 'count'),
).reset_index()

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Expired URLs Dashboard"),

    # Bar chart
    dcc.Graph(id='bar-chart'),

    html.H2("URLs Expired in Selected Year"),
    html.Div(id='table-container')
])


# Callback to update bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    Input('bar-chart', 'id')  # just a dummy input to trigger initial rendering
)
def update_bar(_):
    fig = px.bar(
        expired_per_year,
        x='year',
        y='count',
        text='count',
        title="Expired URLs Grouped by Year",
        labels={'count': 'Number of Expired URLs', 'year': 'Year'},
        color='count',
        color_continuous_scale='Reds'
    )
    fig.update_traces(textposition='outside')
    return fig


# Callback to update table based on clicked bar
@app.callback(
    Output('table-container', 'children'),
    Input('bar-chart', 'clickData')
)
def display_table(clickData):
    if clickData is None:
        return "Click a bar to see URLs for that year."

    # Get the clicked year
    year = clickData['points'][0]['x']
    filtered_df = df[df['year'] == year][['mappedOfferId', 'videoURL', 'expired']]

    # Create a simple HTML table
    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns])),
        html.Tbody([
            html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns])
            for i in range(len(filtered_df))
        ])
    ])


# Run app
if __name__ == '__main__':
    app.run(debug=True)
