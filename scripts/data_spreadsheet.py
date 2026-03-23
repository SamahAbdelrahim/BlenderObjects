import os
import json
import pandas as pd
import numpy as np
import glob

class StimulusDatabase:
    def __init__(self, stl_params_dir="/Users/samahabdelrahim/git-repos/BlenderObjects/stl_parameters/"):
        self.stl_params_dir = stl_params_dir
        self.df = None
        self.parameter_ranges = {}
        
    def load_parameters(self):
        """Load all parameter files into a pandas DataFrame"""
        data = []
        
        # Get all JSON parameter files
        param_files = glob.glob(os.path.join(self.stl_params_dir, "shape_generator_object_*.json"))
        
        for param_file in param_files:
            with open(param_file, 'r') as f:
                params = json.load(f)
                
            # Extract base filename without extension
            base_name = os.path.splitext(os.path.basename(param_file))[0]
            complexity_level = params['complexity_level']
            
            # Construct STL filename based on parameters
            stl_filename = f"shape_gen_ext{params['num_extrusions']}_extrange{params['extrusion_range']:.2f}_rot{params['max_rotation']}_seed{params['random_seed']}.stl"
            stl_path = os.path.join(self.stl_params_dir, stl_filename)
            
            # Create row entry
            row = {
                'object_id': f"stimulus_{complexity_level}",
                'complexity_level': complexity_level,
                'param_file': param_file,
                'stl_file': stl_path,
                'num_extrusions': params['num_extrusions'],
                'min_extrude': params['min_extrude'],
                'max_extrude': params['max_extrude'],
                'extrusion_range': params['extrusion_range'],
                'min_rotation': params['min_rotation'],
                'max_rotation': params['max_rotation'],
                'rotation_range': params['rotation_range'],
                'random_seed': params['random_seed']
            }
            data.append(row)
        
        # Create DataFrame and sort by complexity level
        self.df = pd.DataFrame(data)
        self.df.sort_values('complexity_level', inplace=True)
        
        # Calculate parameter ranges for normalization
        self._calculate_parameter_ranges()
        
        return self.df
    
    def _calculate_parameter_ranges(self):
        """Calculate min/max ranges for each numerical parameter"""
        numerical_columns = [
            'complexity_level', 'num_extrusions', 'min_extrude', 
            'max_extrude', 'extrusion_range', 'min_rotation', 
            'max_rotation', 'rotation_range'
        ]
        
        self.parameter_ranges = {
            col: {
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'range': self.df[col].max() - self.df[col].min()
            }
            for col in numerical_columns
        }
    
    def normalize_parameters(self):
        """Create normalized versions of all numerical parameters"""
        if self.df is None:
            raise ValueError("Must load parameters first using load_parameters()")
            
        for param, ranges in self.parameter_ranges.items():
            if ranges['range'] > 0:  # Avoid division by zero
                normalized_col = f"{param}_normalized"
                self.df[normalized_col] = (self.df[param] - ranges['min']) / ranges['range']
            
        return self.df
    
    def save_database(self, output_file='stimulus_database.csv'):
        """Save the database to a CSV file"""
        if self.df is not None:
            self.df.to_csv(output_file, index=False)
            print(f"Database saved to {output_file}")
        else:
            print("No data to save. Please load parameters first.")
            
    def get_parameter_ranges(self):
        """Return the calculated parameter ranges"""
        return self.parameter_ranges

def main():
    # Create database instance
    db = StimulusDatabase()
    
    # Load and process parameters
    print("Loading parameters...")
    db.load_parameters()
    
    # Normalize parameters
    print("Normalizing parameters...")
    db.normalize_parameters()
    
    # Save the database
    print("Saving database...")
    db.save_database()
    
    # Print parameter ranges
    print("\nParameter Ranges:")
    for param, ranges in db.get_parameter_ranges().items():
        print(f"{param}:")
        print(f"  Min: {ranges['min']:.3f}")
        print(f"  Max: {ranges['max']:.3f}")
        print(f"  Range: {ranges['range']:.3f}")

if __name__ == "__main__":
    main()