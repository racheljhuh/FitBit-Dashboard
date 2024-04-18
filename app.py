# %%
import dash
from dash import dcc, html, Input, Output, dash_table, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go # or plotly.express as px
from plotly.express import data
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# %%
# Import data
df = pd.read_csv('actualdata.csv')
df.head()

# %%
# Convert Date column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Extract month from Date column
df['Month'] = df['Date'].dt.month_name()

df_table = df.drop(['WeightKg', 'BMIBin', 'StepBin', 'Month', 'SleepEff'], axis=1)

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

new_column_titles = {
    'Date': 'Date',
    'Id': 'User',
    'StepTotal': 'Steps',
    'Calories': 'Calories',
    'WeightPounds': 'Weight (lbs)',
    'BMI': 'BMI',
    'TotalMinutesAsleep': 'Time Asleep (mins)',
    'TotalTimeInBed': 'Time In Bed (mins)',
}


# Define app layout
app.layout = html.Div([
    html.Div([
        # GitHub icon linked to repository
        html.A(
            html.Img(src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                     style={'width': '30px', 'height': '30px'}),
            href="https://github.com/racheljhuh/FitBit-Dashboard",
            target="_blank",  # Open link in a new tab
            style={'position': 'absolute', 'top': '10px', 'right': '10px'}
        )
    ]),
    # Header and description centered at the top
    html.Div([
        html.H1("Fitness Activity Dashboard"),
        html.Div(
            "This dashboard is for physical therapists with 30 patients with health data spanning from April 12 to March 12. It gives an overview of how various health attributes affect the others, and of the patterns amongst and within users as well. This can also be used by public health organizations to monitor population-level trends, develop targeted interventions, and advocate for policies that support healthier lifestyles.",
            className="header-description")
    ], className="row", style={'text-align': 'center'}),

    # Area chart and scatter plot with controls
    html.Div([
        # Area chart and controls
        html.Div([
            # Area chart
            html.Div([
                dcc.Graph(id='area-chart'),
            ], style={'position': 'relative', 'margin-top': '20px'}),
            
            # Controls for the area chart
            html.Div([
                html.Label("Time Range:"),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=min_date,
                    end_date=max_date,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    display_format='YYYY-MM-DD'
                ),
                html.Label("Measurement:"),
                dcc.RadioItems(
                    id='y-axis-selector',
                    options=[{'label': 'Time In Bed but Not Asleep (mins)', 'value': 'SleepEff'},
                             {'label': 'Time Asleep (mins)', 'value': 'TotalMinutesAsleep'},
                             {'label': 'Time In Bed (mins)', 'value': 'TotalTimeInBed'}],
                    value=y_axis_selected,
                    labelStyle={'display': 'block'}
                ),
            ], className="area-controls-box", style={'border': '1px solid grey', 'border-radius': '5px', 'margin-bottom': '50px'})
        ], className="six columns"),

        # Scatter plot and controls
        html.Div([
            # Scatter plot
            html.Div([
                dcc.Graph(id='scatter-plot'),
            ], style={'position': 'relative', 'margin-bottom': '20px'}),
            
            # Controls for the scatter plot
            html.Div([
                html.Label("Month:"),
                dcc.RadioItems(
                    id='month-radio',
                    options=[{'label': month, 'value': month} for month in ['April', 'May']],
                    value='April',  # Default selection
                    labelStyle={'display': 'block'},
                    className="control-radio"
                ),
                html.Button("Switch Axes", id='switch-axes-button', n_clicks=0),
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
            ], className="scatter-controls-box", style={'border': '1px solid grey', 'border-radius': '5px', 'margin-bottom': '50px'})
        ], className="six columns"),
    ], className="row"),

    # Dashboard at the bottom
    html.Div([
        # Data table on the left
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{'name': new_column_titles[col], 'id': col} for col in df_table.columns],
                data=df_table.to_dict('records'),
                page_size=10,  # Set page size to limit rows displayed
                sort_action='native',  # Enable sorting
                style_table={'overflowX': 'auto', 'width': '100%'},  # Adjusted style
            )
        ], className="eight columns"),
        # Interactive elements
        html.Div([
            html.Label("Select users:"),
            dcc.Dropdown(
                id='id-dropdown',
                options=[{'label': id_val, 'value': id_val} for id_val in df_table['Id'].unique()],
                value=[],  # Default value, can be set to a list of initial IDs if desired
                multi=True  # Allow multiple IDs to be selected
            ),
            html.Label("Date Range:"),
            # Date range slider
            dcc.DatePickerRange(
                    id='date-slider',
                    start_date=min_date,
                    end_date=max_date,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    display_format='YYYY-MM-DD'
            ),
            html.Label("Step Total Range:"),
            dcc.RangeSlider(
                id='steptotal-slider',
                min=df_table['StepTotal'].min(),  # Minimum StepTotal value
                max=df_table['StepTotal'].max(),  # Maximum StepTotal value
                value=[df_table['StepTotal'].min(), df_table['StepTotal'].max()],  # Initial range
                marks={df_table['StepTotal'].min(): str(df_table['StepTotal'].min()),
                    df_table['StepTotal'].max(): str(df_table['StepTotal'].max())},  # Only show min and max values
                step=1,  # Increment by 1
                tooltip={'always_visible': True, 'placement': 'bottom'}  # Show tooltip always for debugging
            ),

            html.Label("Calories Range:"),
            dcc.RangeSlider(
                id='calories-slider',
                min=df_table['Calories'].min(),  # Minimum Calories value
                max=df_table['Calories'].max(),  # Maximum Calories value
                value=[df_table['Calories'].min(), df_table['Calories'].max()],  # Initial range
                marks={df_table['Calories'].min(): str(df_table['Calories'].min()),
                    df_table['Calories'].max(): str(df_table['Calories'].max())},  # Only show min and max values
                step=1,  # Increment by 1
                tooltip={'always_visible': True, 'placement': 'bottom'}  # Show tooltip always for debugging
            ),
            html.Label("Weight (lbs) Range:"),
            dcc.RangeSlider(
                id='weight-slider',
                min=df_table['WeightPounds'].min(),  # Minimum WeightPounds value
                max=df_table['WeightPounds'].max(),  # Maximum WeightPounds value
                value=[df_table['WeightPounds'].min(), df_table['WeightPounds'].max()],  # Initial range
                marks={df_table['WeightPounds'].min(): str(df_table['WeightPounds'].min()),
                    df_table['WeightPounds'].max(): str(df_table['WeightPounds'].max())},  # Only show min and max values
                step=1,  # Increment by 1
                tooltip={'always_visible': True, 'placement': 'bottom'}  # Show tooltip only when sliding
            ),
            html.Label("BMI Range:"),
            dcc.RangeSlider(
                id='bmi-slider',
                min=df_table['BMI'].min(),  # Minimum BMI value
                max=df_table['BMI'].max(),  # Maximum BMI value
                value=[df_table['BMI'].min(), df_table['BMI'].max()],  # Initial range
                marks={df_table['BMI'].min(): str(df_table['BMI'].min()),
                    df_table['BMI'].max(): str(df_table['BMI'].max())},  # Only show min and max values
                step=1,  # Increment by 1
                tooltip={'always_visible': True, 'placement': 'bottom'}  # Show tooltip only when sliding
            ),
            html.Label("Time Asleep Range:"),
            dcc.RangeSlider(
                id='sleep-slider',
                min=df_table['TotalMinutesAsleep'].min(),  # Minimum TotalMinutesAsleep value
                max=df_table['TotalMinutesAsleep'].max(),  # Maximum TotalMinutesAsleep value
                value=[df_table['TotalMinutesAsleep'].min(), df_table['TotalMinutesAsleep'].max()],  # Initial range
                marks={df_table['TotalMinutesAsleep'].min(): str(df_table['TotalMinutesAsleep'].min()),
                    df_table['TotalMinutesAsleep'].max(): str(df_table['TotalMinutesAsleep'].max())},  # Only show min and max values
                step=1,  # Increment by 1
                tooltip={'always_visible': True, 'placement': 'bottom'}  # Show tooltip only when sliding
            ),
        ], className="four columns"),
    ], className="row")
], className="container")

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

    scatter_fig.update_layout(paper_bgcolor="white", legend=dict(orientation="h", x=-.5, y=-0.3))

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
# Define color mapping for area plot
area_color_map = {'High Step Count (>10,000)': 'purple', 'Average Step Count (5,000-9,999)': 'red', 'Low Step Count (<5,000)': 'lightblue'}
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
                  labels={'StepBin': 'Step Count'}, color_discrete_map=area_color_map)  # Apply color mapping
    fig.update_yaxes(title_text=y_label)
    fig.update_layout(title='Sleep Effectivity Based on Step Count Over Time',
                      legend=dict(orientation="h", x=-.5, y=-0.3))  # Adjust x and y values here
    return fig
    

