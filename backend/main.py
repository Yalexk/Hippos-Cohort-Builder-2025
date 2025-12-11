from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Load the cleaned data
DATA_PATH = "data/cleaned_anzhfr_full.csv"
df = None

def load_data():
    global df
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        print(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
    else:
        print(f"Warning: Data file not found at {DATA_PATH}")
        df = pd.DataFrame()

# Load data on startup
load_data()

@app.route("/api/cohort", methods=['POST'])
def build_cohort():
    try:
        filters = request.json
        print(f"Received filters: {filters}")
        
        # Start with full dataset
        filtered_df = df.copy()
        
        # Apply age filters
        if filters.get('minAge') and filters['minAge'] != '':
            min_age = float(filters['minAge'])
            filtered_df = filtered_df[filtered_df['age'] >= min_age]
        
        if filters.get('maxAge') and filters['maxAge'] != '':
            max_age = float(filters['maxAge'])
            filtered_df = filtered_df[filtered_df['age'] <= max_age]
        
        # Apply categorical filters - iterate through all possible filter fields
        categorical_filters = [
            'sex', 'ptype', 'uresidence', 'walk', 'cogstat', 'frailty', 
            'addelassess', 'ftype', 'afracture', 'asa', 'e_dadmit', 
            'painassess', 'painmanage', 'analges', 'surg', 'delay', 
            'anaesth', 'wbear', 'ward', 'gerimed', 'delassess', 'fassess',
            'pulcers', 'mobil', 'bonemed', 'dbonemed1', 'malnutrition', 
            'ons', 'wdest', 'fwalk2', 'dresidence', 'fbonemed2', 'fop2'
        ]
        
        for filter_key in categorical_filters:
            if filters.get(filter_key) and filters[filter_key] != '' and filter_key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[filter_key] == filters[filter_key]]
        
        count = len(filtered_df)
        print(f"Cohort size: {count}")
        
        return jsonify({
            "count": count,
            "filters": filters
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)
