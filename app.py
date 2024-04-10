# %%
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go # or plotly.express as px
from plotly.express import data
import statsmodels

# %%
# Import data
df = pd.read_csv('actualdata.csv')
df.head()

# %%
# Convert Date column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Extract month from Date column
df['Month'] = df['Date'].dt.month_name()

# Get min and max dates from the DataFrame
min_date = df['Date'].min()
max_date = df['Date'].max()

# Initial y-axis option
y_axis_options = ['SleepEff', 'TotalMinutesAsleep', 'TotalTimeInBed']
y_axis_selected = y_axis_options[0]

# Initialize the Dash app
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # Load the CSS stylesheet
app = dash.Dash(__name__, external_stylesheets=stylesheets)  # Initialize the app
server = app.server

# Define app layout
app.layout = html.Div([
    # Left column: Heading and Area chart
    html.Div([
        # Heading
        html.Div([
            html.H1("Fitness Activity Dashboard", className="header-title"),
            html.Div(
                "This dashboard is for physical therapists with 30 patients with health data spanning from April 12 to March 12. It gives an overview of how various health attributes affect the others, and of the patterns amongst and within users as well. This can also be used by public health organizations to monitor population-level trends, develop targeted interventions, and advocate for policies that support healthier lifestyles.",
                className="header-description")  # Description text
        ], className="row"),

        # Area chart and controls
        html.Div([
            # Area chart
            html.Div([
                dcc.Graph(id='area-chart'),
            ], style={'position': 'relative'}),
            
            # Controls with updated styling
            html.Div([
                html.Label("Time Range:", className="date-control-label"),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=min_date,
                    end_date=max_date,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    display_format='YYYY-MM-DD'
                ),
                html.Label("Measurement:", className="yaxis-control-label"),
                dcc.RadioItems(
                    id='y-axis-selector',
                    options=[{'label': 'Time In Bed but Not Asleep (mins)', 'value': 'SleepEff'},
                             {'label': 'Time Asleep (mins)', 'value': 'TotalMinutesAsleep'},
                             {'label': 'Time In Bed (mins)', 'value': 'TotalTimeInBed'}],
                    value=y_axis_selected,
                    labelStyle={'display': 'block'}
                ),
            ], className="area-controls-box", style={'border': '1px solid grey', 'border-radius': '5px'})
        ], className="area-chart-container"),  # Container for the area chart and controls
    ], className="four columns"),

    # Right column: Scatter plot and controls 
    html.Div([
        # Scatter plot and controls
        html.Div([
            # Scatter plot
            html.Div([
                dcc.Graph(id='scatter-plot', style={'padding-right': '50px', 'padding-bottom': '50px'}),
            ], style={'position': 'relative'}),
            
            # Controls (bottom right corner)
            html.Div([
                html.Div([
                    html.Label("Month:", className="control-label"),
                    dcc.RadioItems(
                        id='month-radio',
                        options=[{'label': month, 'value': month} for month in ['April', 'May']],
                        value='April',  # Default selection
                        labelStyle={'display': 'block'},
                        className="control-radio"
                    ),
                    html.Button("Switch Axes", id='switch-axes-button', n_clicks=0, className="control-button"),
                    dcc.Checklist(
                        id='uncolored-dots-checkbox',
                        options=[{'label': 'Include Users without BMI', 'value': 'include'}],
                        value=[],
                        className="control-checkbox"
                    ),
                    dcc.Checklist(
                        id='trendline-checkbox',
                        options=[{'label': 'Show Trendlines', 'value': 'trendline_on'}],
                        value=['trendline_on'],
                        className="control-checkbox"
                    ),
                ], className="controls-box"),
            ], style={'position': 'absolute', 'bottom': 135, 'right': 5, 'padding': '5px',
                      'background-color': 'white', 'border': '1px solid grey', 'border-radius': '5px'}),
        ], className="eight columns", style={'padding-top': '40px', 'position': 'relative'}),  # Adjust padding-top

        # DataTable
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {'name': col, 'id': col} for col in df.columns[4:13]
                ],
                data=df.iloc[:, 4:13].to_dict('records'),
                page_size=10,  # Set page size to limit rows displayed
                sort_action='native',  # Enable sorting
                style_table={'overflowX': 'auto', 'width': '200%'},  # Adjusted style
            )
        ], className="eight columns", style={'margin-top': '20px'})  # Adjusted className and style for DataTable
    ], className="eight columns")
], className="row")


