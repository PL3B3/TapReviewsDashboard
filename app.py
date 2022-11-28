from datetime import datetime, timedelta
import json
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

NONE = "No Selection"
RATE_TYPES = ["food", "food_taste", "food_portion", "food_look", "service", "vibe", "overall"]
SUMMARY_RATE_TYPES = ["overall", "food", "service", "vibe"]

@st.cache
def get_data():
    df = pd.read_json("reviews.json")
    df["time"] = pd.to_datetime(df["time"])
    return df

df = get_data()
DISH_TYPES = list(df["dish"].unique())
RESTAURANTS = list(df["restaurant"].unique())

st.title("TapReviews Insights")
# st.write(reviews)

dish_name = st.selectbox("Choose Dish", [NONE] + DISH_TYPES)

if dish_name != NONE:
    dish_df = df[df["dish"] == dish_name]
    st.subheader("Average Dish Rating")
    st.text(f'{dish_df["food"].mean():.2f}')
    st.text(f'{dish_df["food_taste"].mean():.2f}')
    st.text(f'{dish_df["food_portion"].mean():.2f}')
    st.text(f'{dish_df["food_look"].mean():.2f}')
    st.subheader("Number of Reviews for Dish")
    st.text(f'{len(dish_df)}')
    st.subheader("Dish Rating Breakdown")
    dish_histogram = np.histogram(dish_df["food"], bins=[1,2,3,4,5,6])[0]
    st.bar_chart(dish_histogram)


st.header("Average Dish Ratings")
st.dataframe(df.groupby("dish")["food"].mean().sort_values(ascending=False))

# if dish_name != NONE:
#     df[df["dish"] == dish_name].groupby(df["time"].dt.hour)["service"].sum()

st.header("Average Service Ratings by Hour of Day")
st.line_chart(df.groupby(df["time"].dt.hour)["service"].mean(numeric_only=True))

st.header("Average Service Ratings by Day of Week")
st.line_chart(df.groupby(df["time"].dt.day_of_week)["service"].mean(numeric_only=True))

# st.header("Average Ratings Over Time")
rate_type = st.selectbox("Choose Rating Type", RATE_TYPES)
restaurant = st.selectbox("Choose Restaurant", [NONE] + RESTAURANTS)
st.header(f"Ratings Over Time [{rate_type}]")
    # rate_df = df[["time", "food", "food_taste", "food_portion", "food_look", "service", "vibe", "overall"]]
rate_df = df
if restaurant != NONE:
    rate_df = rate_df[rate_df["restaurant"] == restaurant]
    # rate_df = rate_df[rate_df["time"] > datetime.now() - timedelta(days=7)]
rate_df = rate_df[["time"] + [rate_type]].set_index("time").resample('D').mean(numeric_only=True)
st.line_chart(rate_df)

melt_df = pd.melt(
    df.set_index("time")
        .resample('D')
        .mean(numeric_only=True)
        .reset_index(), 
    id_vars=["time"]
)
st.altair_chart(alt.Chart(melt_df).mark_line().encode(
    x='time',
    y=alt.Y('value', scale=alt.Scale(domain=(1,5))),
    color="variable")
)

# df[df["dish"] == dish_name]
# df[df["time"].dt.hour == 9]

# df["time"].dt.hour