import streamlit as st
from pycountry import countries
import requests
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io

st.set_page_config(
    page_title="U.S. Census Bureau App",
    layout="centered"
)

st.image("https://www.census.gov/mycd/application/images/census_doc_logo.png")
st.subheader("Interactive Dashboard : Yearly Birth Rate per Country")

country_list = [""]
for country in countries:
    name = country.name
    country_list.append(name)

country = st.selectbox("Select country to visualize data :", country_list)

st.write("")

if country:
    try:
        country_code = countries.get(name=country).alpha_2
        url = f"https://api.census.gov/data/timeseries/idb/1year?get=NAME,AGE,POP,AREA_KM2&GENC={country_code}&YR=2021&SEX=0"
        response = requests.get(url).json()
        df = pd.DataFrame(response, columns=response[0])

        df1 = df.drop(0)
        df1["AGE"] = df1["AGE"].astype("int")
        df1["POP"] = df1["POP"].astype("int")

        df2 = pd.DataFrame(columns=["Year", "Number of Births", "TempCalculation", "Progression"])
        df2["Year"] = 2021 - df1["AGE"]
        df2["Number of Births"] = df1["POP"]
        df2["TempCalculation"] = df2["Number of Births"].shift(-1)
        df2["Progression"] = round((df2["Number of Births"] - df2["TempCalculation"]) / df2["TempCalculation"], 2)
        df2 = df2.drop("TempCalculation", axis=1)
        df2.style.format({"Number of Births": lambda x: "{:,}".format(x)})
        df2 = df2.set_index("Year")

        col1, col2, col3, col4 = st.columns(4)
        with col2:
            st.metric(label="Year Min. Births",
                      value=df2["Number of Births"].idxmin(),
                      delta=None)
        with col4:
            st.metric(label="Year Max. Births",
                      value=df2["Number of Births"].idxmax(),
                      delta=None)
        st.write("")

        plt.figure(figsize=(20, 7))
        sns.barplot(data=df2, x=df2.index, y=df2["Number of Births"], color="#226094")
        plt.xticks(rotation=90)
        plt.title(f"U.S. Census Bureau - Yearly Birth Rate of {country}")
        plt.xlabel("")
        plt.show()
        img = io.BytesIO()
        plt.savefig(img, format='png')

        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

        st.download_button(label="Download Graph",
                           data=img,
                           file_name=f"U.S. Census Bureau - Yearly Birth Rate - {country}.png",
                           mime="png"
                           )

        st.write("")

        with st.expander(f"View data of {country}"):
            # Style bars inside cells of Number of Births column
            # df2_style = df2.style.bar(subset=["Number of Births"], axis=0, cmap="Blues")
            # To get styling to work with Streamlit 1.10.0, convert the styled dataframe to HTML
            # st.write(df2_style.to_html(escape=False), unsafe_allow_html=True)
            st.dataframe(data=df2, use_container_width=True)

    except AttributeError:
        st.write("")
    except json.decoder.JSONDecodeError:
        st.error("Country not referenced in U.S. Census Bureau database. Try another country.")
