# NYC Flood-Related 311 Complaints Analysis

This repository contains code and analysis for exploring flood-related 311 complaints in New York City, with a focus on spatial patterns and socioeconomic factors.

## Overview

This project analyzes NYC 311 service request data related to flooding issues from 2019, examining:
- Spatial distribution of flood complaints across NYC
- Temporal patterns in reporting behavior
- Relationship between complaint rates and socioeconomic factors
- Interactive visualization of complaint data

The analysis is based on the methodology from the research paper ["Quantifying spatial underreporting disparities in resident crowdsourcing"](https://www.nature.com/articles/s43588-023-00572-6) by Nikhil Garg et al.

## Repository Structure

- `scripts/`: Python scripts for data processing, analysis, and visualization
  - `data_processing.py`: Functions for downloading and processing 311 and census data
  - `visualization.py`: Functions for creating static visualizations
  - `socioeconomic_analysis.py`: Functions for analyzing relationships with socioeconomic factors
  - `interactive_map.py`: Functions for creating interactive choropleth maps
  - `precise_point_map.py`: Functions for creating precise point-based interactive maps
  - `run_analysis.py`: Main script to run the complete analysis pipeline

- `notebooks/`: Jupyter notebooks for interactive exploration
  - `demo_analysis.ipynb`: Demonstration of the complete analysis workflow

- `data/`: Processed data files
  - `flood_complaints_2019.csv`: Processed flood-related 311 complaints from 2019
  - `aggregated_flood_complaints_2019.geojson`: Complaints aggregated by census tract
  - `flood_complaints_with_census_2019.csv`: Complaints joined with census data

- `figures/`: Output visualizations
  - Static visualizations (PNG files)
  - Interactive maps (HTML files)

- `docs/`: Documentation and additional resources

## Key Features

1. **Data Processing Pipeline**
   - Filters 311 data for flood-related complaints
   - Joins with census tract data
   - Calculates complaint rates per population

2. **Spatial Analysis**
   - Choropleth maps of complaint counts and rates
   - Pixel-based maps for detailed spatial patterns
   - Identification of hotspots and spatial clusters

3. **Socioeconomic Analysis**
   - Correlation analysis with demographic variables
   - Regression models to identify key predictors
   - Visualization of relationships with income, education, etc.

4. **Interactive Visualizations**
   - Precise point maps showing individual complaints
   - Hover functionality to display detailed information
   - Category-based maps showing complaint types

## Interactive Maps

The repository includes several interactive HTML maps:

1. **Precise Point Maps**
   - `precise_flood_complaints_points.html`: Shows each complaint as a small point, colored by status
   - `precise_flood_complaints_by_type.html`: Shows each complaint colored by complaint type

2. **Choropleth Maps**
   - `interactive_flood_complaints_count.html`: Census tract map of complaint counts
   - `interactive_flood_complaints_rate.html`: Census tract map of complaint rates
   - `interactive_flood_complaints_vs_income.html`: Bivariate map of complaints vs income

## Getting Started

### Prerequisites
- Python 3.8+
- Required packages: pandas, geopandas, numpy, matplotlib, folium, scikit-learn

### Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/nyc_flood_311_analysis.git
cd nyc_flood_311_analysis
```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Run the analysis:
```
cd scripts
python run_analysis.py
```

### Using the Interactive Maps

1. Navigate to the `figures` directory
2. Open any HTML file in a web browser
3. For point maps:
   - Hover over points to see complaint details
   - Click on points for additional information
   - Use the legend to understand color coding

## Methodology

This analysis builds on the methodology from Garg et al. (2023), which examines spatial disparities in resident crowdsourcing systems. Key methodological steps include:

1. Data collection from NYC Open Data 311 Service Requests
2. Spatial joining with census tract boundaries
3. Normalization of complaint counts by population
4. Statistical analysis of relationships with socioeconomic variables
5. Visualization using both static and interactive approaches

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NYC Open Data for providing the 311 Service Request data
- U.S. Census Bureau for demographic data
- Nikhil Garg et al. for the research methodology in "Quantifying spatial underreporting disparities in resident crowdsourcing"
