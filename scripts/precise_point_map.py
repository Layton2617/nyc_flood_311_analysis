"""
Precise point-based interactive map module for NYC flood-related 311 complaints analysis.

This module provides functions to create interactive maps showing individual complaint points
with precise small markers for flood-related 311 complaints in NYC, allowing hover information 
display and interactive exploration.
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster, FastMarkerCluster
import os
import branca.colormap as cm
import random

# Constants
DATA_DIR = "../data"
FIGURES_DIR = "../figures"
RESULTS_DIR = "../results"

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

def create_precise_point_map(df, title, filename, cluster=False, max_points=None):
    """
    Create an interactive map with precise small markers for each complaint point.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data including Latitude and Longitude
        title (str): Title for the map
        filename (str): Output filename (HTML)
        cluster (bool): Whether to cluster markers for better performance
        max_points (int): Maximum number of points to display (None for all)
    
    Returns:
        folium.Map: The interactive map object
    """
    print(f"Creating precise point-based interactive map: {title}...")
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Limit points if specified
    if max_points is not None and len(df_copy) > max_points:
        df_copy = df_copy.sample(max_points, random_state=42)
    
    # Calculate center of the map
    center = [df_copy['Latitude'].mean(), df_copy['Longitude'].mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Create a marker cluster if requested (for better performance with many points)
    if cluster:
        marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each complaint
    for idx, row in df_copy.iterrows():
        # Create popup content with complaint details
        popup_content = f"""
        <div style="width: 300px;">
            <h4>Complaint Details</h4>
            <b>Complaint Type:</b> {row['Complaint Type']}<br>
            <b>Created Date:</b> {row['Created Date']}<br>
            <b>Status:</b> {row['Status']}<br>
            <b>Address:</b> {row.get('Incident Address', 'N/A')}<br>
            <b>ZIP Code:</b> {row.get('Incident Zip', 'N/A')}<br>
        </div>
        """
        
        # Create popup and tooltip with detailed information
        popup = folium.Popup(popup_content, max_width=300)
        # Create a more compact tooltip that works better with folium's hover display
        tooltip = f"类型: {row['Complaint Type']} | 状态: {row['Status']} | 日期: {row['Created Date'].split()[0]}"
        
        # Determine marker color based on complaint status
        if row['Status'] == 'Closed':
            color = 'green'
        elif row['Status'] == 'Open':
            color = 'red'
        elif row['Status'] == 'Pending':
            color = 'orange'
        else:
            color = 'blue'
        
        # Create and add marker with very small radius for precise point display
        marker = folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=1,  # Very small radius for precise point display
            popup=popup,
            tooltip=tooltip,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,  # High opacity for better visibility despite small size
            weight=0.5  # Thin border
        )
        
        # Add to cluster or directly to map
        if cluster:
            marker.add_to(marker_cluster)
        else:
            marker.add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; background-color: white; 
                padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <p><b>Legend</b></p>
        <div style="display: grid; grid-template-columns: auto auto; grid-gap: 5px;">
            <div style="background-color: green; width: 10px; height: 10px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Closed</div>
            <div style="background-color: red; width: 10px; height: 10px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Open</div>
            <div style="background-color: orange; width: 10px; height: 10px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Pending</div>
            <div style="background-color: blue; width: 10px; height: 10px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Other Status</div>
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_precise_category_point_map(df, category_column, title, filename, cluster=False, max_points=None):
    """
    Create an interactive map with precise small points colored by category.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data including Latitude and Longitude
        category_column (str): Column name to use for categorization
        title (str): Title for the map
        filename (str): Output filename (HTML)
        cluster (bool): Whether to cluster markers for better performance
        max_points (int): Maximum number of points to display (None for all)
    
    Returns:
        folium.Map: The interactive map object
    """
    print(f"Creating precise category-based point map: {title}...")
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Limit points if specified
    if max_points is not None and len(df_copy) > max_points:
        df_copy = df_copy.sample(max_points, random_state=42)
    
    # Calculate center of the map
    center = [df_copy['Latitude'].mean(), df_copy['Longitude'].mean()]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Get unique categories
    categories = df_copy[category_column].unique()
    
    # Create a color map for categories
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
              'darkpurple', 'pink', 'lightblue', 'lightgreen']
    
    # If we have more categories than colors, cycle through colors
    category_colors = {}
    for i, category in enumerate(categories):
        category_colors[category] = colors[i % len(colors)]
    
    # Create a marker cluster if requested
    if cluster:
        marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each complaint
    for idx, row in df_copy.iterrows():
        category = row[category_column]
        color = category_colors[category]
        
        # Create popup content with complaint details
        popup_content = f"""
        <div style="width: 300px;">
            <h4>Complaint Details</h4>
            <b>{category_column}:</b> {category}<br>
            <b>Created Date:</b> {row['Created Date']}<br>
            <b>Status:</b> {row['Status']}<br>
            <b>Address:</b> {row.get('Incident Address', 'N/A')}<br>
            <b>ZIP Code:</b> {row.get('Incident Zip', 'N/A')}<br>
        </div>
        """
        
        # Create popup and tooltip
        popup = folium.Popup(popup_content, max_width=300)
        tooltip = f"{category}"
        
        # Create and add marker with very small radius for precise point display
        marker = folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=1,  # Very small radius for precise point display
            popup=popup,
            tooltip=tooltip,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,  # High opacity for better visibility despite small size
            weight=0.5  # Thin border
        )
        
        # Add to cluster or directly to map
        if cluster:
            marker.add_to(marker_cluster)
        else:
            marker.add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; background-color: white; 
                padding: 10px; border: 2px solid grey; border-radius: 5px; max-height: 300px; overflow-y: auto;">
        <p><b>Legend</b></p>
        <div style="display: grid; grid-template-columns: auto auto; grid-gap: 5px;">
    '''
    
    # Add each category to the legend
    for category, color in category_colors.items():
        legend_html += f'''
            <div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%; border: 1px solid black;"></div>
            <div>{category}</div>
        '''
    
    legend_html += '''
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

if __name__ == "__main__":
    # Test with sample data
    ensure_dirs()
    
    # Load processed data if available
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "processed", "flood_complaints_2019.csv"))
        
        # Create precise point maps
        create_precise_point_map(
            df, 
            'NYC Flood-Related 311 Complaints (2019) - Precise Points', 
            'precise_flood_complaints_points.html',
            cluster=False,
            max_points=10000
        )
        
        create_precise_category_point_map(
            df,
            'Complaint Type',
            'NYC Flood-Related 311 Complaints (2019) - Precise Points by Type',
            'precise_flood_complaints_by_type.html',
            cluster=False,
            max_points=10000
        )
        
        print("Precise point maps created successfully!")
    except Exception as e:
        print(f"Error creating precise point maps: {e}")
