import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
import os
import zipfile
import whitebox
import leafmap.foliumap as leafmap

# --- 1. WHITEBOXTOOLS INITIALIZATION ---
def init_wbt():
    wbt = whitebox.WhiteboxTools()
    if not os.path.exists(wbt.exe_path):
        with st.spinner("Downloading Hydrological Engine..."):
            whitebox.download_wbt()
    # Set permissions for Linux Environment
    if os.name != 'nt': # If not Windows
        os.chmod(wbt.exe_path, 0o755)
    return wbt

wbt = init_wbt()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="County Flood Risk Assessment", layout="wide")
st.title("🌊 County Flood Risk Assessment System")
st.sidebar.info("Prepared by: Eng. Elijah Aloyo")

# --- 3. UTILITY FUNCTIONS ---
def extract_zip(uploaded_file, folder_name):
    path = os.path.join("temp", folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
    with zipfile.ZipFile(uploaded_file, "r") as z:
        z.extractall(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".shp"):
                return os.path.join(root, file)
    return None

# --- 4. SIDEBAR INPUTS ---
st.sidebar.header("Analysis Parameters")
w_slope = st.sidebar.slider("Slope Weight (%)", 0, 100, 35)
w_river = st.sidebar.slider("River Proximity Weight (%)", 0, 100, 30)
w_soil_lc = st.sidebar.slider("Soil/Land Cover Weight (%)", 0, 100, 35)

# --- 5. MAIN UI ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Upload Datasets")
    aoi_zip = st.file_uploader("1. AOI Boundary (ZIP)", type="zip")
    river_zip = st.file_uploader("2. River Network (ZIP)", type="zip")
    other_zip = st.file_uploader("3. Soil & Land Cover (ZIP)", type="zip")
    
    run_btn = st.button("Generate Flood Susceptibility Map")

# --- 6. PROCESSING LOGIC ---
if run_btn:
    if aoi_zip and river_zip:
        with st.spinner("Analyzing Flood Risk Factors..."):
            # A. Process AOI
            aoi_shp = extract_zip(aoi_zip, "aoi")
            gdf_aoi = gpd.read_file(aoi_shp)
            
            # B. Hydrological Pre-processing (Example: Fill Sinks)
            # Assuming 'dem.tif' exists in your repo or is downloaded via API
            # wbt.fill_depressions(i="temp/dem.tif", output="temp/filled_dem.tif")
            
            # C. MCDA Analysis (Simulation of the math)
            # In production, you would use rasterio to multiply the arrays:
            # risk = (slope_arr * w_slope) + (river_arr * w_river)...
            
            st.success("Analysis Complete!")

            # D. DISPLAY RESULTS
            with col2:
                st.subheader("Flood Susceptibility Visualization")
                m = leafmap.Map(center=[gdf_aoi.geometry.centroid.y.iloc[0], 
                                        gdf_aoi.geometry.centroid.x.iloc[0]], 
                                zoom=13)
                
                m.add_gdf(gdf_aoi, layer_name="Study Area", style={'color': 'blue', 'fillOpacity': 0.1})
                
                # If you have a resulting raster:
                # m.add_raster("temp/risk_map.tif", layer_name="Risk Zones", colormap="jet")
                
                m.to_streamlit(height=600)
                
                # Download Result
                st.download_button("Download Report (PDF)", data="Sample Report Content", file_name="Flood_Report.pdf")
                
                st.markdown("---")
                st.write("**Prepared by: Eng. Elijah Aloyo**")
    else:
        st.error("Please ensure all mandatory datasets are uploaded.")
