# Hippos Cohort Builder 2025

A web-based cohort builder and analytics platform for hip fracture patient data using the ANZHFR dataset. Built with React frontend and Python Flask backend, featuring advanced filtering, cohort management, and mortality analysis visualization.

## Project Structure

```
Hippos-Cohort-Builder-2025/
├── frontend/                 # React + Vite application
│   ├── src/
│   │   ├── App.jsx          # Main cohort builder interface
│   │   ├── Cohorts.jsx      # Saved cohorts management & analysis
│   │   ├── App.css          # Clinical minimal theme styles
│   │   └── Cohorts.css      # Analysis interface styles
│   └── package.json
├── backend/                  # Flask API server
│   ├── main.py              # API endpoints (build, save, delete, analyse)
│   ├── cohort_analysis.py   # Analysis orchestration
│   ├── mortality_analysis.py # Mortality computation & visualization
│   └── data/
│       ├── cleaning.py      # Data preprocessing pipeline
│       ├── cohorts/         # Saved cohort CSV files
│       └── saved_cohorts.json # Cohort metadata
└── README.md
```

## Features

### Cohort Builder
- **10 Clinical Sections** with collapsible filter groups
- **Multi-select Checkboxes** for all categorical variables
- **Age Range Filters** with compact input controls
- **Real-time Cohort Counting** matching all selected criteria
- **Clinical Minimal Design** optimized for medical use

### Cohort Management
- **Save Cohorts** to CSV with persistent storage
- **View Saved Cohorts** in a compact sidebar list
- **Delete Cohorts** with confirmation
- **Cohort Metadata** tracking filters, patient counts, and creation dates

### Analysis & Visualization
- **Mortality Analysis** across 30-day, 90-day, 120-day, and 365-day timeframes
- **Stacked Bar Charts** showing Alive/Deceased patient counts
- **Interactive Analysis Panel** displaying charts and cohort statistics
- **Modular Analysis Architecture** supporting future analytics modules

## Prerequisites

- **Node.js** (v16 or higher) and npm
- **Python** (v3.8 or higher)
- **Git**

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Yalexk/Hippos-Cohort-Builder-2025.git
cd Hippos-Cohort-Builder-2025
```

### 2. Backend Setup

#### a. Navigate to backend directory
```bash
cd backend
```

#### b. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

#### c. Install Python dependencies
```bash
pip install flask flask-cors pandas scikit-learn matplotlib
```

Required packages:
- `flask` - Web framework
- `flask-cors` - CORS support
- `pandas` - Data manipulation
- `scikit-learn` - KNN imputation for data cleaning
- `matplotlib` - Chart generation for analysis

#### d. Place your data file
- Place your CSV file (`unsw_datathon_2025.csv`) in the `backend/data/` directory
- **IMPORTANT**: Never commit this file to git (it's already in `.gitignore`)

#### e. Run data cleaning (first time only)
```bash
cd data
python3 cleaning.py
cd ..
```

This will:
- Create a backup of your original data
- Clean and transform the data
- Generate `cleaned_anzhfr_full.csv`

#### f. Start the backend server
```bash
python3 main.py
```

Server will run on `http://localhost:5050`

### 3. Frontend Setup

Open a **new terminal** window/tab:

#### a. Navigate to frontend directory
```bash
cd frontend
```

#### b. Install Node.js dependencies
```bash
npm install
```

This installs:
- `react` - UI framework
- `vite` - Build tool
- `axios` - HTTP client
- `react-router-dom` - Client-side routing
- Other dev dependencies

#### c. Start the development server
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

### 4. Access the Application

Open your browser and go to: **http://localhost:5173**

## Usage

### Cohort Builder Interface

The cohort builder features 10 collapsible clinical sections with multi-select filters:

