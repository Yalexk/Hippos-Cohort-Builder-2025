# Hippos Cohort Builder 2025

A web-based cohort builder for hip fracture patient analytics using the ANZHFR dataset. Built with React frontend and Python Flask backend.

## Project Structure

```
Hippos-Cohort-Builder-2025/
├── frontend/          # React + Vite application
├── backend/           # Flask API server
│   ├── data/         # Data cleaning scripts
│   └── main.py       # API endpoints
└── README.md
```

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
pip install flask flask-cors pandas scikit-learn
```

Required packages:
- `flask` - Web framework
- `flask-cors` - CORS support
- `pandas` - Data manipulation
- `scikit-learn` - KNN imputation for data cleaning

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

The cohort builder is organized into 10 clinical sections:

1. **Demographics** - Age, sex, patient type, residence
2. **Presentation to ED** - Admission pathway, pain management
3. **Pre-fracture Functional Status** - Mobility, cognition, frailty
4. **Fracture Characteristics** - Fracture type, ASA score
5. **Surgical Pathway** - Surgery details, timing, anaesthesia
6. **Post-operative Care** - Ward type, assessments, mobilization
7. **Bone Health** - Medications on admission and discharge
8. **Nutrition** - Malnutrition assessment, supplements
9. **Discharge Outcomes** - Destination, mobility status
10. **120-Day Follow-Up** - Residence, medications, reoperations

### How to Use

1. Select filters from any of the 10 sections
2. Multiple filters can be applied simultaneously
3. Click "Build Cohort" to see the patient count
4. Results show the number of patients matching all selected criteria

## API Endpoints

### `POST /api/cohort`

Build a cohort based on filter criteria.

**Request body:**
```json
{
  "minAge": "65",
  "maxAge": "85",
  "sex": "Female",
  "frailty": "Mildly frail",
  "ftype": "Intracapsular displaced"
}
```

**Response:**
```json
{
  "count": 1234,
  "filters": { ... }
}
```

## Data Cleaning Pipeline

The `cleaning.py` script performs:

1. **Label Mapping** - Converts numeric codes to text labels
2. **DateTime Construction** - Builds proper datetime fields
3. **Derived Fields** - Calculates LOS, time to surgery
4. **Validation** - Removes outliers and invalid values
5. **KNN Imputation** - Fills missing continuous variables using K-Nearest Neighbors
6. **Default Values** - Sets defaults for missing categorical data

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

### Building for Production

```bash
cd frontend
npm run build
```

Production files will be in `frontend/dist/`

## Important Notes

### Data Security

- **NEVER commit CSV data files** to git
- Data files are already in `.gitignore` and `.copilotignore`
- Keep all patient data local and confidential

### Git Branches

- `main` - Stable branch
- `alex/query` - Feature branch for query development

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 5050
lsof -ti:5050 | xargs kill -9
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt  # If you create one
```

### Frontend Issues

**CORS errors:**
- Ensure backend is running on port 5050
- Check CORS configuration in `backend/main.py`

**Network errors:**
- Verify backend server is running
- Check the port numbers match in frontend and backend

## Technology Stack

**Frontend:**
- React 19.2
- Vite 7.2
- Axios
- CSS3

**Backend:**
- Python 3.x
- Flask 3.0
- Pandas
- scikit-learn

## License

This project is for the UNSW Datathon 2025.

## Contributors

- Team Hippos

## Support

For issues or questions, please create an issue in the GitHub repository.
