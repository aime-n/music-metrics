# app.py

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import requests

# Set the page configuration
st.set_page_config(
    page_title="Instagram Metrics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define a mapping from state names to state codes (ISO 3166-2)
brazil_states = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO"
}

# Function to load JSON data
@st.cache_data
def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)

# Load data
user_insights = load_json('data/user_insights.json')
demographics_city = load_json('data/demographics_city.json')
demographics_state = load_json('data/demographics_state.json')

# Convert JSON data to DataFrames
def json_to_df(json_data, metric_name):
    data = json_data['data']
    for item in data:
        if item['name'] == metric_name:
            values = item['values'][0]['value']
            df = pd.DataFrame(list(values.items()), columns=['Category', 'Percentage'])
            return df
    return pd.DataFrame()

# Extract DataFrames
# Example metrics: reach, impressions, likes, comments, shares, follower_growth, ctr
# Assuming 'user_insights.json' has these metrics per date

def extract_user_insights(json_data):
    data = json_data['data']
    df = pd.DataFrame(data)
    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'])
    return df

user_insights_df = extract_user_insights(user_insights)

# Demographics DataFrames
demographics_city_df = json_to_df(demographics_city, 'audience_city')
demographics_state_df = json_to_df(demographics_state, 'audience_state')

# Map State names to State Codes
# Assuming 'demographics_state_df' has 'State' as state codes (e.g., "SP")
# If 'State' is state names, map them to codes
if demographics_state_df['Category'].dtype == object and demographics_state_df['Category'].str.len().max() > 2:
    demographics_state_df['State_Code'] = demographics_state_df['Category'].map(brazil_states)
else:
    demographics_state_df['State_Code'] = demographics_state_df['Category']

# Remove 'Other' if present, or handle it appropriately
demographics_state_df = demographics_state_df[demographics_state_df['State_Code'].notna()]

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Reach vs Impressions", "Interactions", "Demographics"])

# Home Page
if page == "Home":
    st.title("Instagram Metrics Dashboard")
    st.markdown("""
    Welcome to the Instagram Metrics Dashboard. Use the navigation bar to explore different metrics and insights.
    """)
    
# Reach vs Impressions Page
elif page == "Reach vs Impressions":
    st.title("Reach vs. Impressions Over Time")
    
    # Create the plot
    fig = px.line(
        user_insights_df,
        x='date',
        y=['reach', 'impressions'],
        markers=True,
        labels={'value': 'Count', 'variable': 'Metric'},
        title='Reach vs. Impressions Over Time',
        template='plotly_white'
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Count'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
# Interactions Page
elif page == "Interactions":
    st.title("Total Interactions by Content Type")
    
    # Assuming 'user_insights_df' has a 'Content_Type' column
    if 'Content_Type' in user_insights_df.columns:
        # Aggregate interactions
        interactions_df = user_insights_df.groupby('Content_Type')[['likes', 'comments', 'shares']].sum().reset_index()
        interactions_df['Total_Interactions'] = interactions_df['likes'] + interactions_df['comments'] + interactions_df['shares']
        
        # Create bar chart
        fig = px.bar(
            interactions_df,
            x='Content_Type',
            y='Total_Interactions',
            color='Content_Type',
            labels={'Total_Interactions': 'Total Interactions', 'Content_Type': 'Content Type'},
            title='Total Interactions by Content Type',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No 'Content_Type' data available in user insights.")
    
# Demographics Page
elif page == "Demographics":
    st.title("Audience Distribution Across Brazilian States")
    
    # Fetch GeoJSON data for Brazilian states
    @st.cache_data
    def get_geojson(url):
        response = requests.get(url)
        return response.json()
    
    geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    brazil_geojson = get_geojson(geojson_url)
    
    # Create choropleth map
    fig = px.choropleth(
        demographics_state_df,
        geojson=brazil_geojson,
        locations='State_Code',
        color='Percentage',
        color_continuous_scale='Blues',
        featureidkey='properties.sigla',
        scope='south america',
        labels={'Percentage': 'Audience (%)'},
        title='Instagram Audience Distribution Across Brazilian States'
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Audience Percentage",
            ticksuffix="%",
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