1. **Demographics** - Age, sex, patient type, residence
2. **Presentation to ED** - Admission pathway, pain assessment & management
3. **Pre-fracture Functional Status** - Walking ability, cognition, frailty
4. **Fracture Characteristics** - Fracture type, additional fractures, ASA score
5. **Surgical Pathway** - Surgery type, timing, anaesthesia, weight bearing
6. **Post-operative Care** - Ward type, geriatric input, delirium assessment
7. **Bone Health** - Pre-admission and discharge bone medications
8. **Nutrition** - Malnutrition screening, oral nutrition supplements
9. **Discharge Outcomes** - Destination, walking ability, residence
10. **120-Day Follow-Up** - Residence, bone medications, further operations

### Building a Cohort

1. **Expand sections** by clicking on filter group labels
2. **Select multiple options** using checkboxes (hold Shift for range selection)
3. **Set age range** with compact min/max inputs
4. **Click "Build Cohort"** to see real-time patient count
5. **Save cohort** by entering a name and clicking "Save Cohort"

### Managing Saved Cohorts

1. Navigate to **"View Saved Cohorts"** from the main page
2. **Click a cohort name** in the left sidebar to select it
3. **View analysis** in the right panel showing:
   - Patient count and filters applied
   - Mortality analysis chart (if analysed)
4. **Delete cohorts** using the × button next to each name

### Running Analysis

1. Select a cohort from the sidebar
2. The backend automatically:
   - Loads the saved cohort CSV
   - Computes mortality statistics across timeframes
   - Generates a stacked bar chart (Alive/Deceased)
   - Returns results with base64-encoded chart image
3. View the chart and statistics in the analysis panel

## API Endpoints

### `POST /api/cohort`
Build a cohort based on filter criteria.

**Request:**
```json
{
  "minAge": "65",
  "maxAge": "85",
  "sex": ["Female"],
  "frailty": ["Mildly frail", "Moderately frail"],
  "ftype": ["Intracapsular displaced"]
}
```

**Response:**
```json
{
  "count": 1234,
  "filters": { ... }
}
```

### `GET /api/cohorts`
Retrieve all saved cohorts.

**Response:**
```json
{
  "cohort_1_20251211123456": {
    "id": "cohort_1_20251211123456",
    "name": "High-risk elderly patients",
    "count": 456,
    "filters": { ... },
    "csv_path": "data/cohorts/cohort_1_20251211123456.csv",
    "created_at": "2025-12-11T12:34:56"
  }
}
```

### `POST /api/cohorts`
Save a new cohort.

**Request:**
```json
{
  "name": "High-risk elderly patients",
  "filters": { ... },
  "count": 456
}
```

**Response:**
```json
{
  "id": "cohort_1_20251211123456",
  "name": "High-risk elderly patients",
  "count": 456,
  "csv_path": "data/cohorts/cohort_1_20251211123456.csv",
  "created_at": "2025-12-11T12:34:56"
}
```

### `DELETE /api/cohorts/<cohort_id>`
Delete a saved cohort and its CSV file.

**Response:**
```json
{
  "success": true,
  "message": "Deleted cohort: High-risk elderly patients"
}
```

### `POST /api/cohorts/<cohort_id>/analyse`
Run mortality analysis on a saved cohort.

**Response:**
```json
{
  "cohort_id": "cohort_1_20251211123456",
  "cohort_name": "High-risk elderly patients",
  "total_patients": 456,
  "mortality": {
    "30_day": { "count": 23, "rate": 5.04 },
    "90_day": { "count": 45, "rate": 9.87 },
    "120_day": { "count": 52, "rate": 11.40 },
    "365_day": { "count": 89, "rate": 19.52 }
  },
  "mortality_chart": "data:image/png;base64,iVBORw0KG..."
}
```

## Data Cleaning Pipeline

The `cleaning.py` script performs:

1. **Label Mapping** - Converts numeric codes to Australian English text labels
2. **DateTime Construction** - Builds proper datetime fields from date/time columns
3. **Derived Fields** - Calculates LOS, time to surgery, mortality flags
4. **Validation** - Removes outliers and invalid values
5. **KNN Imputation** - Fills missing continuous variables using K-Nearest Neighbors
6. **Default Values** - Sets defaults for missing categorical data

