from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="Dish Reviews Dashboard",
    page_icon="🍔",
    layout="wide",
)

st.title("Dish Reviews Dashboard")



NONE = "No Selection"
RATE_TYPES = ["food", "food_taste", "food_portion", "food_look", "service", "vibe", "overall"]
SUMMARY_RATE_TYPES = ["overall", "food", "service", "vibe"]
ID_COLS = ["time", "restaurant", "dish"]
FOOD_COLS = ["food", "food_taste", "food_portion", "food_look"]

@st.cache
def get_data():
    df = pd.read_json("reviews.json")
    df["time"] = pd.to_datetime(df["time"])
    return df


df = get_data()[ID_COLS + FOOD_COLS]
DISH_TYPES = list(df["dish"].unique())
RESTAURANTS = list(df["restaurant"].unique())

s_dish = st.sidebar.selectbox("Choose Dish", DISH_TYPES)
s_store = st.sidebar.selectbox("Choose Restaurant", ["All"] + RESTAURANTS)
s_rating = st.sidebar.selectbox("Choose Rating", FOOD_COLS)
df = df[df["dish"] == s_dish]
if s_store != "All":
    df = df[df["restaurant"] == s_store]

last_week = datetime.now() - timedelta(days=7)
df_week = df[df["time"] > last_week].mean()
df_last_week = df[last_week - df["time"] < timedelta(days=7)].mean()
st.subheader(f"Weekly Average Ratings for \"{s_dish}\"")
c0_0, c0_1, c0_2, c0_3 = st.columns(4)
with c0_0:
    st.metric(
        "Overall", 
        f'{df_week["food"]:.2f}', 
        f'{df_week["food"] - df_last_week["food"]:.3f}'
    )
with c0_1:
    st.metric(
        "Taste", 
        f'{df_week["food_taste"]:.2f}',
        f'{df_week["food_taste"] - df_last_week["food_taste"]:.3f}'
    )
with c0_2:
    st.metric(
        "Portion", 
        f'{df_week["food_portion"]:.2f}',
        f'{df_week["food_portion"] - df_last_week["food_portion"]:.3f}'
    )
with c0_3:
    st.metric(
        "Look", 
        f'{df_week["food_look"]:.2f}',
        f'{df_week["food_look"] - df_last_week["food_look"]:.3f}'
    )


c1_0, c1_1 = st.columns(2)
with c1_0:
    st.subheader(f"Ratings Distribution")
    st.bar_chart(np.histogram(df["food"], bins=[1,2,3,4,5,6])[0])

# st.subheader("Number of Reviews for Dish")
# st.text(f'{len(dish_df)}')
# st.subheader("Dish Rating Breakdown")
# dish_histogram = np.histogram(dish_df["food"], bins=[1,2,3,4,5,6])[0]
# st.bar_chart(dish_histogram)