import streamlit as st
from pycountry import countries
import requests
import json
import pandas as pd
from st_aggrid import AgGrid
import seaborn as sns
import matplotlib.pyplot as plt
import io

# Set app settings
st.set_page_config(
    page_title="U.S. Census Bureau App",
    layout="centered"
)

# App header
st.image("https://www.census.gov/mycd/application/images/census_doc_logo.png")
st.subheader("Interactive Dashboard : Yearly Birth Rate (1921-2021)")

# Create list of countries to select from
country_list = [""]
for country in countries:
    name = country.name
    country_list.append(name)

country = st.selectbox("Select country to visualize data :", country_list)

# Insert space
st.write("")

# Once country is selected...
if country:
    try:
        # Fetch data
        country_code = countries.get(name=country).alpha_2
        url = f"https://api.census.gov/data/timeseries/idb/1year?get=NAME,AGE,POP,AREA_KM2&GENC={country_code}&YR=2021&SEX=0"
        response = requests.get(url).json()
        df = pd.DataFrame(response, columns=response[0])
        df.drop(0, inplace=True)

        # Wrangle data
        df1 = pd.DataFrame(columns=["Year", "Number of Births", "% Rate"])
        df1["Year"] = 2021 - df["AGE"].astype("int")
        df1["Number of Births"] = df["POP"].astype("int")
        df1["% Rate"] = round(df1["Number of Births"].pct_change(periods=-1), 2)

        # Select time range
        col1, col2 = st.columns(2)
        with col1:
            index_year_1921 = len(df1["Year"]) - 1
            start_year = st.selectbox("Select start year :", df1["Year"], index=index_year_1921)
        with col2:
            end_year = st.selectbox("Select end year :", df1["Year"])
        st.write("")

        # Filter dataframe based on selected time range
        df1 = df1.loc[(df1["Year"] >= start_year) & (df1["Year"] <= end_year)]

        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col2:
            min_rate = df1["% Rate"].min()
            min_index = df1["% Rate"].idxmin()
            st.metric(label="Min. Rate Year",
                      value=df1.loc[min_index, "Year"],
                      delta=f"{min_rate:.1%}"
                      )
        with col3:
            max_rate = df1["% Rate"].max()
            max_index = df1["% Rate"].idxmax()
            st.metric(label="Max. Rate Year",
                      value=df1.loc[max_index, "Year"],
                      delta=f"{max_rate:.1%}"
                      )
        with col4:
            average_rate = df1["% Rate"].mean()
            st.metric(label="Average Rate",
                      value=f"{average_rate:.1%}"
                      )

        # Insert space
        st.write("")

        # Generate and display graph
        plt.figure(figsize=(20, 7))
        sns.barplot(data=df1, x=df1["Year"], y=df1["Number of Births"], color="#226094")
        plt.xticks(rotation=90)
        plt.title(f"U.S. Census Bureau - Yearly Birth Rate\n{country} ({start_year}-{end_year})")
        plt.xlabel("")
        plt.show()
        image = io.BytesIO()
        plt.savefig(image, format='png')

        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

        # Display button to download graph
        st.download_button(label="Download Graph",
                           data=image,
                           file_name=f"U.S. Census Bureau - Yearly Birth Rate - {country} ({start_year}-{end_year}).png",
                           mime="png"
                           )

        # Insert space
        st.write("")

        # Copy dataframe, reformat data, display data
        df2 = df1.copy()
        df2["% Rate"] = df2["% Rate"] * 100

        with st.expander(f"Interactive table of {country}"):
            AgGrid(df2)

    except json.decoder.JSONDecodeError:
        st.error("Country not referenced in U.S. Census Bureau database. Try another country.")