## Analysis Architecture

The analysis system uses a modular approach:

- **`cohort_analysis.py`** - Orchestrates analysis workflows and delegates to specialized modules
- **`mortality_analysis.py`** - Computes mortality statistics and generates visualization charts
- **Future modules** - Can be added for length of stay, readmissions, complications, etc.

### Mortality Analysis

Analyzes patient outcomes across four timeframes using dataset columns:
- `mort30d` - 30-day mortality
- `mort90d` - 90-day mortality
- `mort120d` - 120-day mortality
- `mort365d` - 365-day mortality

Generates stacked bar charts showing:
- Alive (bottom, blue)
- Deceased (top, red)
- Total patient counts labeled above each bar

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python3 main.py
```

The Flask server runs in debug mode and auto-reloads on file changes.

### Frontend Development

```bash
cd frontend
npm run dev
```

Vite dev server supports hot module replacement (HMR).

### Adding New Analysis Modules

1. Create `backend/<module_name>_analysis.py`
2. Implement computation and visualization functions
3. Import and call from `cohort_analysis.py`
4. Update API response structure in `main.py`
5. Add frontend rendering in `Cohorts.jsx`

### Building for Production

```bash
cd frontend
npm run build
```

Production files will be in `frontend/dist/`

## Important Notes

### Data Security

- **NEVER commit CSV data files** to git
- Data files are in `.gitignore` and `.copilotignore`
- Saved cohort CSVs stored locally in `backend/data/cohorts/`
- Keep all patient data local and confidential

### Git Branches

- `main` - Stable production branch
- `alex/mortality` - Mortality analysis feature
- `alex/visualisation` - Visualization improvements

## Troubleshooting

### Backend Issues

**Module import errors:**
```bash
# Ensure you're running from backend/ directory
cd backend
python3 main.py

# If using package-style imports fails, use local imports
# (Already configured in current codebase)
```

**Port already in use:**
```bash
# Kill process on port 5050
lsof -ti:5050 | xargs kill -9
```

**Missing dependencies:**
```bash
source venv/bin/activate
pip install flask flask-cors pandas scikit-learn matplotlib
```

**Chart generation fails:**
Ensure matplotlib backend is set correctly (using 'Agg' for non-GUI):
```python
import matplotlib
matplotlib.use('Agg')
```

### Frontend Issues

**CORS errors:**
- Ensure backend is running on port 5050
- Check CORS configuration in `backend/main.py` allows `http://localhost:5173`

**Network errors:**
- Verify backend server is running (`python3 main.py`)
- Check API endpoint URLs in `App.jsx` and `Cohorts.jsx`

**Router not working:**
- Ensure `react-router-dom` is installed: `npm install react-router-dom`
- Check routes in `main.jsx`

**Styles not loading:**
- Clear browser cache
- Check CSS imports in JSX files
- Verify `.css` files exist in `frontend/src/`

## Technology Stack

**Frontend:**
- React 19.2
- Vite 7.2
- Axios (HTTP client)
- React Router DOM (routing)
- CSS3 (clinical minimal design)

**Backend:**
- Python 3.x
- Flask 3.0 (web framework)
- Flask-CORS (cross-origin support)
- Pandas (data manipulation)
- scikit-learn (KNN imputation)
- Matplotlib (chart generation with Agg backend)

## Design Principles

- **Clinical First**: Minimal white/grey theme optimized for medical professionals
- **Compact UI**: Efficient use of screen space with collapsible sections
- **Multi-Select Everything**: Checkbox-based filtering for flexible cohort building
- **Persistent Storage**: All cohorts saved as CSV with metadata tracking
- **Modular Analysis**: Extensible architecture for adding new analytics

## License

This project is for the UNSW Datathon 2025.

## Contributors

- Team Hippos
- Alex Y (GitHub: @Yalexk)

## Support

For issues or questions, please create an issue in the GitHub repository or contact the development team.
