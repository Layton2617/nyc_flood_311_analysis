"""
Point-based interactive map module for NYC flood-related 311 complaints analysis.

This module provides functions to create interactive maps showing individual complaint points
for flood-related 311 complaints in NYC, allowing hover information display and interactive exploration.
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

def create_point_interactive_map(df, title, filename, cluster=True, max_points=None):
    """
    Create an interactive map with markers for each complaint point.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data including Latitude and Longitude
        title (str): Title for the map
        filename (str): Output filename (HTML)
        cluster (bool): Whether to cluster markers for better performance
        max_points (int): Maximum number of points to display (None for all)
    
    Returns:
        folium.Map: The interactive map object
    """
    print(f"Creating point-based interactive map: {title}...")
    
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
        
        # Create popup and tooltip
        popup = folium.Popup(popup_content, max_width=300)
        tooltip = f"{row['Complaint Type']}"
        
        # Determine marker color based on complaint status
        if row['Status'] == 'Closed':
            color = 'green'
        elif row['Status'] == 'Open':
            color = 'red'
        elif row['Status'] == 'Pending':
            color = 'orange'
        else:
            color = 'blue'
        
        # Create and add marker
        marker = folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=popup,
            tooltip=tooltip,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1
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
            <div style="background-color: green; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Closed</div>
            <div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Open</div>
            <div style="background-color: orange; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Pending</div>
            <div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Other Status</div>
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_fast_point_map(df, title, filename, max_points=None):
    """
    Create a fast-rendering interactive map with many points using FastMarkerCluster.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data including Latitude and Longitude
        title (str): Title for the map
        filename (str): Output filename (HTML)
        max_points (int): Maximum number of points to display (None for all)
    
    Returns:
        folium.Map: The interactive map object
    """
    print(f"Creating fast point-based interactive map: {title}...")
    
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
    
    # Create a callback function for the FastMarkerCluster
    callback = """
    function (row) {
        var marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
            radius: 5,
            color: row[2],
            fillColor: row[2],
            fillOpacity: 0.7,
            weight: 1
        });
        marker.bindTooltip(row[3]);
        return marker;
    };
    """
    
    # Prepare data for FastMarkerCluster
    data = []
    for idx, row in df_copy.iterrows():
        # Determine marker color based on complaint status
        if row['Status'] == 'Closed':
            color = 'green'
        elif row['Status'] == 'Open':
            color = 'red'
        elif row['Status'] == 'Pending':
            color = 'orange'
        else:
            color = 'blue'
        
        # Add data point: [lat, lng, color, tooltip]
        data.append([row['Latitude'], row['Longitude'], color, row['Complaint Type']])
    
    # Add FastMarkerCluster to the map
    FastMarkerCluster(data, callback=callback).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; background-color: white; 
                padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <p><b>Legend</b></p>
        <div style="display: grid; grid-template-columns: auto auto; grid-gap: 5px;">
            <div style="background-color: green; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Closed</div>
            <div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Open</div>
            <div style="background-color: orange; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Pending</div>
            <div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Other Status</div>
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_category_point_map(df, category_column, title, filename, cluster=True, max_points=None):
    """
    Create an interactive map with points colored by category.
    
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
    print(f"Creating category-based point map: {title}...")
    
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
        
        # Create and add marker
        marker = folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=popup,
            tooltip=tooltip,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1
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
            <div style="background-color: {color}; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
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

def create_time_animated_map(df, title, filename, time_column='Created Date', time_format='%Y-%m-%d', max_points=None):
    """
    Create an interactive map with time animation for points.
    
    Args:
        df (pd.DataFrame): DataFrame with complaint data including Latitude and Longitude
        title (str): Title for the map
        filename (str): Output filename (HTML)
        time_column (str): Column name containing time data
        time_format (str): Format of the time data
        max_points (int): Maximum number of points to display (None for all)
    
    Returns:
        folium.Map: The interactive map object
    """
    print(f"Creating time-animated point map: {title}...")
    
    # Import TimestampedGeoJson
    from folium.plugins import TimestampedGeoJson
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Ensure time column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df_copy[time_column]):
        df_copy[time_column] = pd.to_datetime(df_copy[time_column])
    
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
    
    # Prepare features for TimestampedGeoJson
    features = []
    
    for idx, row in df_copy.iterrows():
        # Format time for TimestampedGeoJson
        time_str = row[time_column].strftime(time_format)
        
        # Determine marker color based on complaint status
        if row['Status'] == 'Closed':
            color = 'green'
        elif row['Status'] == 'Open':
            color = 'red'
        elif row['Status'] == 'Pending':
            color = 'orange'
        else:
            color = 'blue'
        
        # Create feature
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['Longitude'], row['Latitude']]
            },
            'properties': {
                'time': time_str,
                'popup': f"{row['Complaint Type']}<br>{time_str}<br>Status: {row['Status']}",
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.7,
                    'stroke': True,
                    'radius': 5,
                    'weight': 1,
                    'color': color
                }
            }
        }
        
        features.append(feature)
    
    # Add TimestampedGeoJson to map
    TimestampedGeoJson(
        {
            'type': 'FeatureCollection',
            'features': features
        },
        period='P1D',  # One day per step
        duration='P1D',  # Show points for one day
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY-MM-DD',
        time_slider_drag_update=True
    ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 100px; right: 50px; z-index: 1000; background-color: white; 
                padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <p><b>Legend</b></p>
        <div style="display: grid; grid-template-columns: auto auto; grid-gap: 5px;">
            <div style="background-color: green; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Closed</div>
            <div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Open</div>
            <div style="background-color: orange; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Pending</div>
            <div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%; border: 1px solid black;"></div>
            <div>Other Status</div>
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(os.path.join(FIGURES_DIR, filename))
    
    return m

def create_all_point_maps(complaints_df):
    """
    Create all point-based interactive maps for the analysis.
    
    Args:
        complaints_df (pd.DataFrame): DataFrame with complaint data
    """
    # Ensure directories exist
    ensure_dirs()
    
    # Create basic point map with clustering
    create_point_interactive_map(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Individual Points',
        'interactive_flood_complaints_points.html',
        cluster=True,
        max_points=10000  # Limit for better performance
    )
    
    # Create fast point map for larger datasets
    create_fast_point_map(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - All Points (Fast Rendering)',
        'interactive_flood_complaints_fast_points.html',
        max_points=20000  # Limit for better performance
    )
    
    # Create category-based point map
    create_category_point_map(
        complaints_df,
        'Complaint Type',
        'NYC Flood-Related 311 Complaints (2019) - By Complaint Type',
        'interactive_flood_complaints_by_type.html',
        cluster=True,
        max_points=10000  # Limit for better performance
    )
    
    # Create time-animated map
    create_time_animated_map(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Time Animation',
        'interactive_flood_complaints_time_animation.html',
        time_column='Created Date',
        max_points=5000  # Limit for better performance
    )

if __name__ == "__main__":
    # Load processed data
    complaints_df = pd.read_csv(os.path.join(DATA_DIR, "processed", "flood_complaints_2019.csv"))
    
    # Create all point-based interactive maps
    create_all_point_maps(complaints_df)
