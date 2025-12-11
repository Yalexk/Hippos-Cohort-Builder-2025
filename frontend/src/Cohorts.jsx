import { useState, useEffect } from 'react'
import './Cohorts.css'
import axios from "axios"

function Cohorts() {
  const [savedCohorts, setSavedCohorts] = useState([])
  const [loading, setLoading] = useState(true)

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
      
      // TODO: Navigate to analysis page or display results
      // For now, just log and alert
      alert(`Analysis complete for "${cohortName}"!\n\nPatients: ${response.data.total_patients}\n30-day mortality: ${response.data.mortality['30_day']?.rate?.toFixed(1)}%\n\nCheck console for full results.`)
      
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

      {savedCohorts.length === 0 ? (
        <div className="empty-state">
          <p>No saved cohorts yet</p>
          <a href="/" className="build-link">Build your first cohort</a>
        </div>
      ) : (
        <div className="cohorts-grid">
          {savedCohorts.map((cohort) => (
            <div key={cohort.id} className="cohort-card">
              <div className="cohort-card-header">
                <h3>{cohort.name}</h3>
                <button 
                  className="delete-btn-card"
                  onClick={() => deleteCohort(cohort.id, cohort.name)}
                  title="Delete cohort"
                >
                  ×
                </button>
              </div>
              
              <div className="cohort-stats">
                <div className="stat-item">
                  <span className="stat-label">Patients</span>
                  <span className="stat-value">{cohort.count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Filters Applied</span>
                  <span className="stat-value">{getActiveFiltersCount(cohort.filters)}</span>
                </div>
              </div>

              <div className="cohort-meta">
                <span className="cohort-date">
                  Created: {formatDate(cohort.created_at)}
                </span>
              </div>

              <div className="cohort-actions">
                <button className="btn-secondary">View Details</button>
                <button 
                  className="btn-primary"
                  onClick={() => analyseCohort(cohort.id, cohort.name)}
                >
                  Analyse
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Cohorts
