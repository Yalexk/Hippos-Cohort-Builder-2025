from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import json
from datetime import datetime
# Import local module when running as a script from the backend directory
from cohort_analysis import analyse_cohort

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Load the cleaned data
DATA_PATH = "data/cleaned_anzhfr_full.csv"
COHORTS_FILE = "data/saved_cohorts.json"
COHORTS_DATA_DIR = "data/cohorts"
df = None
saved_cohorts = {}

# Create cohorts directory if it doesn't exist
if not os.path.exists(COHORTS_DATA_DIR):
    os.makedirs(COHORTS_DATA_DIR)

def load_data():
    global df
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        print(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
    else:
        print(f"Warning: Data file not found at {DATA_PATH}")
        df = pd.DataFrame()

def load_cohorts():
    global saved_cohorts
    if os.path.exists(COHORTS_FILE):
        with open(COHORTS_FILE, 'r') as f:
            saved_cohorts = json.load(f)
        print(f"Loaded {len(saved_cohorts)} saved cohorts")
    else:
        saved_cohorts = {}

def save_cohorts():
    with open(COHORTS_FILE, 'w') as f:
        json.dump(saved_cohorts, f, indent=2)

# Load data on startup
load_data()
load_cohorts()

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
            filter_values = filters.get(filter_key)
            if filter_values and len(filter_values) > 0 and filter_key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[filter_key].isin(filter_values)]
        
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

@app.route("/api/cohorts", methods=['GET'])
def get_cohorts():
    """Get all saved cohorts"""
    return jsonify(saved_cohorts)

@app.route("/api/cohorts", methods=['POST'])
def save_cohort():
    """Save a new cohort"""
    try:
        data = request.json
        cohort_name = data.get('name')
        filters = data.get('filters')
        count = data.get('count')
        
        if not cohort_name:
            return jsonify({"error": "Cohort name is required"}), 400
        
        # Generate unique ID
        cohort_id = f"cohort_{len(saved_cohorts) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Re-apply filters to get the actual filtered data
        filtered_df = df.copy()
        
        # Apply age filters
        if filters.get('minAge') and filters['minAge'] != '':
            min_age = float(filters['minAge'])
            filtered_df = filtered_df[filtered_df['age'] >= min_age]
        
        if filters.get('maxAge') and filters['maxAge'] != '':
            max_age = float(filters['maxAge'])
            filtered_df = filtered_df[filtered_df['age'] <= max_age]
        
        # Apply categorical filters
        categorical_filters = [
            'sex', 'ptype', 'uresidence', 'walk', 'cogstat', 'frailty', 
            'addelassess', 'ftype', 'afracture', 'asa', 'e_dadmit', 
            'painassess', 'painmanage', 'analges', 'surg', 'delay', 
            'anaesth', 'wbear', 'ward', 'gerimed', 'delassess', 'fassess',
            'pulcers', 'mobil', 'bonemed', 'dbonemed1', 'malnutrition', 
            'ons', 'wdest', 'fwalk2', 'dresidence', 'fbonemed2', 'fop2'
        ]
        
        for filter_key in categorical_filters:
            filter_values = filters.get(filter_key)
            if filter_values and len(filter_values) > 0 and filter_key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[filter_key].isin(filter_values)]
        
        # Save the filtered data to CSV
        csv_path = os.path.join(COHORTS_DATA_DIR, f"{cohort_id}.csv")
        filtered_df.to_csv(csv_path, index=False)
        print(f"Saved cohort data to: {csv_path} ({len(filtered_df)} rows)")
        
        # Save metadata
        saved_cohorts[cohort_id] = {
            "id": cohort_id,
            "name": cohort_name,
            "filters": filters,
            "count": count,
            "csv_path": csv_path,
            "created_at": datetime.now().isoformat()
        }
        
        save_cohorts()
        print(f"Saved cohort: {cohort_name} ({count} patients)")
        
        return jsonify(saved_cohorts[cohort_id])
    
    except Exception as e:
        print(f"Error saving cohort: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/cohorts/<cohort_id>", methods=['DELETE'])
def delete_cohort(cohort_id):
    """Delete a saved cohort"""
    try:
        if cohort_id in saved_cohorts:
            cohort_name = saved_cohorts[cohort_id]['name']
            
            # Delete the CSV file if it exists
            csv_path = saved_cohorts[cohort_id].get('csv_path')
            if csv_path and os.path.exists(csv_path):
                os.remove(csv_path)
                print(f"Deleted CSV file: {csv_path}")
            
            del saved_cohorts[cohort_id]
            save_cohorts()
            print(f"Deleted cohort: {cohort_name}")
            return jsonify({"success": True, "message": f"Deleted cohort: {cohort_name}"})
        else:
            return jsonify({"error": "Cohort not found"}), 404
    
    except Exception as e:
        print(f"Error deleting cohort: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/cohorts/<cohort_id>/analyse", methods=['POST'])
def analyse_cohort_endpoint(cohort_id):
    """Analyse a saved cohort"""
    try:
        if cohort_id not in saved_cohorts:
            return jsonify({"error": "Cohort not found"}), 404
        
        cohort = saved_cohorts[cohort_id]
        csv_path = cohort.get('csv_path')
        # RETRIEVE FILTERS
        cohort_filters = cohort.get('filters', {}) 
        
        if not csv_path or not os.path.exists(csv_path):
            return jsonify({"error": "Cohort data file not found"}), 404
        
        # PASS FILTERS TO ANALYSIS
        analysis_results = analyse_cohort(cohort_id, csv_path, cohort_filters)
        
        # Add cohort metadata
        analysis_results['cohort_name'] = cohort['name']
        analysis_results['created_at'] = cohort['created_at']
        
        print(f"Analysed cohort: {cohort['name']}")
        
        return jsonify(analysis_results)
    
    except Exception as e:
        print(f"Error analysing cohort: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)