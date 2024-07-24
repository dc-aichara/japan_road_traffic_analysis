import asyncio

import streamlit as st

from gpx_route_status.pipeline import get_closed_roads

st.set_page_config(layout="wide")

# Streamlit app title
st.title("GPX Route Viewer with Closed Roads")

# Upload GPX file
uploaded_file = st.file_uploader(
    "Upload your GPX file to check restricted roads on your route.",
    type=["gpx"]
)

# Interval selection
interval = st.sidebar.selectbox(
    "Select GPX Points Interval for road info check:",
    options=[200, 300, 400],
    index=2,  # Default selection (400)
)

# Process the uploaded file only if a file is uploaded
if uploaded_file is not None:
    try:
        info = st.empty()
        info.info("Processing your GPX file. This may take a few moments...")
        # Ensure the function is running in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        closed_roads, fig = loop.run_until_complete(
            get_closed_roads(
                gpx_file_path=uploaded_file,
                gpx_points_interval=interval,
            )
        )
        # loop.close()
        info.empty()
        st.subheader("GPX Route with Closed Sections Highlighted in Red")
        st.plotly_chart(fig)

        # Create and display dataframe of closed sections
        st.subheader("Restricted Roads Details")
        st.dataframe(closed_roads)

        # Download button for the closed roads data
        csv = closed_roads.to_csv(index=False)
        st.download_button(
            label="Download Restricted Roads Data",
            data=csv,
            file_name="closed_roads.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"An error occurred: {e}. Please try again with file upload.")
else:
    st.info("Please upload a GPX file to visualize the route and closed roads.")

# Data reference
st.markdown("""
    ---
    **Data References:**
    - OSM for road data
    - [JARTIC for live traffic data](https://www.jartic.or.jp/)
""")
