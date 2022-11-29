from datetime import datetime, timedelta
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
import altair as alt
import time

st.set_page_config(
    page_title="Dish Reviews Dashboard",
    page_icon="🍔",
    layout="wide",
)
st_autorefresh(interval=3000, limit=100000)

def rating_chart(data, x, y):
    st.altair_chart(alt.Chart(data).mark_line().encode(
            x=x,
            y=alt.Y(y, scale=alt.Scale(domain=(1,5)))
        ),
        use_container_width=True
    )


st.title("Dish Reviews Dashboard")

ID_COLS = ["time", "restaurant", "dish"]
FOOD_COLS = ["food", "food_taste", "food_portion", "food_look"]

# @st.cache
# def get_data():
#     df = pd.read_json("reviews.json")
#     df["time"] = pd.to_datetime(df["time"])
#     return df

if "data" not in st.session_state:
    st.title("Loading Data")
    time.sleep(0.2)
    st.experimental_rerun()

for i in range(st.session_state.queue.qsize()):
    st.session_state.data.append(st.session_state.queue.get())

def get_data():
    df = pd.DataFrame.from_records(st.session_state.data)
    df["time"] = pd.to_datetime(df["time"])
    return df

raw_df = get_data()[ID_COLS + FOOD_COLS]
DISH_TYPES = list(raw_df["dish"].unique())
RESTAURANTS = list(raw_df["restaurant"].unique())

s_dish = st.sidebar.selectbox("Choose Dish", DISH_TYPES)
s_store = st.sidebar.selectbox("Choose Restaurant", ["All"] + RESTAURANTS)
df = raw_df[raw_df["dish"] == s_dish]
if s_store != "All":
    df = df[df["restaurant"] == s_store]

last_week = datetime.now() - timedelta(days=7)
df_week = df[df["time"] > last_week]
df_last_week = df[(df["time"] <= last_week) & (df["time"] > last_week - timedelta(days=7))]
st.subheader(f"Weekly Metrics for \"{s_dish}\"")

c0_0, c0_1, c0_2, c0_3, c0_4 = st.columns(5)
with c0_0:
    st.metric(
        "\# Reviews", 
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

c2_0, c2_1 = st.columns(2)
with c2_0:
    st.subheader("Raw Data")
    st.dataframe(raw_df, use_container_width=True)
with c2_1:
    st.subheader("Average Dish Ratings")
    st.dataframe(raw_df.groupby("dish").mean(numeric_only=True).sort_values(by="food", ascending=False), use_container_width=True)