################################################################### DATA TABLE #############################################################################

@app.callback(
    Output('data-table', 'data'),
    [Input('id-dropdown', 'value'),
     Input('date-slider', 'start_date'),
     Input('date-slider', 'end_date'),
     Input('steptotal-slider', 'value'),
     Input('calories-slider', 'value'),
     Input('weight-slider', 'value'),
     Input('bmi-slider', 'value'),
     Input('sleep-slider', 'value')]
)
def update_table(selected_ids, start_date, end_date, step_range, calories_range, weight_range, bmi_range, sleep_range):
    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_input == 'id-dropdown':
        if not selected_ids:
            # If no IDs are selected, return the original data
            return df_table.to_dict('records')
        else:
            # Filter the dataframe based on selected IDs and return the filtered data
            filtered_df = df_table[df_table['Id'].isin(selected_ids)]
    elif triggered_input == 'date-slider':
        # Filter the dataframe based on selected date range and return the filtered data
        filtered_df = df_table[(df_table['Date'] >= start_date) & (df_table['Date'] <= end_date)]
    else:
        # If none of the inputs are triggered, return the original data
        filtered_df = df_table

    # Additional filters based on other sliders
    filtered_df = filtered_df[(filtered_df['StepTotal'] >= step_range[0]) & (filtered_df['StepTotal'] <= step_range[1]) &
                               (filtered_df['Calories'] >= calories_range[0]) & (filtered_df['Calories'] <= calories_range[1]) &
                               (filtered_df['WeightPounds'] >= weight_range[0]) & (filtered_df['WeightPounds'] <= weight_range[1]) &
                               (filtered_df['BMI'] >= bmi_range[0]) & (filtered_df['BMI'] <= bmi_range[1]) &
                               (filtered_df['TotalMinutesAsleep'] >= sleep_range[0]) & (filtered_df['TotalMinutesAsleep'] <= sleep_range[1])]

    return filtered_df.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


