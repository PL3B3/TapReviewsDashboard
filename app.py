from datetime import datetime, timedelta
import json
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

NONE = "No Selection"
ID_COLS = ["time", "restaurant", "dish"]
SUMMARY_COLS = ["overall", "food", "service", "vibe"]

@st.cache
def get_data():
    df = pd.read_json("reviews.json")
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
    st.dataframe(raw_df.groupby("restaurant").mean().sort_values(by="overall", ascending=False), use_container_width=True)

# df[df["dish"] == dish_name]
# df[df["time"].dt.hour == 9]

# df["time"].dt.hour