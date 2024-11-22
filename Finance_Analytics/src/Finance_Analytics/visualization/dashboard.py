import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load your cleaned data
df = pd.read_csv('/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final/Final_expenditure.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("State-wise Expenditure Analysis Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': 'All States', 'value': 'All'}] + [{'label': state, 'value': state} for state in df['State'].unique()],
            value='All',
            multi=False,
            clearable=False,
            style={'width': '48%', 'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in df['Exp Category'].unique()],
            value='All',
            multi=False,
            clearable=False,
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
        )
    ]),
    
    dcc.RangeSlider(
        id='year-slider',
        min=df['Year'].apply(lambda x: int(x.split('-')[0])).min(),
        max=df['Year'].apply(lambda x: int(x.split('-')[0])).max(),
        value=[df['Year'].apply(lambda x: int(x.split('-')[0])).min(), df['Year'].apply(lambda x: int(x.split('-')[0])).max()],
        marks={str(year): str(year) for year in range(df['Year'].apply(lambda x: int(x.split('-')[0])).min(), df['Year'].apply(lambda x: int(x.split('-')[0])).max() + 1)},
        step=1,
    ),
    
    dcc.Graph(id='expenditure-time-series'),
    dcc.Graph(id='expenditure-category-pie'),
    
    html.Div(id='summary-stats', style={'margin-top': '20px'})
])

@app.callback(
    [Output('expenditure-time-series', 'figure'),
     Output('expenditure-category-pie', 'figure'),
     Output('summary-stats', 'children')],
    [Input('state-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graphs(selected_state, selected_category, year_range):
    # Filter data based on selected state
    if selected_state == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['State'] == selected_state]

    # Filter data based on year range
    filtered_df = filtered_df[
        (filtered_df['Year'].apply(lambda x: int(x.split('-')[0])) >= year_range[0]) & 
         (filtered_df['Year'].apply(lambda x: int(x.split('-')[0])) <= year_range[1])
    ]

    # Filter data based on selected category
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Exp Category'] == selected_category]
    
    # Time series chart
    time_series = px.line(filtered_df, x='Year', y='Value', color='Exp Category',
                          title=f'Expenditure Over Years for {"All States" if selected_state == "All" else selected_state}')
    time_series.update_layout(legend_title_text='Expenditure Category')
    
    # Pie chart for category breakdown
    category_df = filtered_df[filtered_df['Year'] == str(year_range[1])]
    pie_chart = px.pie(category_df, values='Value', names='Exp Category',
                       title=f'Expenditure Breakdown by Category for {"All States" if selected_state == "All" else selected_state} from {year_range[0]} to {year_range[1]}')
    
    # Summary statistics
    total_expenditure = filtered_df['Value'].sum()
    avg_expenditure = filtered_df['Value'].mean()
    max_expenditure = filtered_df['Value'].max()
    
    if not filtered_df.empty:
        max_year = filtered_df.loc[filtered_df['Value'].idxmax(), 'Year']
    else:
        max_year = "N/A"

    summary_stats = html.Div([
        html.H4(f"Summary Statistics for {'All States' if selected_state == 'All' else selected_state}"),
        html.P(f"Total Expenditure: ₹{total_expenditure:,.2f}"),
        html.P(f"Average Annual Expenditure: ₹{avg_expenditure:,.2f}"),
        html.P(f"Highest Expenditure: ₹{max_expenditure:,.2f} in {max_year}")
    ])
    
    return time_series, pie_chart, summary_stats

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)