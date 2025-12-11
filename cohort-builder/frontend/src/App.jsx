import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Fetching data from backend...')
      const response = await fetch('http://localhost:5000/api/data')
      console.log('Response:', response)
      if (!response.ok) {
        throw new Error('Failed to fetch data')
      }
      const result = await response.json()
      console.log('Data received:', result)
      setData(result)
    } catch (err) {
      console.error('Error fetching data:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>React + Python Backend</h1>
      
      <div className="card">
        <button onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Data from Backend'}
        </button>
        
        {error && (
          <div className="error">
            <p>Error: {error}</p>
            <p>Make sure the Python backend is running on port 5000</p>
          </div>
        )}
        
        {data && (
          <div className="data-display">
            <h2>{data.message}</h2>
            <ul>
              {data.items.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
