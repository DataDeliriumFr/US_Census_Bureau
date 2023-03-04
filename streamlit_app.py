import streamlit as st
from pycountry import countries
import requests
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io


st.image("https://www.census.gov/mycd/application/images/census_doc_logo.png")
st.subheader("Interactive Dashboard : Yearly Birth Rate per Country")

country_list = [""]
for country in countries:
    name = country.name
    country_list.append(name)

country = st.selectbox("Select country to visualize data :", country_list)

if country:
    try:
        country_code = countries.get(name=country).alpha_2
        url = f"https://api.census.gov/data/timeseries/idb/1year?get=NAME,AGE,POP,AREA_KM2&GENC={country_code}&YR=2021&SEX=0"
        response = requests.get(url)
        response = response.json()
        df = pd.DataFrame(response, columns=response[0])

        df1 = df.drop(0)
        df1["AGE"] = df1["AGE"].astype("int")
        df1["POP"] = df1["POP"].astype("int")

        df2 = pd.DataFrame(columns=["Year", "Number of Births"])
        df2["Year"] = 2021 - df1["AGE"]
        df2["Number of Births"] = df1["POP"]
        df2 = df2.set_index("Year")

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

        st.download_button(label="Download Graph", data=img, file_name=f"U.S. Census Bureau - Yearly Birth Rate - {country}.png", mime="png")
        
        with st.expander(f"View data of {country}"):
            style = df2.style.format({"Number of Births": lambda x :"{,:.}".format(x)})
            st.dataframe(style)

    except (AttributeError):
        st.write("")
    except json.decoder.JSONDecodeError:
        st.error("Country not referenced in U.S. Census Bureau database. Try another country.")
