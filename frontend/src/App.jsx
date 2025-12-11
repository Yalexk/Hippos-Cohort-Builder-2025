import { useState, useEffect } from 'react'
import './App.css'
import axios from "axios"

function App() {
  const [filters, setFilters] = useState({
    // Demographics
    minAge: '',
    maxAge: '',
    sex: '',
    ptype: '',
    uresidence: '',
    
    // Pre-fracture Functional Status
    walk: '',
    cogstat: '',
    frailty: '',
    addelassess: '',
    
    // Fracture Characteristics
    ftype: '',
    afracture: '',
    asa: '',
    
    // Presentation to ED
    e_dadmit: '',
    painassess: '',
    painmanage: '',
    analges: '',
    
    // Surgical Pathway
    surg: '',
    delay: '',
    anaesth: '',
    wbear: '',
    
    // Post-operative Care
    ward: '',
    gerimed: '',
    delassess: '',
    fassess: '',
    pulcers: '',
    mobil: '',
    
    // Bone Health
    bonemed: '',
    dbonemed1: '',
    
    // Nutrition
    malnutrition: '',
    ons: '',
    
    // Discharge Outcomes
    wdest: '',
    fwalk2: '',
    
    // Follow-up Outcomes
    dresidence: '',
    fbonemed2: '',
    fop2: ''
  })
  const [cohortSize, setCohortSize] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedCohorts, setSavedCohorts] = useState([])
  const [cohortName, setCohortName] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)

  // Load saved cohorts on mount
  useEffect(() => {
    loadSavedCohorts()
  }, [])

  const loadSavedCohorts = async () => {
    try {
      const response = await axios.get("http://localhost:5050/api/cohorts")
      setSavedCohorts(Object.values(response.data))
    } catch (err) {
      console.error('Error loading cohorts:', err)
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const buildCohort = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Sending filters:', filters)
      const response = await axios.post("http://localhost:5050/api/cohort", filters)
      console.log('Cohort response:', response.data)
      setCohortSize(response.data.count)
    } catch (err) {
      console.error('Error building cohort:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const saveCohort = async () => {
    if (!cohortName.trim()) {
      alert('Please enter a cohort name')
      return
    }

    if (cohortSize === null) {
      alert('Please build a cohort first')
      return
    }

    try {
      await axios.post("http://localhost:5050/api/cohorts", {
        name: cohortName,
        filters: filters,
        count: cohortSize
      })
      setCohortName('')
      setShowSaveDialog(false)
      loadSavedCohorts()
      alert(`Cohort "${cohortName}" saved successfully!`)
    } catch (err) {
      console.error('Error saving cohort:', err)
      alert('Failed to save cohort')
    }
  }

  const deleteCohort = async (cohortId, cohortName) => {
    if (!confirm(`Are you sure you want to delete "${cohortName}"?`)) {
      return
    }

    try {
      await axios.delete(`http://localhost:5050/api/cohorts/${cohortId}`)
      loadSavedCohorts()
    } catch (err) {
      console.error('Error deleting cohort:', err)
      alert('Failed to delete cohort')
    }
  }

  return (
    <div className="app">
      <h1>Hip Fracture Cohort Builder</h1>
      
      <div className="cohort-builder">
        <div className="filters-section">
          <h2>Filters</h2>
          
          {/* 1. DEMOGRAPHICS */}
          <div className="section-header">1. Demographics</div>
          
          <div className="filter-group">
            <label>Age Range</label>
            <div className="age-inputs">
              <input
                type="number"
                placeholder="Min Age"
                value={filters.minAge}
                onChange={(e) => handleFilterChange('minAge', e.target.value)}
              />
              <span>to</span>
              <input
                type="number"
                placeholder="Max Age"
                value={filters.maxAge}
                onChange={(e) => handleFilterChange('maxAge', e.target.value)}
              />
            </div>
          </div>

          <div className="filter-group">
            <label>Sex</label>
            <select value={filters.sex} onChange={(e) => handleFilterChange('sex', e.target.value)}>
              <option value="">All</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Intersex or indeterminate">Intersex or indeterminate</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Patient Type</label>
            <select value={filters.ptype} onChange={(e) => handleFilterChange('ptype', e.target.value)}>
              <option value="">All</option>
              <option value="Public">Public</option>
              <option value="Private">Private</option>
              <option value="Overseas">Overseas</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Usual Residence</label>
            <select value={filters.uresidence} onChange={(e) => handleFilterChange('uresidence', e.target.value)}>
              <option value="">All</option>
              <option value="Private residence">Private residence</option>
              <option value="Residential aged care facility">RACF</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* 3. PRE-FRACTURE FUNCTIONAL STATUS */}
          <div className="section-header">3. Pre-fracture Functional Status</div>

          <div className="filter-group">
            <label>Mobility Ability</label>
            <select value={filters.walk} onChange={(e) => handleFilterChange('walk', e.target.value)}>
              <option value="">All</option>
              <option value="Walks without walking aids">Walks unaided</option>
              <option value="Walks with either a stick or crutch">Walks with 1 aid</option>
              <option value="Walks with two aids or frame">Walks with 2 aids/frame</option>
              <option value="Uses a wheelchair / bed bound">Wheelchair/bedbound</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Cognition</label>
            <select value={filters.cogstat} onChange={(e) => handleFilterChange('cogstat', e.target.value)}>
              <option value="">All</option>
              <option value="Normal cognition">Normal cognition</option>
              <option value="Impaired cognition or known dementia">Impaired/dementia</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Frailty</label>
            <select value={filters.frailty} onChange={(e) => handleFilterChange('frailty', e.target.value)}>
              <option value="">All</option>
              <option value="Very Fit">Very Fit</option>
              <option value="Well">Well</option>
              <option value="Well, with treated comorbid disease">Well, with treated comorbid disease</option>
              <option value="Vulnerable">Vulnerable</option>
              <option value="Mildly frail">Mildly frail</option>
              <option value="Moderately frail">Moderately frail</option>
              <option value="Severely frail">Severely frail</option>
              <option value="Very severely frail">Very severely frail</option>
              <option value="Terminally ill">Terminally ill</option>
              <option value="Frailty assessment using other validated tool">Other tool</option>
            </select>
          </div>

          <div className="filter-group">
            <label>ADL Risk/Delirium Risk</label>
            <select value={filters.addelassess} onChange={(e) => handleFilterChange('addelassess', e.target.value)}>
              <option value="">All</option>
              <option value="Not assessed">Not assessed</option>
              <option value="Assessed and not identified">Assessed & not identified</option>
              <option value="Assessed and identified">Assessed & identified</option>
            </select>
          </div>

          {/* 4. FRACTURE CHARACTERISTICS */}
          <div className="section-header">4. Fracture Characteristics</div>

          <div className="filter-group">
            <label>Fracture Type</label>
            <select value={filters.ftype} onChange={(e) => handleFilterChange('ftype', e.target.value)}>
              <option value="">All</option>
              <option value="Intracapsular undisplaced/impacted displaced">Intracapsular undisplaced</option>
              <option value="Intracapsular displaced">Intracapsular displaced</option>
              <option value="Per/intertrochanteric">Inter/pertrochanteric</option>
              <option value="Subtrochanteric">Subtrochanteric</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Atypical/Pathological</label>
            <select value={filters.afracture} onChange={(e) => handleFilterChange('afracture', e.target.value)}>
              <option value="">All</option>
              <option value="Not pathological or atypical fracture">Neither</option>
              <option value="Pathological fracture">Pathological</option>
              <option value="Atypical fracture">Atypical</option>
            </select>
          </div>

          <div className="filter-group">
            <label>ASA Score</label>
            <select value={filters.asa} onChange={(e) => handleFilterChange('asa', e.target.value)}>
              <option value="">All</option>
              <option value="Healthy individual with no systemic disease">ASA 1</option>
              <option value="Mild systemic disease not limiting activity">ASA 2</option>
              <option value="Severe systemic disease that limits activity but is not incapacitating">ASA 3</option>
              <option value="Incapacitating systemic disease constantly life threatening">ASA 4</option>
              <option value="Moribund not expected to survive 24 hours">ASA 5</option>
            </select>
          </div>

          {/* 2. PRESENTATION TO ED */}
          <div className="section-header">2. Presentation to ED</div>

          <div className="filter-group">
            <label>Arrived via ED</label>
            <select value={filters.e_dadmit} onChange={(e) => handleFilterChange('e_dadmit', e.target.value)}>
              <option value="">All</option>
              <option value="Yes">Yes</option>
              <option value="No - transferred from another hospital (via ED)">No - transferred (via ED)</option>
              <option value="No - in-patient fall">No - in-patient fall</option>
              <option value="No - transferred from another hospital (direct to ward)">No - direct to ward</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Pain Assessment</label>
            <select value={filters.painassess} onChange={(e) => handleFilterChange('painassess', e.target.value)}>
              <option value="">All</option>
              <option value="Within 30 minutes of ED presentation">Within 30 min</option>
              <option value="Greater than 30 minutes of ED presentation">&gt;30 min</option>
              <option value="Pain assessment not documented or not done">Not done/documented</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Analgesia Management</label>
            <select value={filters.painmanage} onChange={(e) => handleFilterChange('painmanage', e.target.value)}>
              <option value="">All</option>
              <option value="Given within 30 minutes of ED presentation">Within 30 min</option>
              <option value="Given more than 30 minutes after ED presentation">&gt;30 min</option>
              <option value="Not required – already provided by paramedics">Pre-hospital</option>
              <option value="Not required – no pain documented on assessment">Not required</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Nerve Block</label>
            <select value={filters.analges} onChange={(e) => handleFilterChange('analges', e.target.value)}>
              <option value="">All</option>
              <option value="Nerve block before OT">Before OT</option>
              <option value="Nerve block in OT">In OT</option>
              <option value="Both">Both</option>
              <option value="Neither">Neither</option>
            </select>
          </div>

          {/* 5. SURGICAL PATHWAY */}
          <div className="section-header">5. Surgical Pathway</div>

          <div className="filter-group">
            <label>Surgery Performed</label>
            <select value={filters.surg} onChange={(e) => handleFilterChange('surg', e.target.value)}>
              <option value="">All</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="No – surgical fixation not clinically indicated">Not indicated</option>
              <option value="No – patient for palliation">Palliation</option>
              <option value="No – other reason">Other reason</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Surgical Delay</label>
            <select value={filters.delay} onChange={(e) => handleFilterChange('delay', e.target.value)}>
              <option value="">All</option>
              <option value="No delay, surgery completed <48 hours">&lt;48h (No delay)</option>
              <option value="Delay: patient medically unfit">Medically unfit</option>
              <option value="Delay: anticoagulation issues">Anticoagulation</option>
              <option value="Delay: theatre availability">Theatre unavailable</option>
              <option value="Delay: surgeon availability">Surgeon unavailable</option>
              <option value="Delay: delayed diagnosis of hip fracture">Late diagnosis</option>
              <option value="Other (state reason)">Other</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Anaesthesia Type</label>
            <select value={filters.anaesth} onChange={(e) => handleFilterChange('anaesth', e.target.value)}>
              <option value="">All</option>
              <option value="General anaesthesia">General</option>
              <option value="Spinal anaesthesia">Spinal</option>
              <option value="General and spinal anaesthesia">General + Spinal</option>
              <option value="Spinal / regional anaesthesia">Spinal/regional</option>
              <option value="General and spinal/regional anaesthesia">General + Spinal/regional</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Weight-bearing Post-op</label>
            <select value={filters.wbear} onChange={(e) => handleFilterChange('wbear', e.target.value)}>
              <option value="">All</option>
              <option value="Unrestricted weight bearing">Unrestricted</option>
              <option value="Restricted / non weight bearing">Restricted/non-weight bearing</option>
            </select>
          </div>

          {/* 6. POST-OPERATIVE CARE */}
          <div className="section-header">6. Post-operative Care</div>

          <div className="filter-group">
            <label>Ward Type</label>
            <select value={filters.ward} onChange={(e) => handleFilterChange('ward', e.target.value)}>
              <option value="">All</option>
              <option value="Hip fracture unit/Orthopaedic ward/preferred ward">Preferred ortho ward</option>
              <option value="Outlying ward">Outlier ward</option>
              <option value="HDU / ICU / CCU">HDU/ICU/CCU</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Geriatric Assessment</label>
            <select value={filters.gerimed} onChange={(e) => handleFilterChange('gerimed', e.target.value)}>
              <option value="">All</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="No geriatric medicine service available">No service available</option>
              <option value="Not known">Unknown</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Delirium Assessment</label>
            <select value={filters.delassess} onChange={(e) => handleFilterChange('delassess', e.target.value)}>
              <option value="">All</option>
              <option value="Not assessed">Not assessed</option>
              <option value="Assessed and not identified">Assessed & not identified</option>
              <option value="Assessed and identified">Assessed & identified</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Falls Assessment</label>
            <select value={filters.fassess} onChange={(e) => handleFilterChange('fassess', e.target.value)}>
              <option value="">All</option>
              <option value="Performed during admission">Performed</option>
              <option value="No">Not performed</option>
              <option value="Awaits falls clinic assessment">Awaiting clinic</option>
              <option value="Not relevant">Not relevant</option>
              <option value="Further intervention not appropriate">Not appropriate</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Pressure Ulcers</label>
            <select value={filters.pulcers} onChange={(e) => handleFilterChange('pulcers', e.target.value)}>
              <option value="">All</option>
              <option value="No">No</option>
              <option value="Yes">Yes</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Mobilised Day 1</label>
            <select value={filters.mobil} onChange={(e) => handleFilterChange('mobil', e.target.value)}>
              <option value="">All</option>
              <option value="Mobilised day 1 (opportunity given)">Yes (opportunity given)</option>
              <option value="Not mobilised day 1">Not mobilised</option>
            </select>
          </div>

          {/* 7. BONE HEALTH */}
          <div className="section-header">7. Bone Health & Medications</div>

          <div className="filter-group">
            <label>Bone Protection on Admission</label>
            <select value={filters.bonemed} onChange={(e) => handleFilterChange('bonemed', e.target.value)}>
              <option value="">All</option>
              <option value="No bone protection medication">No</option>
              <option value="Calcium and/or vitamin D only">Calcium/Vitamin D</option>
              <option value="Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT">Anti-resorptives/anabolics</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Bone Protection at Discharge</label>
            <select value={filters.dbonemed1} onChange={(e) => handleFilterChange('dbonemed1', e.target.value)}>
              <option value="">All</option>
              <option value="No bone protection medication">No</option>
              <option value="Yes - Calcium and/or vitamin D only">Yes - Calcium/Vit D</option>
              <option value="Yes - Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT">Yes - Anti-resorptives</option>
              <option value="No but received prescription at separation from hospital">Prescribed at discharge</option>
            </select>
          </div>

          {/* 8. NUTRITION */}
          <div className="section-header">8. Nutrition</div>

          <div className="filter-group">
            <label>Malnutrition Assessment</label>
            <select value={filters.malnutrition} onChange={(e) => handleFilterChange('malnutrition', e.target.value)}>
              <option value="">All</option>
              <option value="Not done">Not done</option>
              <option value="Malnourished">Malnourished</option>
              <option value="Not malnourished">Not malnourished</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Oral Nutritional Supplements</label>
            <select value={filters.ons} onChange={(e) => handleFilterChange('ons', e.target.value)}>
              <option value="">All</option>
              <option value="No">No</option>
              <option value="Yes">Yes</option>
            </select>
          </div>

          {/* 9. DISCHARGE OUTCOMES */}
          <div className="section-header">9. Discharge Outcomes</div>

          <div className="filter-group">
            <label>Discharge Destination</label>
            <select value={filters.wdest} onChange={(e) => handleFilterChange('wdest', e.target.value)}>
              <option value="">All</option>
              <option value="Private residence">Private residence</option>
              <option value="Residential aged care facility">RACF</option>
              <option value="Rehabilitation unit public">Public rehab</option>
              <option value="Rehabilitation unit private">Private rehab</option>
              <option value="Other hospital / ward / specialty">Other hospital</option>
              <option value="Deceased">Deceased</option>
              <option value="Short term care in residential care facility (NZ only)">Short-term care</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Discharge Mobility</label>
            <select value={filters.fwalk2} onChange={(e) => handleFilterChange('fwalk2', e.target.value)}>
              <option value="">All</option>
              <option value="Walks without walking aids">Walks unaided</option>
              <option value="Walks with either a stick or crutch">1 aid</option>
              <option value="Walks with two aids or frame">2 aids/frame</option>
              <option value="Uses a wheelchair / bed bound">Wheelchair/bedbound</option>
              <option value="Not relevant">Not relevant</option>
            </select>
          </div>

          {/* 10. FOLLOW-UP OUTCOMES */}
          <div className="section-header">10. 120-Day Follow-Up</div>

          <div className="filter-group">
            <label>Residence at Follow-up</label>
            <select value={filters.dresidence} onChange={(e) => handleFilterChange('dresidence', e.target.value)}>
              <option value="">All</option>
              <option value="Private residence">Home</option>
              <option value="Residential aged care facility">RACF</option>
              <option value="Deceased">Deceased</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Bone Medication at Follow-up</label>
            <select value={filters.fbonemed2} onChange={(e) => handleFilterChange('fbonemed2', e.target.value)}>
              <option value="">All</option>
              <option value="No bone protection medication">No</option>
              <option value="Calcium and/or vitamin D only">Calcium/Vit D</option>
              <option value="Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT">Anti-resorptives/anabolics</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Reoperation</label>
            <select value={filters.fop2} onChange={(e) => handleFilterChange('fop2', e.target.value)}>
              <option value="">All</option>
              <option value="No reoperation">No reoperation</option>
              <option value="Reduction of dislocated prosthesis">Dislocation</option>
              <option value="Washout or debridement">Washout</option>
              <option value="Implant removal">Implant removal</option>
              <option value="Revision of internal fixation">Revision</option>
              <option value="Conversion to hemiarthroplasty">Conversion to hemi</option>
              <option value="Conversion to total hip replacement">Conversion to THR</option>
              <option value="Excision arthroplasty">Excision arthroplasty</option>
              <option value="Periprosthetic fracture">Periprosthetic fracture</option>
              <option value="Revision arthroplasty">Revision arthroplasty</option>
              <option value="Not relevant">Not relevant</option>
            </select>
          </div>

          <button 
            className="build-btn"
            onClick={buildCohort}
            disabled={loading}
          >
            {loading ? 'Building...' : 'Build Cohort'}
          </button>
        </div>

        <div className="results-section">
          <h2>Results</h2>
          
          {error && (
            <div className="error">
              <p>Error: {error}</p>
              <p>Make sure the backend is running on port 5050</p>
            </div>
          )}

          {cohortSize !== null && !error && (
            <div className="cohort-result">
              <div className="cohort-count">
                <span className="count-number">{cohortSize}</span>
                <span className="count-label">patients in cohort</span>
              </div>
              
              <button 
                className="save-cohort-btn"
                onClick={() => setShowSaveDialog(true)}
              >
                Save Cohort
              </button>

              {showSaveDialog && (
                <div className="save-dialog">
                  <input
                    type="text"
                    placeholder="Enter cohort name..."
                    value={cohortName}
                    onChange={(e) => setCohortName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && saveCohort()}
                  />
                  <div className="dialog-buttons">
                    <button onClick={saveCohort}>Save</button>
                    <button onClick={() => {setShowSaveDialog(false); setCohortName('')}}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          )}

          {cohortSize === null && !error && !loading && (
            <div className="placeholder">
              <p>Select filters and click "Build Cohort" to see results</p>
            </div>
          )}

          <div className="saved-cohorts-section">
            <h3>Saved Cohorts</h3>
            {savedCohorts.length === 0 ? (
              <p className="no-cohorts">No saved cohorts yet</p>
            ) : (
              <div className="cohorts-list">
                {savedCohorts.map((cohort) => (
                  <div key={cohort.id} className="cohort-item">
                    <div className="cohort-info">
                      <span className="cohort-name">{cohort.name}</span>
                      <span className="cohort-count-small">{cohort.count} patients</span>
                    </div>
                    <button 
                      className="delete-btn"
                      onClick={() => deleteCohort(cohort.id, cohort.name)}
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
