"""
Main script to run the complete NYC flood-related 311 complaints analysis pipeline.

This script orchestrates the entire data processing, visualization, and analysis workflow
for analyzing flood-related 311 complaints in NYC and their relationship with
socioeconomic factors at the census tract level.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
import data_processing
import visualization
import socioeconomic_analysis

def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run NYC flood-related 311 complaints analysis')
    
    parser.add_argument('--year', type=int, default=2019,
                        help='Year to analyze (default: 2019)')
    parser.add_argument('--sample', action='store_true',
                        help='Use a sample of the data for testing')
    parser.add_argument('--sample-size', type=int, default=10000,
                        help='Sample size if using sample data (default: 10000)')
    parser.add_argument('--skip-processing', action='store_true',
                        help='Skip data processing step (use existing processed data)')
    parser.add_argument('--skip-visualization', action='store_true',
                        help='Skip visualization step')
    parser.add_argument('--skip-analysis', action='store_true',
                        help='Skip socioeconomic analysis step')
    parser.add_argument('--resolution', type=int, default=100,
                        help='Resolution for pixel maps (default: 100)')
    
    return parser.parse_args()

def main():
    """Main function to run the complete analysis pipeline."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging()
    logger.info("Starting NYC flood-related 311 complaints analysis")
    logger.info(f"Arguments: {args}")
    
    # Create necessary directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    figures_dir = os.path.join(base_dir, 'figures')
    results_dir = os.path.join(base_dir, 'results')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Step 1: Data Processing
    if not args.skip_processing:
        logger.info("Step 1: Processing data")
        try:
            flood_complaints_df, census_gdf, aggregated_gdf = data_processing.process_data()
            logger.info("Data processing completed successfully")
        except Exception as e:
            logger.error(f"Error in data processing: {e}")
            return
    else:
        logger.info("Skipping data processing, loading processed data")
        try:
            flood_complaints_df = data_processing.download_nyc_311_data(year=args.year, sample=args.sample, sample_size=args.sample_size)
            census_gdf = data_processing.download_census_tracts()
            aggregated_gdf = socioeconomic_analysis.load_data()
            logger.info("Processed data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return
    
    # Step 2: Visualization
    if not args.skip_visualization:
        logger.info("Step 2: Creating visualizations")
        try:
            visualization.visualize_data(flood_complaints_df, aggregated_gdf)
            logger.info("Visualizations created successfully")
        except Exception as e:
            logger.error(f"Error in visualization: {e}")
    
    # Step 3: Socioeconomic Analysis
    if not args.skip_analysis:
        logger.info("Step 3: Running socioeconomic analysis")
        try:
            results = socioeconomic_analysis.run_analysis()
            logger.info("Socioeconomic analysis completed successfully")
        except Exception as e:
            logger.error(f"Error in socioeconomic analysis: {e}")
    
    logger.info("Analysis pipeline completed")

if __name__ == "__main__":
    main()
