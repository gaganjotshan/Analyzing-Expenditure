import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load your cleaned data
df = pd.read_csv('/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final/expenditure_analysis.csv')

# Convert 'Year' to a numeric value representing the starting year
df['Year'] = df['Year'].apply(lambda x: int(x.split('-')[0]))

# Replace any non-numeric values in 'Value' with NaN and drop those rows
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
df.dropna(subset=['Value'], inplace=True)

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
            options=[{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in df['Exp_Category'].unique()],
            value='All',
            multi=False,
            clearable=False,
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
        )
    ]),
    
    dcc.RangeSlider(
        id='year-slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=[df['Year'].min(), df['Year'].max()],
        marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1)},
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
    filtered_df = df.copy()
    
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    # Filter data based on year range
    filtered_df = filtered_df[
        (filtered_df['Year'] >= year_range[0]) & 
        (filtered_df['Year'] <= year_range[1])
    ]

    # Filter data based on selected category
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Exp_Category'] == selected_category]
    
    # Check if filtered DataFrame is empty
    if filtered_df.empty:
        return {}, {}, "No data available for the selected filters."

    # Aggregate data by Year and Exp_Category
    aggregated_df = filtered_df.groupby(['Year', 'Exp_Category'], as_index=False)['Value'].sum()

    # Time series chart
    time_series = px.line(aggregated_df, x='Year', y='Value', color='Exp_Category',
                          title=f'Expenditure Over Years for {"All States" if selected_state == "All" else selected_state}',
                          labels={'Value': 'Expenditure (in ₹)', 'Year': 'Financial Year'},
                          markers=True)  # Added markers for better visibility
    
    time_series.update_traces(mode='lines+markers')  # Ensures both lines and markers are shown

    # Pie chart for category breakdown
    category_df = aggregated_df[aggregated_df['Year'] == year_range[1]]
    
    if category_df.empty:
        pie_chart = px.pie(title="No data available for pie chart")
    else:
        pie_chart = px.pie(category_df, values='Value', names='Exp_Category',
                           title=f'Expenditure Breakdown by Category for {"All States" if selected_state == "All" else selected_state} from {year_range[0]} to {year_range[1]}')
    
    # Summary statistics
    total_expenditure = aggregated_df['Value'].sum()
    avg_expenditure = aggregated_df['Value'].mean()
    max_expenditure = aggregated_df['Value'].max()
    
    max_year = aggregated_df.loc[aggregated_df['Value'].idxmax(), 'Year'] if not aggregated_df.empty else "N/A"

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