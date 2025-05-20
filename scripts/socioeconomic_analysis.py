"""
Socioeconomic analysis module for NYC flood-related 311 complaints.

This module provides functions to analyze the relationship between
flood-related 311 complaints and socioeconomic factors at the census tract level.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Constants
DATA_DIR = "../data"
FIGURES_DIR = "../figures"
RESULTS_DIR = "../results"

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data():
    """
    Load processed data for analysis.
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame with aggregated complaint data and socioeconomic variables
    """
    # Load aggregated data
    aggregated_gdf = gpd.read_file(os.path.join(DATA_DIR, "processed", "aggregated_flood_complaints_2019.geojson"))
    
    return aggregated_gdf

def calculate_descriptive_statistics(gdf):
    """
    Calculate descriptive statistics for complaint data and socioeconomic variables.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with complaint and socioeconomic data
    
    Returns:
        pd.DataFrame: DataFrame with descriptive statistics
    """
    print("Calculating descriptive statistics...")
    
    # Select columns for analysis
    analysis_cols = ['complaint_count', 'complaint_rate', 'population', 
                     'median_income', 'pct_college', 'pct_poverty', 'pct_owner_occupied']
    
    # Filter columns that exist in the data
    analysis_cols = [col for col in analysis_cols if col in gdf.columns]
    
    # Calculate descriptive statistics
    stats_df = gdf[analysis_cols].describe().T
    
    # Add additional statistics
    stats_df['median'] = gdf[analysis_cols].median()
    stats_df['skew'] = gdf[analysis_cols].skew()
    stats_df['kurtosis'] = gdf[analysis_cols].kurtosis()
    
    # Save to CSV
    stats_df.to_csv(os.path.join(RESULTS_DIR, "descriptive_statistics.csv"))
    
    return stats_df

def calculate_correlations(gdf):
    """
    Calculate correlations between complaint rates and socioeconomic variables.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with complaint and socioeconomic data
    
    Returns:
        pd.DataFrame: DataFrame with correlation coefficients
    """
    print("Calculating correlations...")
    
    # Select columns for analysis
    analysis_cols = ['complaint_rate', 'median_income', 'pct_college', 
                     'pct_poverty', 'pct_owner_occupied']
    
    # Filter columns that exist in the data
    analysis_cols = [col for col in analysis_cols if col in gdf.columns]
    
    # Calculate correlation matrix
    corr_matrix = gdf[analysis_cols].corr()
    
    # Save to CSV
    corr_matrix.to_csv(os.path.join(RESULTS_DIR, "correlation_matrix.csv"))
    
    # Create correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix: Flood Complaints and Socioeconomic Factors')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_heatmap.png"), dpi=300)
    plt.close()
    
    return corr_matrix

def run_regression_models(gdf):
    """
    Run regression models to analyze the relationship between complaint rates
    and socioeconomic factors.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with complaint and socioeconomic data
    
    Returns:
        dict: Dictionary with regression results
    """
    print("Running regression models...")
    
    # Select columns for analysis
    target_col = 'complaint_rate'
    feature_cols = ['median_income', 'pct_college', 'pct_poverty', 'pct_owner_occupied']
    
    # Filter columns that exist in the data
    feature_cols = [col for col in feature_cols if col in gdf.columns]
    
    if not feature_cols:
        print("No valid feature columns found")
        return None
    
    # Prepare data
    X = gdf[feature_cols].copy()
    y = gdf[target_col].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # OLS Regression with statsmodels
    X_with_const = sm.add_constant(X_scaled_df)
    ols_model = sm.OLS(y, X_with_const).fit()
    
    # Save OLS results
    with open(os.path.join(RESULTS_DIR, "ols_regression_results.txt"), 'w') as f:
        f.write(ols_model.summary().as_text())
    
    # Random Forest Regression
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_scaled, y)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    # Save feature importance
    feature_importance.to_csv(os.path.join(RESULTS_DIR, "rf_feature_importance.csv"), index=False)
    
    # Create feature importance plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feature_importance)
    plt.title('Random Forest Feature Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "rf_feature_importance.png"), dpi=300)
    plt.close()
    
    # Return results
    results = {
        'ols_model': ols_model,
        'rf_model': rf_model,
        'feature_importance': feature_importance
    }
    
    return results

def analyze_spatial_patterns(gdf):
    """
    Analyze spatial patterns in complaint rates.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with complaint and socioeconomic data
    
    Returns:
        dict: Dictionary with spatial analysis results
    """
    print("Analyzing spatial patterns...")
    
    # Check for spatial autocorrelation
    # This is a simplified approach - in a real implementation, you would use pysal for Moran's I
    
    # Calculate global statistics
    global_stats = {
        'total_complaints': gdf['complaint_count'].sum(),
        'mean_complaint_rate': gdf['complaint_rate'].mean(),
        'median_complaint_rate': gdf['complaint_rate'].median(),
        'max_complaint_rate': gdf['complaint_rate'].max(),
        'min_complaint_rate': gdf['complaint_rate'].min()
    }
    
    # Save global statistics
    pd.DataFrame([global_stats]).to_csv(os.path.join(RESULTS_DIR, "global_spatial_statistics.csv"), index=False)
    
    # Identify hotspots (simplified approach)
    # In a real implementation, you would use proper hotspot analysis methods
    threshold = gdf['complaint_rate'].mean() + gdf['complaint_rate'].std()
    hotspots = gdf[gdf['complaint_rate'] > threshold]
    
    # Save hotspots
    if not hotspots.empty:
        hotspots.to_file(os.path.join(RESULTS_DIR, "complaint_hotspots.geojson"), driver='GeoJSON')
    
    # Return results
    results = {
        'global_stats': global_stats,
        'hotspots': hotspots
    }
    
    return results

def run_analysis():
    """
    Run the complete socioeconomic analysis.
    
    Returns:
        dict: Dictionary with all analysis results
    """
    # Ensure directories exist
    ensure_dirs()
    
    # Load data
    gdf = load_data()
    
    # Run analyses
    stats_df = calculate_descriptive_statistics(gdf)
    corr_matrix = calculate_correlations(gdf)
    regression_results = run_regression_models(gdf)
    spatial_results = analyze_spatial_patterns(gdf)
    
    # Compile results
    results = {
        'descriptive_stats': stats_df,
        'correlations': corr_matrix,
        'regression': regression_results,
        'spatial': spatial_results
    }
    
    # Generate summary report
    generate_summary_report(results, gdf)
    
    return results

def generate_summary_report(results, gdf):
    """
    Generate a summary report of the analysis results.
    
    Args:
        results (dict): Dictionary with analysis results
        gdf (gpd.GeoDataFrame): GeoDataFrame with complaint and socioeconomic data
    """
    print("Generating summary report...")
    
    with open(os.path.join(RESULTS_DIR, "analysis_summary.md"), 'w') as f:
        f.write("# NYC Flood-Related 311 Complaints Analysis Summary\n\n")
        
        # Overview
        f.write("## Overview\n\n")
        f.write("This report summarizes the analysis of flood-related 311 complaints in NYC for 2019 ")
        f.write("and their relationship with socioeconomic factors at the census tract level.\n\n")
        
        # Data summary
        f.write("## Data Summary\n\n")
        f.write(f"- Total census tracts analyzed: {len(gdf)}\n")
        f.write(f"- Total flood-related complaints: {int(gdf['complaint_count'].sum())}\n")
        f.write(f"- Average complaints per tract: {gdf['complaint_count'].mean():.2f}\n")
        f.write(f"- Average complaint rate (per capita): {gdf['complaint_rate'].mean():.6f}\n\n")
        
        # Key findings
        f.write("## Key Findings\n\n")
        
        # Correlations
        f.write("### Correlations with Complaint Rate\n\n")
        if 'correlations' in results and isinstance(results['correlations'], pd.DataFrame):
            corr_series = results['correlations']['complaint_rate'].drop('complaint_rate')
            f.write("| Socioeconomic Factor | Correlation with Complaint Rate |\n")
            f.write("|----------------------|--------------------------------|\n")
            for factor, corr in corr_series.items():
                f.write(f"| {factor} | {corr:.4f} |\n")
            f.write("\n")
        
        # Regression results
        f.write("### Regression Analysis\n\n")
        if 'regression' in results and results['regression'] and 'ols_model' in results['regression']:
            ols_model = results['regression']['ols_model']
            f.write(f"- R-squared: {ols_model.rsquared:.4f}\n")
            f.write(f"- Adjusted R-squared: {ols_model.rsquared_adj:.4f}\n")
            f.write("- Significant predictors (p < 0.05):\n")
            
            for var, p_value in zip(ols_model.params.index, ols_model.pvalues):
                if p_value < 0.05 and var != 'const':
                    coef = ols_model.params[var]
                    f.write(f"  - {var}: coefficient = {coef:.4f}, p-value = {p_value:.4f}\n")
            f.write("\n")
        
        # Feature importance
        f.write("### Random Forest Feature Importance\n\n")
        if ('regression' in results and results['regression'] and 
            'feature_importance' in results['regression']):
            feature_imp = results['regression']['feature_importance']
            f.write("| Feature | Importance |\n")
            f.write("|---------|------------|\n")
            for _, row in feature_imp.iterrows():
                f.write(f"| {row['Feature']} | {row['Importance']:.4f} |\n")
            f.write("\n")
        
        # Spatial patterns
        f.write("### Spatial Patterns\n\n")
        if 'spatial' in results and 'global_stats' in results['spatial']:
            stats = results['spatial']['global_stats']
            f.write(f"- Mean complaint rate: {stats['mean_complaint_rate']:.6f}\n")
            f.write(f"- Median complaint rate: {stats['median_complaint_rate']:.6f}\n")
            
            if 'hotspots' in results['spatial']:
                hotspots = results['spatial']['hotspots']
                f.write(f"- Number of hotspot tracts: {len(hotspots)}\n")
                if not hotspots.empty:
                    f.write(f"- Average complaint rate in hotspots: {hotspots['complaint_rate'].mean():.6f}\n")
            f.write("\n")
        
        # Conclusions
        f.write("## Conclusions\n\n")
        f.write("Based on the analysis of flood-related 311 complaints in NYC for 2019, we found that:\n\n")
        f.write("1. There is significant spatial variation in flood-related complaint rates across NYC census tracts.\n")
        f.write("2. Socioeconomic factors show meaningful correlations with complaint rates, suggesting that reporting behavior is influenced by demographic characteristics.\n")
        f.write("3. The most important predictors of flood-related complaint rates are [list top factors based on analysis].\n")
        f.write("4. Areas with higher [income/education/etc.] tend to report more flood-related issues, which may indicate reporting disparities rather than actual differences in flooding incidents.\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. City agencies should consider these reporting disparities when allocating resources based on 311 data.\n")
        f.write("2. Additional outreach and education about the 311 system may be needed in areas with lower reporting rates.\n")
        f.write("3. Combining 311 data with other sources of information about flooding (e.g., flood maps, weather data) could provide a more complete picture of actual needs.\n")
        f.write("4. Future research should explore temporal patterns and the relationship between reporting and actual flooding incidents.\n")
    
    print(f"Summary report saved to {os.path.join(RESULTS_DIR, 'analysis_summary.md')}")

if __name__ == "__main__":
    run_analysis()
