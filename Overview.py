from datetime import datetime, timedelta
import json
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
import altair as alt
import threading
from queue import Queue
from google.cloud import firestore

ID_COLS = ["time", "restaurant", "dish"]
SUMMARY_COLS = ["overall", "food", "service", "vibe"]

st.set_page_config(
    page_title="Overview Dashboard",
    layout="wide",
)
st_autorefresh(interval=3000, limit=100000)

if 'review_ref' not in st.session_state:
    st.session_state.data = []
    cred = st.secrets["firestore_credentials"]
    # with open("firebase_key.json") as secret:
    #     cred = json.load(secret)
    db = firestore.Client.from_service_account_info(cred)
    review_ref = db.collection('review_test')
    st.session_state.review_ref = review_ref
    queue = Queue()
    st.session_state.queue = queue
    def on_snapshot(snapshot, changes, read_time):
        print("Data Changed")
        for change in changes:
            if change.type.name == 'ADDED':
                queue.put(change.document.to_dict())
    review_ref.on_snapshot(on_snapshot)


if st.session_state.queue.qsize() > 0:
    print("data added")
for i in range(st.session_state.queue.qsize()):
    st.session_state.data.append(st.session_state.queue.get())
# st.write(len(st.session_state.data))

if not st.session_state.data:
    st.title("Loading Data")
    time.sleep(0.2)
    st.experimental_rerun()

# @st.cache
# def get_data():
#     df = pd.read_json("reviews.json")
#     df["time"] = pd.to_datetime(df["time"])
#     return df

def get_data():
    df = pd.DataFrame.from_records(st.session_state.data)
    df["time"] = pd.to_datetime(df["time"])
    return df

raw_df = get_data()[ID_COLS + SUMMARY_COLS]
DISH_TYPES = list(raw_df["dish"].unique())
RESTAURANTS = list(raw_df["restaurant"].unique())

s_store = st.sidebar.selectbox("Choose Restaurant", ["All"] + RESTAURANTS)
df = raw_df
if s_store != "All":
    df = df[df["restaurant"] == s_store]
last_week = datetime.now() - timedelta(days=7)
df_week = df[df["time"] > last_week]
df_last_week = df[(df["time"] <= last_week) & (df["time"] > last_week - timedelta(days=7))]
st.title("Overview Dashboard")

st.subheader(f"Weekly Metrics for \"{s_store}\"")

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
        f'{df_week["overall"].mean():.2f}',
        f'{df_week["overall"].mean() - df_last_week["overall"].mean():.3f}'
    )
with c0_2:
    st.metric(
        "Food", 
        f'{df_week["food"].mean():.2f}', 
        f'{df_week["food"].mean() - df_last_week["food"].mean():.3f}'
    )
with c0_3:
    st.metric(
        "Service", 
        f'{df_week["service"].mean():.2f}',
        f'{df_week["service"].mean() - df_last_week["service"].mean():.3f}'
    )
with c0_4:
    st.metric(
        "Vibe", 
        f'{df_week["vibe"].mean():.2f}',
        f'{df_week["vibe"].mean() - df_last_week["vibe"].mean():.3f}'
    )

s_rating = st.selectbox("Choose Rating", SUMMARY_COLS)
c1_0, c1_1 = st.columns(2)
with c1_0:
    st.header(f"{s_rating} Ratings by Hour of Day")
    df_hourly = df.groupby(df["time"].dt.hour).mean(numeric_only=True).reset_index()
    st.altair_chart(alt.Chart(df_hourly).mark_bar().encode(
            x='time:O',
            y=alt.Y(s_rating, scale=alt.Scale(domain=(0,5)))
        ),
        use_container_width=True
    )
with c1_1:
    st.header(f"{s_rating} Ratings by Day of Week")
    df_daily = df.groupby(df["time"].dt.day_of_week).mean(numeric_only=True).reset_index()
    # st.write(df_daily)
    # day_names =  [
    #     "Monday",
    #     "Tuesday",
    #     "Wednesday",
    #     "Thursday",
    #     "Friday",
    #     "Saturday",
    #     "Sunday"
    # ]
    # st.bar_chart(df_daily[s_rating])
    st.altair_chart(alt.Chart(df_daily).mark_bar().encode(
            x='time:O',
            y=alt.Y(s_rating, scale=alt.Scale(domain=(0,5), zero=False))
        ),
        use_container_width=True
    )
    # st.line_chart(df.groupby(df["time"].dt.day_of_week)["service"].mean(numeric_only=True))

df_resample = df.set_index("time").resample('D').mean(numeric_only=True).reset_index()
# st.header(f"{s_rating} Ratings Over Time")
# st.altair_chart(alt.Chart(df_resample).mark_line().encode(
#             x='time',
#             y=alt.Y(s_rating, scale=alt.Scale(domain=(0,5), zero=False))
#         ),
#         use_container_width=True
#     )

st.subheader("Ratings Over Time")
melt_df = pd.melt(
    df_resample, 
    id_vars=["time"]
)
st.altair_chart(alt.Chart(melt_df).mark_line().encode(
        x='time',
        y=alt.Y('value', scale=alt.Scale(domain=(1,5))),
        color="variable"
    ),
    use_container_width=True
)


c2_0, c2_1 = st.columns(2)
with c2_0:
    st.subheader("Raw Data")
    st.dataframe(raw_df, use_container_width=True)
with c2_1:
    st.subheader("Store averages")
    st.dataframe(raw_df.groupby("restaurant").mean(numeric_only=True).sort_values(by="overall", ascending=False), use_container_width=True)