import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the dataset
file_path = 'gdp_pcap.csv'
gdp_data = pd.read_csv(file_path)

# Extract unique countries for dropdown options
countries = gdp_data['country'].unique()

# Determine the range of years for the slider
years = gdp_data.columns[1:]  # Exclude the 'country' column

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    # Title of the application
    html.H1("GDP Per Capita Analysis"),
    
    # A brief description of what the application does
    html.P("This interactive application allows users to explore GDP per capita across different countries and time periods. Select multiple countries and a range of years to visualize how GDP per capita has evolved."),
    
    # Container for the controls (dropdown and slider)
    html.Div([
        # Dropdown menu for selecting countries. Allows multiple selections.
        html.Div([
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': country, 'value': country} for country in countries],
                value=['USA'],  # Sets the default selection
                multi=True  # Allows selecting multiple countries
            )
        ], style={'width': '50%', 'display': 'inline-block'}),  # Set width to half of the container
        
        # Slider for selecting a range of years
        html.Div([
            dcc.RangeSlider(
                id='year-slider',
                min=int(years[0]),  # Set the minimum value to the first year in the dataset
                max=int(years[-1]),  # Set the maximum value to the last year in the dataset
                value=[2000, 2010],  # Default selected range
                marks={str(year): str(year) for year in range(int(years[0]), int(years[-1])+1, 50)},  # Markers for readability
                step=1  # Slider moves in increments of 1 year
            )
        ], style={'width': '50%', 'display': 'inline-block'}),  # Set width to half of the container
        
    ], style={'display': 'flex'}),  # Use flexbox to layout children side by side
    
    # Graph object where the GDP per capita plot will be displayed
    dcc.Graph(id='gdp-graph'),
], style={'width': '80%', 'margin': '0 auto'})  # Style to center and set the width of the application layout

# Function to convert GDP per capita values from strings to floats
def gdp_to_float(gdp_str):
    # First, check if the value is a string. If it's not, it means it's already a number.
    if isinstance(gdp_str, str):
        # If 'k' is in the string, remove it and multiply the value by 1,000
        if 'k' in gdp_str:
            return float(gdp_str.replace('k', '')) * 1000
        # Otherwise, just convert the string to a float
        return float(gdp_str)
    # If the value is already a number (int or float), just return it
    return gdp_str


# Callback function to update the graph based on user input
@app.callback(
    Output('gdp-graph', 'figure'),  # The component to be updated is the graph's figure
    [Input('country-selector', 'value'),  # Input from the country selector dropdown
     Input('year-slider', 'value')]  # Input from the year range slider
)
def update_graph(selected_countries, selected_years):
    traces = []  # List to hold the data traces for plotting
    for country in selected_countries:  # Iterate through the selected countries
        df = gdp_data[gdp_data['country'] == country]  # Filter the dataset for the selected country
        df_selected_years = df.loc[:, str(selected_years[0]):str(selected_years[1])]  # Filter the dataset for the selected years
        
        # Convert GDP per capita values to floats for proper sorting and plotting
        y_values = [gdp_to_float(value) for value in df_selected_years.values.flatten()]
        
        trace = go.Scatter(  # Create a scatter plot trace for the country
            x=df_selected_years.columns,  # X-axis is the years
            y=y_values,  # Y-axis is the converted GDP per capita values
            mode='lines',  # Plot as lines
            name=country  # Legend name
        )
        traces.append(trace)  # Add the trace to the list of traces
    
    # Return the figure object with the data and layout
    return {
        'data': traces,  # Data traces for plotting
        'layout': go.Layout(  # Layout configuration
            title='GDP Per Capita Over Time',  # Graph title
            xaxis={'title': 'Year'},  # X-axis label
            yaxis={'title': 'GDP Per Capita ($)'},  # Y-axis label
            hovermode='closest'  # Hover mode configuration for better tooltip display
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)