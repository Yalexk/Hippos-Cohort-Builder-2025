import { useState, useEffect } from 'react'
import './Cohorts.css'
import axios from "axios"

// Configuration for charts - easy to expand later
const CHART_OPTIONS = [
  { id: 'all', label: 'Show All Charts' },
  { id: 'mortality', label: 'Mortality Status Across Time Frames' },
  { id: 'walking', label: 'Walking Ability After 120 Days' },
  { id: 'fracture', label: 'Fracture Classification' },
  { id: 'residence', label: 'Pre-Admission Residence Status' },
  { id: 'transition', label: 'Residence Transitions: Admissions to Discharge' }
]

function Cohorts() {
  const [savedCohorts, setSavedCohorts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  // New state for the dropdown selection
  const [activeChart, setActiveChart] = useState('all') 

  useEffect(() => {
    loadSavedCohorts()
  }, [])

  const loadSavedCohorts = async () => {
    try {
      setLoading(true)
      const response = await axios.get("http://localhost:5050/api/cohorts")
      setSavedCohorts(Object.values(response.data))
    } catch (err) {
      console.error('Error loading cohorts:', err)
    } finally {
      setLoading(false)
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

  const analyseCohort = async (cohortId, cohortName) => {
    try {
      const response = await axios.post(`http://localhost:5050/api/cohorts/${cohortId}/analyse`)
      console.log('Analysis results:', response.data)
      console.log('Enhanced metrics:', response.data.enhanced_metrics)
      
      // Reset view to 'all' when a new cohort is selected
      setActiveChart('all')

      // Store all analysis charts in state
      setSelectedAnalysis({ 
        id: cohortId, 
        name: cohortName, 
        mortalityImg: response.data.mortality_chart,
        fwalk2Img: response.data.fwalk2_chart, 
        afractureImg: response.data.afracture_chart,
        residenceImg: response.data.residence_chart,
        residenceTransitionImg: response.data.residence_transition_chart,
        enhancedMetrics: response.data.enhanced_metrics || {}
      })
      
    } catch (err) {
      console.error('Error analysing cohort:', err)
      alert('Failed to analyse cohort')
    }
  }

  const getActiveFiltersCount = (filters) => {
    let count = 0
    if (filters.minAge || filters.maxAge) count++
    
    Object.keys(filters).forEach(key => {
      if (key !== 'minAge' && key !== 'maxAge' && filters[key]?.length > 0) {
        count++
      }
    })
    return count
  }

  // Helper to check if a chart should be displayed
  const shouldShow = (chartId) => {
    return activeChart === 'all' || activeChart === chartId
  }

  if (loading) {
    return (
      <div className="cohorts-page">
        <div className="cohorts-header">
          <h1>Saved Cohorts</h1>
          <a href="/" className="back-link">← Back to Builder</a>
        </div>
        <div className="loading-message">Loading cohorts...</div>
      </div>
    )
  }

  return (
    <div className="cohorts-page">
      <div className="cohorts-header">
        <h1>Saved Cohorts</h1>
        <a href="/" className="back-link">← Back to Builder</a>
      </div>

      <div className="cohorts-content">
        <aside className="cohorts-sidebar">
          <div className="cohorts-list">
            {savedCohorts.length === 0 ? (
              <div className="empty-state-sidebar">
                <p>No saved cohorts yet</p>
                <a href="/" className="build-link-small">Build cohort</a>
              </div>
            ) : (
              savedCohorts.map((cohort) => (
                <div 
                  key={cohort.id} 
                  className={`cohort-list-item ${selectedAnalysis?.id === cohort.id ? 'active' : ''}`}
                  onClick={() => analyseCohort(cohort.id, cohort.name)}
                >
                  <div className="cohort-list-name">{cohort.name}</div>
                  <button 
                    className="delete-btn-small"
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteCohort(cohort.id, cohort.name)
                    }}
                    title="Delete cohort"
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>
        <div className="analysis-panel">
          <div className="analysis-panel-header">
            Cohort Outcomes and Information Dashboard
          </div>
          {!selectedAnalysis ? (
            <div className="analysis-empty">Select a cohort to analyse</div>
          ) : (
            <div className="analysis-content">
              <div className="analysis-meta">
                <h3>{selectedAnalysis.name}</h3>
                
                <div className="analysis-stats">
                  <div className="stat-chip">
                    <span className="stat-label">Patients:</span>
                    <span className="stat-value">{savedCohorts.find(c => c.id === selectedAnalysis.id)?.count || 0}</span>
                  </div>
                  <div className="stat-chip">
                    <span className="stat-label">Filters Applied:</span>
                    <span className="stat-value">{getActiveFiltersCount(savedCohorts.find(c => c.id === selectedAnalysis.id)?.filters || {})}</span>
                  </div>
                  {selectedAnalysis.enhancedMetrics?.n_hospitals !== undefined && selectedAnalysis.enhancedMetrics.n_hospitals > 0 && (
                    <div className="stat-chip">
                      <span className="stat-label">Hospitals:</span>
                      <span className="stat-value">{selectedAnalysis.enhancedMetrics.n_hospitals}</span>
                    </div>
                  )}
                  {selectedAnalysis.enhancedMetrics?.date_range && selectedAnalysis.enhancedMetrics.date_range !== 'Unknown' && (
                    <div className="stat-chip">
                      <span className="stat-label">Date Range:</span>
                      <span className="stat-value">{selectedAnalysis.enhancedMetrics.date_range}</span>
                    </div>
                  )}
                  {selectedAnalysis.enhancedMetrics?.imputation_rate !== undefined && selectedAnalysis.enhancedMetrics.imputation_rate > 0 && (
                    <div className={`stat-chip ${selectedAnalysis.enhancedMetrics.imputation_rate > 20 ? 'stat-chip-warning' : ''}`}>
                      <span className="stat-label">Imputed Data:</span>
                      <span className="stat-value">
                        {selectedAnalysis.enhancedMetrics.patients_with_imputation} patients ({selectedAnalysis.enhancedMetrics.imputation_rate}%)
                        {selectedAnalysis.enhancedMetrics.avg_imputed_fields > 0 && (
                          <span style={{fontSize: '0.85em', color: '#666'}}> • avg {selectedAnalysis.enhancedMetrics.avg_imputed_fields} fields</span>
                        )}
                      </span>
                    </div>
                  )}
                </div>

                {/* Imputation Breakdown Details */}
                {selectedAnalysis.enhancedMetrics?.imputation_by_field && Object.keys(selectedAnalysis.enhancedMetrics.imputation_by_field).length > 0 && (
                  <div className="imputation-breakdown">
                    <h4>Imputation Breakdown by Field</h4>
                    <table className="breakdown-table">
                      <thead>
                        <tr>
                          <th>Field</th>
                          <th>Imputed Patients</th>
                          <th>Rate</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(selectedAnalysis.enhancedMetrics.imputation_by_field).map(([field, data]) => (
                          <tr key={field}>
                            <td>{field.replace(/_/g, ' ')}</td>
                            <td>{data.count}</td>
                            <td className={data.percent > 20 ? 'high-imputation' : ''}>{data.percent}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* New Dropdown Toolbar */}
                <div className="chart-controls">
                  <label htmlFor="chart-selector">Select Diagram:</label>
                  <select 
                    id="chart-selector"
                    value={activeChart} 
                    onChange={(e) => setActiveChart(e.target.value)}
                    className="chart-select"
                  >
                    {CHART_OPTIONS.map(option => (
                      <option key={option.id} value={option.id}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="charts-container">
                {/* 1. Mortality Chart */}
                {shouldShow('mortality') && selectedAnalysis.mortalityImg && (
                  <div className="analysis-chart">
                    <img src={selectedAnalysis.mortalityImg} alt={`Mortality Analysis for ${selectedAnalysis.name}`} />
                  </div>
                )}

                {/* 2. Walking Ability Chart */}
                {shouldShow('walking') && selectedAnalysis.fwalk2Img && (
                  <div className="analysis-chart">
                    <img src={selectedAnalysis.fwalk2Img} alt={`Walking Ability Analysis for ${selectedAnalysis.name}`} />
                  </div>
                )}

                {/* 3. Atypical Fracture Chart */}
                {shouldShow('fracture') && selectedAnalysis.afractureImg && (
                  <div className="analysis-chart">
                    <img src={selectedAnalysis.afractureImg} alt={`Fracture Type Analysis for ${selectedAnalysis.name}`} />
                  </div>
                )}

                {/* 4. Residence Chart */}
                {shouldShow('residence') && selectedAnalysis.residenceImg && (
                  <div className="analysis-chart">
                    <img src={selectedAnalysis.residenceImg} alt={`Pre-Admission Residence Analysis for ${selectedAnalysis.name}`} />
                  </div>
                )}

                {/* 5. Residence Transition Chart */}
                {shouldShow('transition') && selectedAnalysis.residenceTransitionImg && (
                  <div className="analysis-chart">
                    <img src={selectedAnalysis.residenceTransitionImg} alt={`Residence Transition Analysis for ${selectedAnalysis.name}`} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Cohorts