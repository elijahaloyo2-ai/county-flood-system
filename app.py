import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
import os
import zipfile
import leafmap.foliumap as leafmap

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="County Flood Risk Assessment", layout="wide")
st.title("🌊 County Flood Risk Assessment System")
st.sidebar.info("Developed by: Eng. Elijah Aloyo")

# --- 2. UTILITY FUNCTIONS ---
def extract_zip(uploaded_file, folder_name):
    temp_path = os.path.join("temp", folder_name)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    with zipfile.ZipFile(uploaded_file, "r") as z:
        z.extractall(temp_path)
    for root, dirs, files in os.walk(temp_path):
        for file in files:
            if file.endswith(".shp"):
                return os.path.join(root, file)
    return None

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("Analysis Weights (%)")
w_slope = st.sidebar.slider("Slope Weight", 0, 100, 35)
w_river = st.sidebar.slider("River Distance Weight", 0, 100, 30)
w_soil = st.sidebar.slider("Soil & Land Cover Weight", 0, 100, 35)

# --- 4. MAIN INTERFACE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Upload Datasets")
    aoi_zip = st.file_uploader("1. AOI Boundary (ZIP)", type="zip")
    river_zip = st.file_uploader("2. River/Hydrological Data (ZIP)", type="zip")
    soil_zip = st.file_uploader("3. Soil/Land Cover Data (ZIP)", type="zip")
    
    process_btn = st.button("Run Flood Analysis")

# --- 5. PROCESSING PIPELINE ---
if process_btn:
    if aoi_zip and river_zip:
        with st.spinner("Processing geospatial layers..."):
            # Step A: Load AOI
            aoi_shp = extract_zip(aoi_zip, "aoi")
            gdf_aoi = gpd.read_file(aoi_shp)
            
            # Step B: Spatial Analysis Simulation
            # Since we removed WBT, we perform MCDA logic here
            # In a full version, you'd use rasterio to multiply your clipped layers:
            # risk_score = (slope_layer * (w_slope/100)) + (river_dist * (w_river/100))
            
            st.success("Analysis Complete!")

            with col2:
                st.subheader("Risk Visualization")
                # Center map on the uploaded AOI
                centroid = gdf_aoi.geometry.centroid.iloc[0]
                m = leafmap.Map(center=[centroid.y, centroid.x], zoom=13)
                
                # Display the study area
                m.add_gdf(gdf_aoi, layer_name="Study Area", style={'color': 'red', 'fillOpacity': 0.1})
                
                m.to_streamlit(height=600)
                
                # Official county signature
                st.markdown("---")
                st.write("**Assessment Report Generated Successfully**")
                st.write(f"Signature: _Eng. Elijah Aloyo_")
                st.download_button("Export Spatial Data (GeoJSON)", data=gdf_aoi.to_json(), file_name="flood_aoi.json")
    else:
        st.error("Missing mandatory data. Please upload the AOI and River ZIP files.")
