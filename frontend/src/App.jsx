import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch summary')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Article Summarizer</h1>
      <p style={{ marginBottom: '2rem', color: '#aaa' }}>
        Paste a URL to get a concise summary and key insights powered by Groq & LangChain.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="url"
            placeholder="https://example.com/article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? (
              <>
                Summarizing <span className="loading"></span>
              </>
            ) : (
              'Summarize'
            )}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ color: '#ff6b6b', marginTop: '1rem' }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div className="results">
          <div className="summary-card">
            <h2>Summary</h2>
            <p>{result.summary}</p>
          </div>

          <div className="insights-card">
            <h2>Key Insights</h2>
            <ul>
              {result.key_insights.map((insight, index) => (
                <li key={index}>{insight}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
