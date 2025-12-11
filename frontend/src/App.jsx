import { useState, useEffect } from 'react'
import './App.css'
import axios from "axios"

function App() {
  const [filters, setFilters] = useState({
    // Demographics
    minAge: '',
    maxAge: '',
    sex: [],
    ptype: [],
    uresidence: [],
    
    // Pre-fracture Functional Status
    walk: [],
    cogstat: [],
    frailty: [],
    addelassess: [],
    
    // Fracture Characteristics
    ftype: [],
    afracture: [],
    asa: [],
    
    // Presentation to ED
    e_dadmit: [],
    painassess: [],
    painmanage: [],
    analges: [],
    
    // Surgical Pathway
    surg: [],
    delay: [],
    anaesth: [],
    wbear: [],
    
    // Post-operative Care
    ward: [],
    gerimed: [],
    delassess: [],
    fassess: [],
    pulcers: [],
    mobil: [],
    
    // Bone Health
    bonemed: [],
    dbonemed1: [],
    
    // Nutrition
    malnutrition: [],
    ons: [],
    
    // Discharge Outcomes
    wdest: [],
    fwalk2: [],
    
    // Follow-up Outcomes
    dresidence: [],
    fbonemed2: [],
    fop2: []
  })
  const [cohortSize, setCohortSize] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedCohorts, setSavedCohorts] = useState([])
  const [cohortName, setCohortName] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [expandedFilters, setExpandedFilters] = useState({})

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

  const handleCheckboxChange = (field, value) => {
    setFilters(prev => {
      const currentValues = prev[field] || []
      const isChecked = currentValues.includes(value)
      
      return {
        ...prev,
        [field]: isChecked 
          ? currentValues.filter(v => v !== value)
          : [...currentValues, value]
      }
    })
  }

  const toggleFilterExpansion = (filterId) => {
    setExpandedFilters(prev => ({
      ...prev,
      [filterId]: !prev[filterId]
    }))
  }

  const CollapsibleFilter = ({ id, label, options, field, displayMap = {} }) => (
    <div className="filter-group">
      <label onClick={() => toggleFilterExpansion(id)} className="filter-label-collapse">
        <span>{label}</span>
        <span className="collapse-icon">{expandedFilters[id] ? '− ' : '+ '}</span>
      </label>
      {expandedFilters[id] && (
        <div className="checkbox-group">
          {options.map(option => (
            <label key={option} className="checkbox-label">
              <input
                type="checkbox"
                checked={filters[field].includes(option)}
                onChange={() => handleCheckboxChange(field, option)}
              />
              <span>{displayMap[option] || option}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  )

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
      <div className="app-header">
        <h1>Hip Fracture Cohort Builder</h1>
        <a href="/cohorts" className="view-cohorts-link">View Saved Cohorts →</a>
      </div>
      
      <div className="sections-grid">
        {/* 1. DEMOGRAPHICS */}
        <div className="section-box">
          <div className="section-header-box">Demographics</div>
          <div className="filter-group">
            <label>Age Range</label>
            <div className="age-inputs">
              <input
                type="number"
                placeholder="Min"
                value={filters.minAge}
                onChange={(e) => handleFilterChange('minAge', e.target.value)}
              />
              <span>to</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.maxAge}
                onChange={(e) => handleFilterChange('maxAge', e.target.value)}
              />
            </div>
          </div>
          <div className="filter-group">
            <label onClick={() => toggleFilterExpansion('sex')} className="filter-label-collapse">
              <span>Sex</span>
              <span className="collapse-icon">{expandedFilters['sex'] ? '− ' : '+ '}</span>
            </label>
            {expandedFilters['sex'] && (
              <div className="checkbox-group">
                {['Male', 'Female', 'Intersex or indeterminate'].map(option => (
                  <label key={option} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.sex.includes(option)}
                      onChange={() => handleCheckboxChange('sex', option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
          <div className="filter-group">
            <label onClick={() => toggleFilterExpansion('ptype')} className="filter-label-collapse">
              <span>Patient Type</span>
              <span className="collapse-icon">{expandedFilters['ptype'] ? '− ' : '+ '}</span>
            </label>
            {expandedFilters['ptype'] && (
              <div className="checkbox-group">
                {['Public', 'Private', 'Overseas'].map(option => (
                  <label key={option} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.ptype.includes(option)}
                      onChange={() => handleCheckboxChange('ptype', option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
          <div className="filter-group">
            <label onClick={() => toggleFilterExpansion('uresidence')} className="filter-label-collapse">
              <span>Usual Residence</span>
              <span className="collapse-icon">{expandedFilters['uresidence'] ? '− ' : '+ '}</span>
            </label>
            {expandedFilters['uresidence'] && (
              <div className="checkbox-group">
                {['Private residence', 'Residential aged care facility', 'Other'].map(option => (
                  <label key={option} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.uresidence.includes(option)}
                      onChange={() => handleCheckboxChange('uresidence', option)}
                    />
                    <span>{option === 'Residential aged care facility' ? 'RACF' : option}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 2. PRESENTATION TO ED */}
        <div className="section-box">
          <div className="section-header-box">Presentation to ED</div>
          <CollapsibleFilter 
            id="e_dadmit"
            label="Arrived via ED"
            field="e_dadmit"
            options={['Yes', 'No - transferred from another hospital (via ED)', 'No - in-patient fall', 'No - transferred from another hospital (direct to ward)']}
            displayMap={{
              'No - transferred from another hospital (via ED)': 'No - transferred (via ED)',
              'No - transferred from another hospital (direct to ward)': 'No - direct to ward'
            }}
          />
          <CollapsibleFilter 
            id="painassess"
            label="Pain Assessment"
            field="painassess"
            options={['Within 30 minutes of ED presentation', 'Greater than 30 minutes of ED presentation', 'Pain assessment not documented or not done']}
            displayMap={{
              'Within 30 minutes of ED presentation': 'Within 30 min',
              'Greater than 30 minutes of ED presentation': '>30 min',
              'Pain assessment not documented or not done': 'Not done/documented'
            }}
          />
          <CollapsibleFilter 
            id="painmanage"
            label="Analgesia Management"
            field="painmanage"
            options={['Given within 30 minutes of ED presentation', 'Given more than 30 minutes after ED presentation', 'Not required – already provided by paramedics', 'Not required – no pain documented on assessment']}
            displayMap={{
              'Given within 30 minutes of ED presentation': 'Within 30 min',
              'Given more than 30 minutes after ED presentation': '>30 min',
              'Not required – already provided by paramedics': 'Pre-hospital',
              'Not required – no pain documented on assessment': 'Not required'
            }}
          />
          <CollapsibleFilter 
            id="analges"
            label="Nerve Block"
            field="analges"
            options={['Nerve block before OT', 'Nerve block in OT', 'Both', 'Neither']}
            displayMap={{
              'Nerve block before OT': 'Before OT',
              'Nerve block in OT': 'In OT'
            }}
          />
        </div>

        {/* 3. PRE-FRACTURE FUNCTIONAL STATUS */}
        <div className="section-box">
          <div className="section-header-box">Pre-fracture Status</div>
          <CollapsibleFilter 
            id="walk"
            label="Mobility Ability"
            field="walk"
            options={['Walks without walking aids', 'Walks with either a stick or crutch', 'Walks with two aids or frame', 'Uses a wheelchair / bed bound']}
            displayMap={{
              'Walks without walking aids': 'Walks unaided',
              'Walks with either a stick or crutch': 'Walks with 1 aid',
              'Walks with two aids or frame': 'Walks with 2 aids/frame',
              'Uses a wheelchair / bed bound': 'Wheelchair/bedbound'
            }}
          />
          <CollapsibleFilter 
            id="cogstat"
            label="Cognition"
            field="cogstat"
            options={['Normal cognition', 'Impaired cognition or known dementia']}
            displayMap={{
              'Impaired cognition or known dementia': 'Impaired/dementia'
            }}
          />
          <CollapsibleFilter 
            id="frailty"
            label="Frailty"
            field="frailty"
            options={['Very Fit', 'Well', 'Well, with treated comorbid disease', 'Vulnerable', 'Mildly frail', 'Moderately frail', 'Severely frail', 'Very severely frail', 'Terminally ill', 'Frailty assessment using other validated tool']}
            displayMap={{
              'Frailty assessment using other validated tool': 'Other tool'
            }}
          />
          <CollapsibleFilter 
            id="addelassess"
            label="ADL/Delirium Risk"
            field="addelassess"
            options={['Not assessed', 'Assessed and not identified', 'Assessed and identified']}
            displayMap={{
              'Assessed and not identified': 'Assessed & not identified',
              'Assessed and identified': 'Assessed & identified'
            }}
          />
        </div>

        {/* 4. FRACTURE CHARACTERISTICS */}
        <div className="section-box">
          <div className="section-header-box">Fracture Characteristics</div>
          <CollapsibleFilter 
            id="ftype"
            label="Fracture Type"
            field="ftype"
            options={['Intracapsular undisplaced/impacted displaced', 'Intracapsular displaced', 'Per/intertrochanteric', 'Subtrochanteric']}
            displayMap={{
              'Intracapsular undisplaced/impacted displaced': 'Intracapsular undisplaced',
              'Per/intertrochanteric': 'Inter/pertrochanteric'
            }}
          />
          <CollapsibleFilter 
            id="afracture"
            label="Atypical/Pathological"
            field="afracture"
            options={['Not pathological or atypical fracture', 'Pathological fracture', 'Atypical fracture']}
            displayMap={{
              'Not pathological or atypical fracture': 'Neither',
              'Pathological fracture': 'Pathological',
              'Atypical fracture': 'Atypical'
            }}
          />
          <CollapsibleFilter 
            id="asa"
            label="ASA Score"
            field="asa"
            options={['Healthy individual with no systemic disease', 'Mild systemic disease not limiting activity', 'Severe systemic disease that limits activity but is not incapacitating', 'Incapacitating systemic disease constantly life threatening', 'Moribund not expected to survive 24 hours']}
            displayMap={{
              'Healthy individual with no systemic disease': 'ASA 1',
              'Mild systemic disease not limiting activity': 'ASA 2',
              'Severe systemic disease that limits activity but is not incapacitating': 'ASA 3',
              'Incapacitating systemic disease constantly life threatening': 'ASA 4',
              'Moribund not expected to survive 24 hours': 'ASA 5'
            }}
          />
        </div>

        {/* 5. SURGICAL PATHWAY */}
        <div className="section-box">
          <div className="section-header-box">Surgical Pathway</div>
          <CollapsibleFilter 
            id="surg"
            label="Surgery Performed"
            field="surg"
            options={['Yes', 'No', 'No – surgical fixation not clinically indicated', 'No – patient for palliation', 'No – other reason']}
            displayMap={{
              'No – surgical fixation not clinically indicated': 'Not indicated',
              'No – patient for palliation': 'Palliation',
              'No – other reason': 'Other reason'
            }}
          />
          <CollapsibleFilter 
            id="delay"
            label="Surgical Delay"
            field="delay"
            options={['No delay, surgery completed <48 hours', 'Delay: patient medically unfit', 'Delay: anticoagulation issues', 'Delay: theatre availability', 'Delay: surgeon availability', 'Delay: delayed diagnosis of hip fracture', 'Other (state reason)']}
            displayMap={{
              'No delay, surgery completed <48 hours': '<48h (No delay)',
              'Delay: patient medically unfit': 'Medically unfit',
              'Delay: anticoagulation issues': 'Anticoagulation',
              'Delay: theatre availability': 'Theatre unavailable',
              'Delay: surgeon availability': 'Surgeon unavailable',
              'Delay: delayed diagnosis of hip fracture': 'Late diagnosis',
              'Other (state reason)': 'Other'
            }}
          />
          <CollapsibleFilter 
            id="anaesth"
            label="Anaesthesia Type"
            field="anaesth"
            options={['General anaesthesia', 'Spinal anaesthesia', 'General and spinal anaesthesia', 'Spinal / regional anaesthesia', 'General and spinal/regional anaesthesia', 'Other']}
            displayMap={{
              'General anaesthesia': 'General',
              'Spinal anaesthesia': 'Spinal',
              'General and spinal anaesthesia': 'General + Spinal',
              'Spinal / regional anaesthesia': 'Spinal/regional',
              'General and spinal/regional anaesthesia': 'General + Spinal/regional'
            }}
          />
          <CollapsibleFilter 
            id="wbear"
            label="Weight-bearing Post-op"
            field="wbear"
            options={['Unrestricted weight bearing', 'Restricted / non weight bearing']}
            displayMap={{
              'Unrestricted weight bearing': 'Unrestricted',
              'Restricted / non weight bearing': 'Restricted/non-weight bearing'
            }}
          />
        </div>

        {/* 6. POST-OPERATIVE CARE */}
        <div className="section-box">
          <div className="section-header-box">Post-operative Care</div>
          <CollapsibleFilter 
            id="ward"
            label="Ward Type"
            field="ward"
            options={['Hip fracture unit/Orthopaedic ward/preferred ward', 'Outlying ward', 'HDU / ICU / CCU']}
            displayMap={{
              'Hip fracture unit/Orthopaedic ward/preferred ward': 'Preferred ortho ward',
              'Outlying ward': 'Outlier ward',
              'HDU / ICU / CCU': 'HDU/ICU/CCU'
            }}
          />
          <CollapsibleFilter 
            id="gerimed"
            label="Geriatric Assessment"
            field="gerimed"
            options={['Yes', 'No', 'No geriatric medicine service available', 'Not known']}
            displayMap={{
              'No geriatric medicine service available': 'No service available',
              'Not known': 'Unknown'
            }}
          />
          <CollapsibleFilter 
            id="delassess"
            label="Delirium Assessment"
            field="delassess"
            options={['Not assessed', 'Assessed and not identified', 'Assessed and identified']}
            displayMap={{
              'Assessed and not identified': 'Assessed & not identified',
              'Assessed and identified': 'Assessed & identified'
            }}
          />
          <CollapsibleFilter 
            id="fassess"
            label="Falls Assessment"
            field="fassess"
            options={['Performed during admission', 'No', 'Awaits falls clinic assessment', 'Not relevant', 'Further intervention not appropriate']}
            displayMap={{
              'Performed during admission': 'Performed',
              'No': 'Not performed',
              'Awaits falls clinic assessment': 'Awaiting clinic',
              'Further intervention not appropriate': 'Not appropriate'
            }}
          />
          <CollapsibleFilter 
            id="pulcers"
            label="Pressure Ulcers"
            field="pulcers"
            options={['No', 'Yes']}
          />
          <CollapsibleFilter 
            id="mobil"
            label="Mobilised Day 1"
            field="mobil"
            options={['Mobilised day 1 (opportunity given)', 'Not mobilised day 1']}
            displayMap={{
              'Mobilised day 1 (opportunity given)': 'Yes (opportunity given)',
              'Not mobilised day 1': 'Not mobilised'
            }}
          />
        </div>

        {/* 7. BONE HEALTH */}
        <div className="section-box">
          <div className="section-header-box">Bone Health</div>
          <CollapsibleFilter 
            id="bonemed"
            label="Bone Protection on Admission"
            field="bonemed"
            options={['No bone protection medication', 'Calcium and/or vitamin D only', 'Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT']}
            displayMap={{
              'No bone protection medication': 'No',
              'Calcium and/or vitamin D only': 'Calcium/Vitamin D',
              'Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT': 'Anti-resorptives/anabolics'
            }}
          />
          <CollapsibleFilter 
            id="dbonemed1"
            label="Bone Protection at Discharge"
            field="dbonemed1"
            options={['No bone protection medication', 'Yes - Calcium and/or vitamin D only', 'Yes - Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT', 'No but received prescription at separation from hospital']}
            displayMap={{
              'No bone protection medication': 'No',
              'Yes - Calcium and/or vitamin D only': 'Yes - Calcium/Vit D',
              'Yes - Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT': 'Yes - Anti-resorptives',
              'No but received prescription at separation from hospital': 'Prescribed at discharge'
            }}
          />
        </div>

        {/* 8. NUTRITION */}
        <div className="section-box">
          <div className="section-header-box">Nutrition</div>
          <CollapsibleFilter 
            id="malnutrition"
            label="Malnutrition Assessment"
            field="malnutrition"
            options={['Not done', 'Malnourished', 'Not malnourished']}
          />
          <CollapsibleFilter 
            id="ons"
            label="Oral Nutritional Supplements"
            field="ons"
            options={['No', 'Yes']}
          />
        </div>

        {/* 9. DISCHARGE OUTCOMES */}
        <div className="section-box">
          <div className="section-header-box">Discharge Outcomes</div>
          <CollapsibleFilter 
            id="wdest"
            label="Discharge Destination"
            field="wdest"
            options={['Private residence', 'Residential aged care facility', 'Rehabilitation unit public', 'Rehabilitation unit private', 'Other hospital / ward / specialty', 'Deceased', 'Short term care in residential care facility (NZ only)', 'Other']}
            displayMap={{
              'Residential aged care facility': 'RACF',
              'Rehabilitation unit public': 'Public rehab',
              'Rehabilitation unit private': 'Private rehab',
              'Other hospital / ward / specialty': 'Other hospital',
              'Short term care in residential care facility (NZ only)': 'Short-term care'
            }}
          />
          <CollapsibleFilter 
            id="fwalk2"
            label="Discharge Mobility"
            field="fwalk2"
            options={['Walks without walking aids', 'Walks with either a stick or crutch', 'Walks with two aids or frame', 'Uses a wheelchair / bed bound', 'Not relevant']}
            displayMap={{
              'Walks without walking aids': 'Walks unaided',
              'Walks with either a stick or crutch': '1 aid',
              'Walks with two aids or frame': '2 aids/frame',
              'Uses a wheelchair / bed bound': 'Wheelchair/bedbound'
            }}
          />
        </div>

        {/* 10. 120-DAY FOLLOW-UP */}
        <div className="section-box">
          <div className="section-header-box">120-Day Follow-Up</div>
          <CollapsibleFilter 
            id="dresidence"
            label="Residence at Follow-up"
            field="dresidence"
            options={['Private residence', 'Residential aged care facility', 'Deceased', 'Other']}
            displayMap={{
              'Private residence': 'Home',
              'Residential aged care facility': 'RACF'
            }}
          />
          <CollapsibleFilter 
            id="fbonemed2"
            label="Bone Medication at Follow-up"
            field="fbonemed2"
            options={['No bone protection medication', 'Calcium and/or vitamin D only', 'Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT']}
            displayMap={{
              'No bone protection medication': 'No',
              'Calcium and/or vitamin D only': 'Calcium/Vit D',
              'Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT': 'Anti-resorptives/anabolics'
            }}
          />
          <CollapsibleFilter 
            id="fop2"
            label="Reoperation"
            field="fop2"
            options={['No reoperation', 'Reduction of dislocated prosthesis', 'Washout or debridement', 'Implant removal', 'Revision of internal fixation', 'Conversion to hemiarthroplasty', 'Conversion to total hip replacement', 'Excision arthroplasty', 'Periprosthetic fracture', 'Revision arthroplasty', 'Not relevant']}
            displayMap={{
              'Reduction of dislocated prosthesis': 'Dislocation',
              'Washout or debridement': 'Washout',
              'Revision of internal fixation': 'Revision',
              'Conversion to hemiarthroplasty': 'Conversion to hemi',
              'Conversion to total hip replacement': 'Conversion to THR'
            }}
          />
        </div>
      </div>

      {/* Build Button and Results */}
      <div className="build-section">
        <button 
          className="build-btn"
          onClick={buildCohort}
          disabled={loading}
        >
          {loading ? 'Building...' : 'Build Cohort'}
        </button>

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
  )
}

export default App
