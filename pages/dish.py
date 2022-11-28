from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def rating_chart(data, x, y):
    st.altair_chart(alt.Chart(data).mark_line().encode(
            x=x,
            y=alt.Y(y, scale=alt.Scale(domain=(1,5)))
        ),
        use_container_width=True
    )

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
df = df[df["dish"] == s_dish]
if s_store != "All":
    df = df[df["restaurant"] == s_store]

last_week = datetime.now() - timedelta(days=7)
df_week = df[df["time"] > last_week]
df_last_week = df[(df["time"] <= last_week) & (df["time"] > last_week - timedelta(days=7))]
st.subheader(f"Weekly Metrics for \"{s_dish}\"")

c0_0, c0_1, c0_2, c0_3, c0_4 = st.columns(5)
with c0_0:
    st.metric(
        "Number of Reviews", 
        f'{len(df_week)}', 
        f'{len(df_week) - len(df_last_week)}'
    )
with c0_1:
    st.metric(
        "Overall", 
        f'{df_week["food"].mean():.2f}', 
        f'{df_week["food"].mean() - df_last_week["food"].mean():.3f}'
    )
with c0_2:
    st.metric(
        "Taste", 
        f'{df_week["food_taste"].mean():.2f}',
        f'{df_week["food_taste"].mean() - df_last_week["food_taste"].mean():.3f}'
    )
with c0_3:
    st.metric(
        "Portion", 
        f'{df_week["food_portion"].mean():.2f}',
        f'{df_week["food_portion"].mean() - df_last_week["food_portion"].mean():.3f}'
    )
with c0_4:
    st.metric(
        "Look", 
        f'{df_week["food_look"].mean():.2f}',
        f'{df_week["food_look"].mean() - df_last_week["food_look"].mean():.3f}'
    )

st.subheader(f"All-Time Metrics for \"{s_dish}\"")
s_rating = st.selectbox("Choose Rating", FOOD_COLS)
c1_0, c1_1, c1_2 = st.columns(3)
with c1_0:
    st.subheader(f"Ratings Distribution")
    st.bar_chart(np.histogram(df[s_rating], bins=[1,2,3,4,5,6])[0])
with c1_1:
    st.subheader(f"Ratings Trend")
    df_daily = (df
        .set_index("time")
        .resample('D')
        .mean(numeric_only=True)
        .reset_index()
    )
    st.altair_chart(alt.Chart(df_daily).mark_line().encode(
            x='time',
            y=alt.Y(s_rating, scale=alt.Scale(domain=(1,5)))
        ),
        use_container_width=True
    )
with c1_2:
    st.subheader(f"Ratings by Hour of Day")
    df_by_hour = df.groupby(df["time"].dt.hour)[s_rating].mean(numeric_only=True).reset_index()
    st.altair_chart(alt.Chart(df_by_hour).mark_bar(size=20).encode(
            x='time',
            y=alt.Y(s_rating, scale=alt.Scale(domain=(1,5)))
        ),
        use_container_width=True
    )

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True)

# st.subheader("Number of Reviews for Dish")
# st.text(f'{len(dish_df)}')
# st.subheader("Dish Rating Breakdown")
# dish_histogram = np.histogram(dish_df["food"], bins=[1,2,3,4,5,6])[0]
# st.bar_chart(dish_histogram)