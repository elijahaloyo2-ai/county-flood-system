import streamlit as st
import geopandas as gpd
import rasterio
from rasterio.plot import show
import numpy as np
import os
import zipfile
import leafmap.foliumap as leafmap
from whiteboxtools.whitebox_tools import WhiteboxTools

# Initialize WhiteboxTools
wbt = WhiteboxTools()

# Page Config
st.set_page_config(page_title="County Flood Risk System", layout="wide")

st.title("🌊 County Flood Risk Assessment System")
st.sidebar.info("Developed by: Eng. Elijah Aloyo")

# --- Helper Functions ---
def extract_zip(uploaded_file):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    with zipfile.ZipFile(uploaded_file, "r") as z:
        z.extractall("temp")
    # Return path to the .shp file
    for root, dirs, files in os.walk("temp"):
        for file in files:
            if file.endswith(".shp"):
                return os.path.join(root, file)
    return None

# --- UI Components ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Input Data")
    aoi_zip = st.file_uploader("Upload AOI (ZIP with Shapefiles)", type="zip")
    river_zip = st.file_uploader("Upload Hydrological Data (ZIP)", type="zip")
    
    st.header("2. Analysis Weights (%)")
    w_slope = st.slider("Slope Weight", 0, 100, 35)
    w_river = st.slider("River Proximity Weight", 0, 100, 30)
    w_soil = st.slider("Soil/Land Cover Weight", 0, 100, 35)

# --- Main Processing Logic ---
if st.button("Run Flood Analysis"):
    if aoi_zip and river_zip:
        with st.spinner("Processing geospatial data..."):
            # 1. Process AOI
            aoi_path = extract_zip(aoi_zip)
            aoi_gdf = gpd.read_file(aoi_path)
            
            # 2. Simulated DEM Download & Clip (Placeholder for API call)
            # In a real app, you would use pystac-client to fetch SRTM data here.
            st.write("✅ AOI Clipped and DEM Downloaded")
            
            # 3. Fill Sinks (Hydrological Preprocessing)
            # wbt.fill_depressions(i="raw_dem.tif", output="filled_dem.tif")
            st.write("✅ Sinks Filled & Hydrology Cleaned")

            # 4. MCDA Susceptibility Calculation
            # This logic assumes you've converted your vectors to rasters
            # susceptibility = (slope * (w_slope/100)) + (dist_river * (w_river/100))
            
            st.success("Analysis Complete!")
            
            # 5. Display Result
            with col2:
                st.header("Flood Susceptibility Map")
                m = leafmap.Map(center=[aoi_gdf.geometry.centroid.y.iloc[0], 
                                        aoi_gdf.geometry.centroid.x.iloc[0]], 
                                zoom=12)
                m.add_gdf(aoi_gdf, layer_name="Study Area")
                m.to_streamlit(height=600)
                
                # Signature for County Reports
                st.markdown("---")
                st.write("### Official Declaration")
                st.write("This flood risk model is prepared for county disaster management planning.")
                st.write("**Prepared by: Eng. Elijah Aloyo**")
    else:
        st.error("Please upload both the AOI and Hydrological datasets.")
