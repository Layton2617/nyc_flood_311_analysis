"""
Interactive map module for NYC flood-related 311 complaints analysis.

This module provides functions to create interactive maps for flood-related
311 complaints in NYC, allowing hover information display and interactive exploration.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import json
import os
import branca.colormap as cm
from shapely.geometry import mapping

# Constants
DATA_DIR = "../data"
FIGURES_DIR = "../figures"
RESULTS_DIR = "../results"

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

def create_interactive_choropleth(gdf, column, title, filename, 
                                  fill_color='YlOrRd', legend_name=None):
    """
    Create an interactive choropleth map for a given column in a GeoDataFrame.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with geometries and data
        column (str): Column name to visualize
        title (str): Title for the map
        filename (str): Output filename (HTML)
        fill_color (str): Colormap name
        legend_name (str): Name for the legend
    """
    print(f"Creating interactive choropleth map for {column}...")
    
    # Create a copy to avoid modifying the original
    gdf_copy = gdf.copy()
    
    # Ensure the GeoDataFrame has the right CRS for Folium
    if gdf_copy.crs and gdf_copy.crs != "EPSG:4326":
        gdf_copy = gdf_copy.to_crs("EPSG:4326")
    
    # Calculate center of the map
    center = [gdf_copy.geometry.centroid.y.mean(), gdf_copy.geometry.centroid.x.mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Create a colormap
    if legend_name is None:
        legend_name = column
    
    # Get min and max values for the colormap
    vmin = gdf_copy[column].min()
    vmax = gdf_copy[column].max()
    
    # Create a colormap
    colormap = cm.LinearColormap(
        colors=['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#b10026'],
        vmin=vmin,
        vmax=vmax,
        caption=legend_name
    )
    
    # Add the colormap to the map
    m.add_child(colormap)
    
    # Define a function to style the features
    def style_function(feature):
        value = feature['properties'][column]
        return {
            'fillColor': colormap(value),
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    # Define a function to create popups
    def highlight_function(feature):
        return {
            'weight': 3,
            'color': 'black',
            'fillOpacity': 0.9
        }
    
    # Check available fields and adjust tooltip fields accordingly
    available_fields = list(gdf_copy.columns)
    tooltip_fields = [column, 'GEOID', 'median_income', 'pct_college']
    tooltip_aliases = [column, 'Census Tract', 'Median Income', 'College Education (%)']
    
    # Add pct_minority if available
    if 'pct_minority' in available_fields:
        tooltip_fields.append('pct_minority')
        tooltip_aliases.append('Minority (%)')
    
    # Convert the GeoDataFrame to GeoJSON
    geojson_data = json.loads(gdf_copy.to_json())
    
    # Add the GeoJSON layer to the map
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        ),
    ).add_to(m)
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_interactive_heatmap(df, title, filename, radius=15, blur=10):
    """
    Create an interactive heatmap of complaint locations.
    
    Args:
        df (pd.DataFrame): DataFrame with Latitude and Longitude columns
        title (str): Title for the map
        filename (str): Output filename (HTML)
        radius (int): Radius of each point in the heatmap
        blur (int): Amount of blur in the heatmap
    """
    print("Creating interactive heatmap...")
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Calculate center of the map
    center = [df_copy['Latitude'].mean(), df_copy['Longitude'].mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Create the heatmap
    heat_data = [[row['Latitude'], row['Longitude']] for _, row in df_copy.iterrows()]
    HeatMap(heat_data, radius=radius, blur=blur, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_interactive_complaint_map(df, title, filename, cluster=True):
    """
    Create an interactive map with markers for each complaint.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data
        title (str): Title for the map
        filename (str): Output filename (HTML)
        cluster (bool): Whether to cluster markers
    """
    print("Creating interactive complaint map...")
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Calculate center of the map
    center = [df_copy['Latitude'].mean(), df_copy['Longitude'].mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Create a marker cluster if requested
    if cluster:
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each complaint
    for _, row in df_copy.sample(min(5000, len(df_copy))).iterrows():
        popup_text = f"""
        <b>Complaint Type:</b> {row['Complaint Type']}<br>
        <b>Created Date:</b> {row['Created Date']}<br>
        <b>Status:</b> {row['Status']}<br>
        <b>Address:</b> {row.get('Incident Address', 'N/A')}<br>
        <b>ZIP Code:</b> {row.get('Incident Zip', 'N/A')}<br>
        """
        
        popup = folium.Popup(popup_text, max_width=300)
        
        if cluster:
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup,
                tooltip=row['Complaint Type'],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)
        else:
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup,
                tooltip=row['Complaint Type'],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_bivariate_interactive_map(gdf, var1, var2, var1_name, var2_name, title, filename):
    """
    Create an interactive bivariate map showing the relationship between two variables.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with geometries and data
        var1 (str): First variable column name
        var2 (str): Second variable column name
        var1_name (str): Display name for first variable
        var2_name (str): Display name for second variable
        title (str): Title for the map
        filename (str): Output filename (HTML)
    """
    print(f"Creating interactive bivariate map for {var1} vs {var2}...")
    
    # Create a copy to avoid modifying the original
    gdf_copy = gdf.copy()
    
    # Ensure the GeoDataFrame has the right CRS for Folium
    if gdf_copy.crs and gdf_copy.crs != "EPSG:4326":
        gdf_copy = gdf_copy.to_crs("EPSG:4326")
    
    # Calculate center of the map
    center = [gdf_copy.geometry.centroid.y.mean(), gdf_copy.geometry.centroid.x.mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Normalize the variables
    gdf_copy[f'{var1}_norm'] = (gdf_copy[var1] - gdf_copy[var1].min()) / (gdf_copy[var1].max() - gdf_copy[var1].min())
    gdf_copy[f'{var2}_norm'] = (gdf_copy[var2] - gdf_copy[var2].min()) / (gdf_copy[var2].max() - gdf_copy[var2].min())
    
    # Define a function to determine color based on both variables
    def get_color(var1_val, var2_val):
        # Both low
        if var1_val < 0.33 and var2_val < 0.33:
            return '#e8e8e8'  # Light gray
        # Low var1, high var2
        elif var1_val < 0.33 and var2_val >= 0.66:
            return '#73ae80'  # Green
        # High var1, low var2
        elif var1_val >= 0.66 and var2_val < 0.33:
            return '#6c83b5'  # Blue
        # Both high
        elif var1_val >= 0.66 and var2_val >= 0.66:
            return '#2a5a5b'  # Dark teal
        # Medium values
        else:
            return '#b8d6be' if var2_val > var1_val else '#b5c0da'  # Light green or light blue
    
    # Add color to the GeoDataFrame
    gdf_copy['color'] = gdf_copy.apply(lambda row: get_color(row[f'{var1}_norm'], row[f'{var2}_norm']), axis=1)
    
    # Define a function to style the features
    def style_function(feature):
        return {
            'fillColor': feature['properties']['color'],
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    # Define a function for hover styling
    def highlight_function(feature):
        return {
            'weight': 3,
            'color': 'black',
            'fillOpacity': 0.9
        }
    
    # Check available fields and adjust tooltip fields accordingly
    tooltip_fields = [var1, var2, 'GEOID', 'pct_college']
    tooltip_aliases = [var1_name, var2_name, 'Census Tract', 'College Education (%)']
    
    # Add pct_minority if available
    if 'pct_minority' in gdf_copy.columns:
        tooltip_fields.append('pct_minority')
        tooltip_aliases.append('Minority (%)')
    
    # Convert the GeoDataFrame to GeoJSON
    geojson_data = json.loads(gdf_copy.to_json())
    
    # Add the GeoJSON layer to the map
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        ),
    ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; background-color: white; 
                padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <p><b>Legend</b></p>
        <div style="display: grid; grid-template-columns: auto auto; grid-gap: 5px;">
            <div style="background-color: #e8e8e8; width: 20px; height: 20px; border: 1px solid black;"></div>
            <div>Low {0}, Low {1}</div>
            <div style="background-color: #73ae80; width: 20px; height: 20px; border: 1px solid black;"></div>
            <div>Low {0}, High {1}</div>
            <div style="background-color: #6c83b5; width: 20px; height: 20px; border: 1px solid black;"></div>
            <div>High {0}, Low {1}</div>
            <div style="background-color: #2a5a5b; width: 20px; height: 20px; border: 1px solid black;"></div>
            <div>High {0}, High {1}</div>
        </div>
    </div>
    '''.format(var1_name, var2_name)
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_interactive_maps(complaints_df, aggregated_gdf):
    """
    Create all interactive maps for the analysis.
    
    Args:
        complaints_df (pd.DataFrame): DataFrame with complaint data
        aggregated_gdf (gpd.GeoDataFrame): GeoDataFrame with aggregated complaint data
    """
    # Ensure directories exist
    ensure_dirs()
    
    # Create interactive choropleth maps
    create_interactive_choropleth(
        aggregated_gdf,
        'complaint_count',
        'NYC Flood-Related 311 Complaints (2019) - Count by Census Tract',
        'interactive_flood_complaints_count.html',
        legend_name='Complaint Count'
    )
    
    create_interactive_choropleth(
        aggregated_gdf,
        'complaint_rate',
        'NYC Flood-Related 311 Complaints (2019) - Rate by Census Tract',
        'interactive_flood_complaints_rate.html',
        legend_name='Complaint Rate (per 1000 people)'
    )
    
    # Create interactive heatmap
    create_interactive_heatmap(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Heatmap',
        'interactive_flood_complaints_heatmap.html'
    )
    
    # Create interactive complaint map
    create_interactive_complaint_map(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Individual Complaints',
        'interactive_flood_complaints_markers.html'
    )
    
    # Create bivariate map
    create_bivariate_interactive_map(
        aggregated_gdf,
        'complaint_rate',
        'median_income',
        'Complaint Rate',
        'Median Income',
        'NYC Flood Complaints vs Median Income',
        'interactive_flood_complaints_vs_income.html'
    )

if __name__ == "__main__":
    # Load processed data
    complaints_df = pd.read_csv(os.path.join(DATA_DIR, "processed", "flood_complaints_2019.csv"))
    aggregated_gdf = gpd.read_file(os.path.join(DATA_DIR, "processed", "aggregated_flood_complaints_2019.geojson"))
    
    # Print available columns to debug
    print("Available columns in aggregated_gdf:", aggregated_gdf.columns.tolist())
    
    # Create interactive maps
    create_interactive_maps(complaints_df, aggregated_gdf)
