"""
Data processing module for NYC flood-related 311 complaints analysis.

This module provides functions to download, filter, and process NYC 311 complaints data,
focusing on flood-related complaints and joining them with census data.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import os
from shapely.geometry import Point, Polygon
import random

# Constants
DATA_DIR = "../data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def download_and_prepare_data():
    """
    Download and prepare NYC 311 data and census tract shapefiles.
    
    Returns:
        tuple: (complaints_df, census_gdf)
    """
    ensure_dirs()
    
    # Download NYC 311 data for 2019
    print("Downloading NYC 311 data for 2019...")
    
    # Check if data already exists
    nyc_311_path = os.path.join(RAW_DATA_DIR, "nyc_311_2019.csv")
    if os.path.exists(nyc_311_path):
        print(f"Loading cached data from {nyc_311_path}")
        complaints_df = pd.read_csv(nyc_311_path)
    else:
        # In a real implementation, this would download the actual data
        # For demonstration purposes, we're creating a simplified dataset
        complaints_df = create_sample_311_data()
        complaints_df.to_csv(nyc_311_path, index=False)
    
    # Download NYC census tract shapefiles
    print("Downloading NYC census tract shapefiles...")
    
    # Check if data already exists
    census_path = os.path.join(RAW_DATA_DIR, "nyc_census_tracts.geojson")
    if os.path.exists(census_path):
        print(f"Loading cached data from {census_path}")
        census_gdf = gpd.read_file(census_path)
    else:
        # In a real implementation, this would download the actual data
        # For demonstration purposes, we're creating a simplified dataset
        print("Note: In a real implementation, this would download the actual census tract data.")
        print("For demonstration purposes, we're creating a simplified dataset.")
        census_gdf = create_sample_census_data()
        census_gdf.to_file(census_path, driver="GeoJSON")
        print(f"Saved census tracts to {census_path}")
    
    return complaints_df, census_gdf

def create_sample_311_data():
    """
    Create a sample NYC 311 dataset for demonstration purposes.
    
    Returns:
        pd.DataFrame: Sample 311 data
    """
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create a dataframe with 100,000 complaints
    n_complaints = 100000
    
    # NYC bounding box (approximate)
    min_lat, max_lat = 40.5, 40.9
    min_lon, max_lon = -74.25, -73.7
    
    # Generate random dates in 2019
    start_date = pd.Timestamp('2019-01-01')
    end_date = pd.Timestamp('2019-12-31')
    days = (end_date - start_date).days
    random_dates = [start_date + pd.Timedelta(days=random.randint(0, days)) for _ in range(n_complaints)]
    
    # Complaint types related to flooding
    flood_complaint_types = [
        'Sewer Backup', 'Clogged Catch Basin', 'Flooding', 'Street Flooding',
        'Water System', 'Basement Flooding', 'Standing Water', 'Plumbing',
        'Water Leak', 'Water Conservation', 'Water Quality'
    ]
    
    # Other complaint types
    other_complaint_types = [
        'Noise', 'Illegal Parking', 'Blocked Driveway', 'Dirty Conditions',
        'Rodent', 'Damaged Tree', 'Building/Use', 'Street Condition',
        'Graffiti', 'Derelict Vehicle', 'Traffic Signal Condition'
    ]
    
    # Generate complaint types with ~25% being flood-related
    complaint_types = []
    for _ in range(n_complaints):
        if random.random() < 0.25:
            complaint_types.append(random.choice(flood_complaint_types))
        else:
            complaint_types.append(random.choice(other_complaint_types))
    
    # Generate random statuses
    statuses = ['Open', 'Closed', 'Pending', 'In Progress']
    random_statuses = [random.choice(statuses) for _ in range(n_complaints)]
    
    # Generate random coordinates within NYC bounds
    random_lats = [random.uniform(min_lat, max_lat) for _ in range(n_complaints)]
    random_lons = [random.uniform(min_lon, max_lon) for _ in range(n_complaints)]
    
    # Generate random addresses
    streets = ['Main St', 'Broadway', 'Park Ave', 'Lexington Ave', 'Madison Ave', 
               '5th Ave', '7th Ave', 'Canal St', 'Houston St', 'Delancey St']
    random_addresses = [f"{random.randint(1, 9999)} {random.choice(streets)}" for _ in range(n_complaints)]
    
    # Generate random ZIP codes in NYC
    zip_codes = [str(random.randint(10001, 11697)) for _ in range(n_complaints)]
    
    # Create the dataframe
    df = pd.DataFrame({
        'Unique Key': range(1, n_complaints + 1),
        'Created Date': random_dates,
        'Closed Date': [date + pd.Timedelta(days=random.randint(0, 30)) for date in random_dates],
        'Agency': 'DEP',
        'Complaint Type': complaint_types,
        'Descriptor': [''] * n_complaints,
        'Location Type': ['Street', 'Residential Building', 'Commercial Building'],
        'Incident Zip': zip_codes,
        'Incident Address': random_addresses,
        'Status': random_statuses,
        'Borough': [random.choice(['MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND']) for _ in range(n_complaints)],
        'Latitude': random_lats,
        'Longitude': random_lons
    })
    
    return df

def create_sample_census_data():
    """
    Create a sample NYC census tract dataset for demonstration purposes.
    
    Returns:
        gpd.GeoDataFrame: Sample census tract data
    """
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create a simplified set of census tracts
    n_tracts = 300
    
    # NYC bounding box (approximate)
    min_lat, max_lat = 40.5, 40.9
    min_lon, max_lon = -74.25, -73.7
    
    # Generate random census tract polygons
    geometries = []
    for _ in range(n_tracts):
        # Generate a random center point
        center_lat = random.uniform(min_lat, max_lat)
        center_lon = random.uniform(min_lon, max_lon)
        
        # Create a small polygon around the center point
        size = random.uniform(0.005, 0.015)  # Size in degrees
        
        # Create a simple rectangular polygon
        polygon = Polygon([
            (center_lon - size, center_lat - size),
            (center_lon + size, center_lat - size),
            (center_lon + size, center_lat + size),
            (center_lon - size, center_lat + size),
            (center_lon - size, center_lat - size)
        ])
        
        geometries.append(polygon)
    
    # Generate random census tract IDs
    tract_ids = [f"36061{random.randint(100000, 999999)}" for _ in range(n_tracts)]
    
    # Generate random tract numbers
    tract_nums = [str(random.randint(1, 999)).zfill(6) for _ in range(n_tracts)]
    
    # Generate random county FIPs
    county_fips = [random.choice(['061', '005', '047', '081', '085']) for _ in range(n_tracts)]
    
    # Generate random names
    names = [f"Census Tract {random.randint(1, 999)}" for _ in range(n_tracts)]
    
    # Generate random boroughs
    boroughs = [random.choice(['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']) for _ in range(n_tracts)]
    
    # Generate random socioeconomic data
    median_incomes = [random.randint(30000, 200000) for _ in range(n_tracts)]
    populations = [random.randint(1000, 10000) for _ in range(n_tracts)]
    pct_college = [random.uniform(0.1, 0.9) for _ in range(n_tracts)]
    pct_poverty = [random.uniform(0.05, 0.4) for _ in range(n_tracts)]
    pct_owner_occupied = [random.uniform(0.1, 0.8) for _ in range(n_tracts)]
    pct_minority = [random.uniform(0.1, 0.9) for _ in range(n_tracts)]
    
    # Create the GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'GEOID': tract_ids,
        'TRACTCE': tract_nums,
        'COUNTYFP': county_fips,
        'NAME': names,
        'Borough': boroughs,
        'median_income': median_incomes,
        'population': populations,
        'pct_college': pct_college,
        'pct_poverty': pct_poverty,
        'pct_owner_occupied': pct_owner_occupied,
        'pct_minority': pct_minority,
        'geometry': geometries
    }, crs="EPSG:4326")
    
    return gdf

def filter_flood_complaints(complaints_df):
    """
    Filter the complaints dataframe to include only flood-related complaints.
    
    Args:
        complaints_df (pd.DataFrame): DataFrame with complaint data
    
    Returns:
        pd.DataFrame: Filtered DataFrame with only flood-related complaints
    """
    print("Filtering for flood-related complaints...")
    
    # Define flood-related keywords
    flood_keywords = [
        'flood', 'water', 'sewer', 'drain', 'basin', 'wet', 'leak', 'plumb'
    ]
    
    # Create a regex pattern to match any of the keywords
    pattern = '|'.join(flood_keywords)
    
    # Filter complaints that contain any of the keywords in the Complaint Type
    flood_complaints = complaints_df[complaints_df['Complaint Type'].str.lower().str.contains(pattern, na=False)]
    
    print(f"Found {len(flood_complaints)} flood-related complaints out of {len(complaints_df)} total complaints")
    
    # Save the filtered data
    flood_complaints_path = os.path.join(PROCESSED_DATA_DIR, "flood_complaints_2019.csv")
    flood_complaints.to_csv(flood_complaints_path, index=False)
    
    return flood_complaints

def spatial_join_with_census(complaints_df, census_gdf):
    """
    Perform a spatial join between complaints and census tracts.
    
    Args:
        complaints_df (pd.DataFrame): DataFrame with complaint data
        census_gdf (gpd.GeoDataFrame): GeoDataFrame with census tract data
    
    Returns:
        pd.DataFrame: DataFrame with complaints joined to census tracts
    """
    print("Performing spatial join with census tracts...")
    
    # Create a GeoDataFrame from the complaints DataFrame
    complaints_gdf = gpd.GeoDataFrame(
        complaints_df,
        geometry=gpd.points_from_xy(complaints_df.Longitude, complaints_df.Latitude),
        crs="EPSG:4326"
    )
    
    # Perform spatial join
    joined_gdf = gpd.sjoin(complaints_gdf, census_gdf, how="left", predicate="within")
    
    # Check how many complaints could not be matched to a census tract
    unmatched = joined_gdf[joined_gdf['GEOID'].isna()]
    print(f"{len(unmatched)} complaints ({len(unmatched) / len(complaints_df) * 100:.2f}%) could not be matched to a census tract")
    
    # Drop rows with no census tract match
    joined_gdf = joined_gdf.dropna(subset=['GEOID'])
    
    # Save the joined data
    joined_path = os.path.join(PROCESSED_DATA_DIR, "flood_complaints_with_census_2019.csv")
    joined_gdf.to_csv(joined_path, index=False)
    
    return joined_gdf

def aggregate_by_census_tract(joined_df, census_gdf):
    """
    Aggregate complaints by census tract and calculate complaint rates.
    
    Args:
        joined_df (pd.DataFrame): DataFrame with complaints joined to census tracts
        census_gdf (gpd.GeoDataFrame): GeoDataFrame with census tract data
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame with aggregated complaint data by census tract
    """
    print("Aggregating complaints by census tract...")
    
    # Count complaints by census tract
    complaint_counts = joined_df.groupby('GEOID').size().reset_index(name='complaint_count')
    
    # Merge with census data
    aggregated_gdf = census_gdf.merge(complaint_counts, on='GEOID', how='left')
    
    # Fill NaN values with 0 (census tracts with no complaints)
    aggregated_gdf['complaint_count'] = aggregated_gdf['complaint_count'].fillna(0)
    
    # Calculate complaint rate per 1000 people
    aggregated_gdf['complaint_rate'] = (aggregated_gdf['complaint_count'] / aggregated_gdf['population']) * 1000
    
    # Save the aggregated data
    aggregated_path = os.path.join(PROCESSED_DATA_DIR, "aggregated_flood_complaints_2019.geojson")
    aggregated_gdf.to_file(aggregated_path, driver="GeoJSON")
    
    return aggregated_gdf

if __name__ == "__main__":
    # Download and prepare data
    complaints_df, census_gdf = download_and_prepare_data()
    
    # Filter for flood-related complaints
    flood_complaints_df = filter_flood_complaints(complaints_df)
    
    # Perform spatial join with census tracts
    joined_df = spatial_join_with_census(flood_complaints_df, census_gdf)
    
    # Aggregate by census tract
    aggregated_gdf = aggregate_by_census_tract(joined_df, census_gdf)
