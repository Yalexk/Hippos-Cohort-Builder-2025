import { useState, useEffect } from 'react'
import './Cohorts.css'
import axios from "axios"

function Cohorts() {
  const [savedCohorts, setSavedCohorts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState(null) // {id, name, img}

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
      // Show only the selected cohort's image in the right sidebar
      if (response.data.mortality_chart) {
        setSelectedAnalysis({ id: cohortId, name: cohortName, img: response.data.mortality_chart })
      } else {
        setSelectedAnalysis(null)
      }
      
    } catch (err) {
      console.error('Error analysing cohort:', err)
      alert('Failed to analyse cohort')
    }
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleDateString('en-AU', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
          <div className="analysis-panel-header">Analysis</div>
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
                </div>
              </div>
              <div className="analysis-chart">
                <img src={selectedAnalysis.img} alt={`Analysis for ${selectedAnalysis.name}`} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Cohorts
