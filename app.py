import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px


# Set app settings
st.set_page_config(
    page_title="U.S. Census Bureau App",
    layout="centered"
)

# Display logo
st.image("https://www.census.gov/mycd/application/images/census_doc_logo.png")

# Initiate dataframe
df = pd.read_csv("Yearly Births by Country.csv")

# Set up menu side bar
menu_bar = st.sidebar
menu_title = menu_bar.title("Interactive Dashboard")
with menu_bar:
    menu_input = st.radio("Explore data by :", ("worldwide overview", "continent", "country"))

# Display graphs depending on user input
if menu_input == "continent":
    # Line plot of yearly births by continent
    df_grouped = df.groupby(["Continent", "Year"]).agg({'Number of Births': np.sum}).reset_index()
    fig_line = px.line(df_grouped, x="Year", y="Number of Births", color="Continent")
    fig_line.update_layout(title_text='Yearly Births - Continents - Overview')
    st.plotly_chart(fig_line, use_container_width=True)

    with st.expander("**DRILL THROUGH A CONTINENT**"):
        # User input : continent
        continent_list = ["Africa", "Asia", "Europe", "North America", "South America"]
        continent = st.selectbox("Select continent :", continent_list, 0)
        df_continent = df[df["Continent"] == continent]

        country_list = df_continent["Country"].unique().tolist()
        countries = st.multiselect("Compare specific countries :", sorted(country_list))
        graph_countries = " | ".join(sorted(countries))
        df_countries = df_continent[df_continent["Country"].isin(countries)]

        if countries:
            # Plot animated choropleth map of selected countries only
            fig_choro_countries = px.choropleth(df_countries,
                                                locations="Country",
                                                locationmode="country names",
                                                color="Number of Births",
                                                animation_frame="Year",
                                                animation_group="Continent",
                                                color_continuous_scale='teal',
                                                range_color=[df_countries["Number of Births"].min(),
                                                             df_countries["Number of Births"].max()],
                                                scope=continent.lower())
            fig_choro_countries.update_layout(title_text=f'Animated map of {graph_countries}',
                                              geo=dict(showframe=False,
                                                       showcoastlines=False)
                                              )
            fig_choro_countries.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 150
            fig_choro_countries.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5
            st.plotly_chart(fig_choro_countries, use_container_width=True)
        else:
            # Insert space
            st.write("")
            # Plot animated choropleth map
            fig_choro_continent = px.choropleth(df_continent,
                                                locations="Country",
                                                locationmode="country names",
                                                color="Number of Births",
                                                animation_frame="Year",
                                                animation_group="Continent",
                                                color_continuous_scale='teal',
                                                range_color=[df_continent["Number of Births"].min(),
                                                             df_continent["Number of Births"].max()],
                                                scope=continent.lower())
            fig_choro_continent.update_layout(title_text=f'Animated map of {continent}',
                                              geo=dict(showframe=False,
                                                       showcoastlines=False)
                                              )
            fig_choro_continent.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 150
            fig_choro_continent.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5
            st.plotly_chart(fig_choro_continent, use_container_width=True)

elif menu_input == "country":
    country_list = df["Country"].unique().tolist()
    countries_2 = st.multiselect("Enter one or multiple countries:", sorted(country_list))
    countries_print = " | ".join(sorted(countries_2))

    if countries_2:
        try:
            # Select time range
            col1, col2 = st.columns(2)
            with col1:
                start_year = st.selectbox("Select start year :", df["Year"].unique())
            with col2:
                end_year = st.selectbox("Select end year :", df["Year"].unique(), 100)
            st.write("")
            # Filter dataframe based on selected time range
            df_countries_2 = df.loc[
                (df["Year"] >= start_year) & (df["Year"] <= end_year) & (df["Country"].isin(countries_2))]

            # Insert space
            st.write("")

            # Generate and display graph
            fig_line_country = px.line(df_countries_2,
                                       x=df_countries_2["Year"],
                                       y=df_countries_2["Number of Births"],
                                       color=df_countries_2["Country"])
            # fig_bar.update_traces(line=dict(color="#226094"))
            fig_line_country.update_layout(title_text=f"Yearly Births of {countries_print} ({start_year} - {end_year})")
            st.plotly_chart(fig_line_country, use_container_width=True)

        except:
            st.write("Please enter correct range of years")
else:
    # Line Plot of global births
    df_global = df.groupby("Year", as_index=False).sum()
    fig_line_global = px.line(df_global, x="Year", y="Number of Births")
    fig_line_global.update_traces(line=dict(color="#226094"))
    fig_line_global.update_layout(title_text='Yearly Births - Worldwide')
    st.plotly_chart(fig_line_global)
