import streamlit as st
import plotly.express as px
import plotly

import pandas as pd

st.set_page_config(layout="wide")
st.title("Syria Agriculture Monitoring")
st.markdown("***")

crop_data = pd.read_parquet("data/syria_crop_data_cleaned.parquet")

crop_production_df = crop_data.loc[crop_data["Element"] == "Production"]

crop_production_stats = (
    crop_production_df.groupby(by="Item", as_index=False)
    .aggregate(n_years=pd.NamedAgg(column="Year", aggfunc="nunique"))
    .sort_values(by="n_years", ascending=False)
)

crop_items_to_ignore = crop_production_stats.loc[
    crop_production_stats["n_years"] != 60, "Item"
].values

crop_production_df = crop_production_df.loc[
    ~crop_production_df["Item"].isin(crop_items_to_ignore)
]

total_production_by_item = (
    crop_production_df.loc[crop_production_df["Unit"] == "tonnes"]
    .groupby(by="Item", as_index=False)
    .aggregate(total_production=pd.NamedAgg(column="Value", aggfunc="sum"))
    .sort_values(by="total_production", ascending=False)
)

fig = px.line(
    data_frame=crop_production_df.loc[
        crop_production_df["Item"].isin(total_production_by_item.iloc[:5, 0])
    ],
    x="Year",
    y="Value",
    color="Item",
    title="Yearly crop production data (measured in tonnes)",
    labels={"Item": "Crop"},
    height=600,
)

ndvi_mapbox_choropleth_fig = plotly.io.read_json(
    "figures/ndvi-mapbox-choropleth-map.json"
)

with st.container():
    st.write("## Yearly crop production for top 5 regional crops")

    st.plotly_chart(fig, use_container_width=True, sharing="streamlit")

st.markdown("***")

with st.container():
    st.write("# NDVI values over the last 20 years")

    st.write(
        "[NDVI](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) values reflects greenness of a region. Lower values indicates more drought conditions."
    )

    st.write("Use the slider below to switch between years")

    st.plotly_chart(
        ndvi_mapbox_choropleth_fig,
        use_container_width=True,
        sharing="streamlit",
        config={"scrollZoom": False, "displayModeBar": False},
    )
