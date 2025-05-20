"""
Visualization module for NYC flood-related 311 complaints analysis.

This module provides functions to create various visualizations for flood-related
311 complaints in NYC, including choropleth maps, pixel maps, and bivariate maps.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

# Constants
DATA_DIR = "../data"
FIGURES_DIR = "../figures"

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

def create_choropleth_map(gdf, column, title, filename, cmap='viridis', figsize=(12, 10)):
    """
    Create a choropleth map for a given column in a GeoDataFrame.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with geometries and data
        column (str): Column name to visualize
        title (str): Title for the map
        filename (str): Output filename
        cmap (str): Colormap name
        figsize (tuple): Figure size
    """
    print(f"Creating choropleth map for {column}...")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the choropleth map
    gdf.plot(column=column, cmap=cmap, linewidth=0.2, ax=ax, edgecolor='0.8', legend=True)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add a basemap (simplified)
    ax.set_facecolor('lightblue')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_simplified_pixel_map(gdf, column, title, filename, resolution=50, cmap='viridis', figsize=(12, 10)):
    """
    Create a simplified pixel map for a given column in a GeoDataFrame.
    This version avoids complex spatial joins and uses a simpler approach.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with geometries and data
        column (str): Column name to visualize
        title (str): Title for the map
        filename (str): Output filename
        resolution (int): Resolution of the pixel grid
        cmap (str): Colormap name
        figsize (tuple): Figure size
    """
    print(f"Creating simplified pixel map for {column}...")
    
    # Get the bounds of the data
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Create a grid
    cell_width = (maxx - minx) / resolution
    cell_height = (maxy - miny) / resolution
    
    # Initialize an empty grid
    grid = np.zeros((resolution, resolution))
    
    # For each polygon in the GeoDataFrame, find which cells it intersects
    for _, row_data in gdf.iterrows():
        # Get the bounds of this polygon
        if hasattr(row_data, 'geometry') and row_data.geometry is not None:
            p_minx, p_miny, p_maxx, p_maxy = row_data.geometry.bounds
        elif 'geometry' in row_data and row_data['geometry'] is not None:
            p_minx, p_miny, p_maxx, p_maxy = row_data['geometry'].bounds
        else:
            continue  # Skip if no valid geometry
        
        # Calculate which cells this polygon might intersect
        min_col = max(0, int((p_minx - minx) / cell_width))
        max_col = min(resolution - 1, int((p_maxx - minx) / cell_width))
        min_row = max(0, int((p_miny - miny) / cell_height))
        max_row = min(resolution - 1, int((p_maxy - miny) / cell_height))
        
        # For each potential cell, assign the value
        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                # Simply assign the value to the cell
                # This is a simplification that doesn't check for actual intersection
                grid[row, col] = max(grid[row, col], row_data[column])
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the pixel map
    im = ax.imshow(grid, cmap=cmap, origin='lower', 
                  extent=[minx, maxx, miny, maxy])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(column)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_heatmap(df, title, filename, figsize=(12, 10)):
    """
    Create a heatmap of complaint locations.
    
    Args:
        df (pd.DataFrame): DataFrame with Latitude and Longitude columns
        title (str): Title for the map
        filename (str): Output filename
        figsize (tuple): Figure size
    """
    print("Creating heatmap...")
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the heatmap
    hb = ax.hexbin(df['Longitude'], df['Latitude'], gridsize=100, cmap='YlOrRd')
    
    # Add colorbar
    cb = plt.colorbar(hb, ax=ax)
    cb.set_label('Count')
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_time_series(df, title, filename, figsize=(12, 6)):
    """
    Create a time series plot of complaints by date.
    
    Args:
        df (pd.DataFrame): DataFrame with a Created Date column
        title (str): Title for the plot
        filename (str): Output filename
        figsize (tuple): Figure size
    """
    print("Creating time series plot...")
    
    # Convert Created Date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df['Created Date']):
        df['Created Date'] = pd.to_datetime(df['Created Date'])
    
    # Group by date and count
    daily_counts = df.groupby(df['Created Date'].dt.date).size()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the time series
    ax.plot(daily_counts.index, daily_counts.values)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Complaints')
    
    # Format x-axis
    plt.xticks(rotation=45)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_monthly_pattern(df, title, filename, figsize=(12, 6)):
    """
    Create a bar chart of complaints by month.
    
    Args:
        df (pd.DataFrame): DataFrame with a Created Date column
        title (str): Title for the plot
        filename (str): Output filename
        figsize (tuple): Figure size
    """
    print("Creating monthly pattern plot...")
    
    # Convert Created Date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df['Created Date']):
        df['Created Date'] = pd.to_datetime(df['Created Date'])
    
    # Extract month and count
    df['Month'] = df['Created Date'].dt.month
    monthly_counts = df.groupby('Month').size()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the bar chart
    ax.bar(monthly_counts.index, monthly_counts.values)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Complaints')
    
    # Format x-axis
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_weekly_pattern(df, title, filename, figsize=(12, 6)):
    """
    Create a bar chart of complaints by day of week.
    
    Args:
        df (pd.DataFrame): DataFrame with a Created Date column
        title (str): Title for the plot
        filename (str): Output filename
        figsize (tuple): Figure size
    """
    print("Creating weekly pattern plot...")
    
    # Convert Created Date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df['Created Date']):
        df['Created Date'] = pd.to_datetime(df['Created Date'])
    
    # Extract day of week and count
    df['DayOfWeek'] = df['Created Date'].dt.dayofweek
    weekly_counts = df.groupby('DayOfWeek').size()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the bar chart
    ax.bar(weekly_counts.index, weekly_counts.values)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Number of Complaints')
    
    # Format x-axis
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def create_complaint_type_distribution(df, title, filename, figsize=(12, 8)):
    """
    Create a bar chart of complaints by type.
    
    Args:
        df (pd.DataFrame): DataFrame with a Complaint Type column
        title (str): Title for the plot
        filename (str): Output filename
        figsize (tuple): Figure size
    """
    print("Creating complaint type distribution plot...")
    
    # Count complaints by type
    type_counts = df['Complaint Type'].value_counts().head(10)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the bar chart
    type_counts.plot(kind='barh', ax=ax)
    
    # Add title and labels
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Number of Complaints')
    ax.set_ylabel('Complaint Type')
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7, axis='x')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, filename), dpi=300)
    plt.close()

def visualize_data(complaints_df, aggregated_gdf):
    """
    Create all visualizations for the analysis.
    
    Args:
        complaints_df (pd.DataFrame): DataFrame with complaint data
        aggregated_gdf (gpd.GeoDataFrame): GeoDataFrame with aggregated complaint data
    """
    # Ensure directories exist
    ensure_dirs()
    
    # Create choropleth maps
    create_choropleth_map(
        aggregated_gdf,
        'complaint_count',
        'NYC Flood-Related 311 Complaints (2019) - Count by Census Tract',
        'flood_complaints_count_choropleth.png'
    )
    
    create_choropleth_map(
        aggregated_gdf,
        'complaint_rate',
        'NYC Flood-Related 311 Complaints (2019) - Rate by Census Tract',
        'flood_complaints_rate_choropleth.png',
        cmap='YlOrRd'
    )
    
    # Create simplified pixel maps
    create_simplified_pixel_map(
        aggregated_gdf,
        'complaint_count',
        'NYC Flood-Related 311 Complaints (2019) - Count Pixel Map',
        'flood_complaints_count_pixel.png'
    )
    
    create_simplified_pixel_map(
        aggregated_gdf,
        'complaint_rate',
        'NYC Flood-Related 311 Complaints (2019) - Rate Pixel Map',
        'flood_complaints_rate_pixel.png',
        cmap='YlOrRd'
    )
    
    # Create heatmap
    create_heatmap(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Heatmap',
        'flood_complaints_heatmap.png'
    )
    
    # Create time series
    create_time_series(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Daily Counts',
        'flood_complaints_time_series.png'
    )
    
    # Create monthly pattern
    create_monthly_pattern(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Monthly Pattern',
        'flood_complaints_monthly_pattern.png'
    )
    
    # Create weekly pattern
    create_weekly_pattern(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Weekly Pattern',
        'flood_complaints_weekly_pattern.png'
    )
    
    # Create complaint type distribution
    create_complaint_type_distribution(
        complaints_df,
        'NYC Flood-Related 311 Complaints (2019) - Top 10 Complaint Types',
        'flood_complaints_type_distribution.png'
    )

if __name__ == "__main__":
    # Load processed data
    complaints_df = pd.read_csv(os.path.join(DATA_DIR, "processed", "flood_complaints_2019.csv"))
    aggregated_gdf = gpd.read_file(os.path.join(DATA_DIR, "processed", "aggregated_flood_complaints_2019.geojson"))
    
    # Create visualizations
    visualize_data(complaints_df, aggregated_gdf)
