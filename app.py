import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Instagram Metrics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for navigation between different pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Audience Map by State", "Bar Chart by State", "Reach vs Impressions"])

# Fetch the GeoJSON data for Brazilian states
@st.cache_data
def get_brazil_geojson():
    geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    response = requests.get(geojson_url)
    return response.json()

# Load the GeoJSON data
brazil_geojson = get_brazil_geojson()

# Define list of Brazilian states and their codes
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

# Generate synthetic demographic data for each state
def generate_synthetic_data():
    np.random.seed(42)
    data = {
        "State": list(brazil_states.keys()),
        "State_Code": list(brazil_states.values()),
        "Audience_Percentage": np.random.randint(1, 20, size=len(brazil_states))
    }
    brazil_df = pd.DataFrame(data)
    total = brazil_df['Audience_Percentage'].sum()
    brazil_df['Audience_Percentage'] = (brazil_df['Audience_Percentage'] / total) * 100
    return brazil_df

# Load synthetic data
brazil_df = generate_synthetic_data()

# Page 1: Audience Map by State
if page == "Audience Map by State":
    st.title("Audience Distribution Across Brazilian States")
    st.write("This map visualizes the audience distribution across Brazilian states as a percentage of the total audience.")
    
    # Create a choropleth map
    fig = px.choropleth(
        brazil_df,
        geojson=brazil_geojson,
        locations='State_Code',
        color='Audience_Percentage',
        color_continuous_scale='Blues',
        featureidkey='properties.sigla',
        scope='south america',
        labels={'Audience_Percentage': 'Audience (%)'},
        title='Instagram Audience Distribution Across Brazilian States'
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True)

# Page 2: Bar Chart by State
elif page == "Bar Chart by State":
    st.title("Audience Distribution by State")
    st.write("This bar chart displays the audience distribution percentage for each Brazilian state.")
    
    # Create a bar chart
    fig = px.bar(
        brazil_df,
        x='State',
        y='Audience_Percentage',
        color='Audience_Percentage',
        color_continuous_scale='Blues',
        labels={'Audience_Percentage': 'Audience (%)', 'State': 'Brazilian State'},
        title='Instagram Audience Distribution by State'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Page 3: Reach vs Impressions Line Chart
elif page == "Reach vs Impressions":
    st.title("Reach vs. Impressions Over Time")
    st.write("This line chart displays synthetic data for reach and impressions over a period of time.")
    
    # Generate synthetic data for reach and impressions
    dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
    reach = np.random.randint(2000, 5000, size=len(dates))
    impressions = reach + np.random.randint(500, 2000, size=len(dates))
    
    reach_impressions_df = pd.DataFrame({
        "Date": dates,
        "Reach": reach,
        "Impressions": impressions
    })
    
    # Create a line chart
    fig = px.line(
        reach_impressions_df,
        x='Date',
        y=['Reach', 'Impressions'],
        markers=True,
        labels={'value': 'Count', 'variable': 'Metric'},
        title='Reach vs. Impressions Over Time'
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        legend_title="Metrics"
    )
    
    st.plotly_chart(fig, use_container_width=True)