############################################################ SCATTERPLOT ####################################################################

# Define scatter plot function
def scatter_plot(selected_month, uncolored_dots, n_clicks, trendline_on):
    filtered_df = df[df['Month'] == selected_month]

    if 'include' not in uncolored_dots:  # Check if the "Include" checkbox is not checked
        # Filter out rows with missing BMI values and drop rows where BMIBin is 'Unknown'
        filtered_df = filtered_df.dropna(subset=['BMIBin'])
        filtered_df = filtered_df[filtered_df['BMIBin'] != 'Unknown']

    # Define color mapping and legend labels
    color_map = {'Normal': 'purple', 'Overweight': 'red', 'Unknown': 'lightblue'}
    legend_labels = {'Normal': 'Normal BMI', 'Overweight': 'Overweight BMI', 'Unknown': 'Unknown BMI'}

    # Determine variables for x and y axes
    if n_clicks % 2 == 0:
        x_axis, y_axis = 'StepTotal', 'Calories'
    else:
        x_axis, y_axis = 'Calories', 'StepTotal'

    scatter_fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color='BMIBin', hover_name='Id',
                             title=f"Step Total vs Calories with BMI Color Scale ({selected_month})",
                             color_discrete_map=color_map, labels={'BMIBin': 'BMI'},
                             trendline="ols" if trendline_on else None)  # Apply color mapping and legend labels
    # Update x-axis label
    scatter_fig.update_xaxes(title_text="Step Total")

    scatter_fig.update_traces(marker=dict(size=10))

    scatter_fig.update_layout(margin=dict(
        l=50,
        r=170,
        b=100,
        t=100,
        pad=4
    ),
        paper_bgcolor="white", )

    return scatter_fig

# Callback to update scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('month-radio', 'value'),
     Input('uncolored-dots-checkbox', 'value'),
     Input('switch-axes-button', 'n_clicks'),
     Input('trendline-checkbox', 'value')]
)
def update_scatter_plot_callback(selected_month, uncolored_dots, n_clicks, trendline_on):
    return scatter_plot(selected_month, uncolored_dots, n_clicks, 'trendline_on' in trendline_on)


################################################################### AREA PLOT #############################################################################

# Aggregate data by date and StepBin, and calculate mean sleep efficiency and other metrics across all users
def aggregate_data(df, y_axis):
    if y_axis == 'SleepEff':
        df_agg = df.groupby(['Date', 'StepBin']).agg({'SleepEff': 'mean'}).reset_index()
        y_label = 'Time In Bed but Not Asleep (mins)'
    elif y_axis == 'TotalMinutesAsleep':
        df_agg = df.groupby(['Date', 'StepBin']).agg({'TotalMinutesAsleep': 'mean'}).reset_index()
        y_label = 'Time Asleep (mins)'
    elif y_axis == 'TotalTimeInBed':
        df_agg = df.groupby(['Date', 'StepBin']).agg({'TotalTimeInBed': 'mean'}).reset_index()
        y_label = 'Time In Bed (mins)'
    return df_agg, y_label

# Callback to update the area chart based on the selected y-axis option and date range
@app.callback(
    dash.dependencies.Output('area-chart', 'figure'),
    [dash.dependencies.Input('y-axis-selector', 'value'),
     dash.dependencies.Input('date-range', 'start_date'),
     dash.dependencies.Input('date-range', 'end_date')]
)

def update_chart(y_axis_selected, start_date, end_date):
    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    df_agg, y_label = aggregate_data(df_filtered, y_axis_selected)
    fig = px.area(df_agg, x='Date', y=y_axis_selected, color='StepBin',
                  category_orders={'StepBin': ['High Step Count (>10,000)', 'Average Step Count (5,000-9,999)', 'Low Step Count (<5,000)']}, 
                  labels={'StepBin': 'Step Count'})
    fig.update_yaxes(title_text=y_label)
    fig.update_layout(title='Sleep Effectivity Based on Step Count Over Time',
                      legend=dict(orientation="h", x=-.5, y=-0.3))  # Adjust x and y values here
    return fig
    

################################################################### DATA TABLE #############################################################################
def update_table(sort_by):
    if sort_by:
        sorted_df = df.sort_values(by=[col['column_id'] for col in sort_by], ascending=[col['direction'] == 'asc' for col in sort_by])
        return sorted_df.to_dict('records')
    else:
        return df.to_dict('records')


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


