import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [style, setStyle] = useState('executive')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [question, setQuestion] = useState('')
  const [qaLoading, setQaLoading] = useState(false)
  const [conversation, setConversation] = useState([])

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
        body: JSON.stringify({ url, style }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch summary')
      }

      const data = await response.json()
      setResult(data)
      setSessionId(data.session_id)
      setConversation([]) // Reset conversation for new summary
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const askQuestion = async (e) => {
    e.preventDefault()
    if (!question.trim() || !sessionId) return

    setQaLoading(true)
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: question.trim()
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get answer')
      }

      const data = await response.json()
      setConversation(data.conversation_history)
      setQuestion('') // Clear input
    } catch (err) {
      setError(err.message)
    } finally {
      setQaLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>AI Summarizer</h1>
      <p style={{ marginBottom: '2rem', color: '#aaa' }}>
        Paste an article URL or YouTube link to get a concise summary and key insights powered by Groq & LangChain.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="url"
            placeholder="https://example.com/article or https://youtube.com/watch?v=..."
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

        <div className="style-selector-container">
          <label htmlFor="style-select" className="style-label">
            Summarization Style:
          </label>
          <select
            id="style-select"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="style-select"
          >
            <option value="executive">📋 Executive Summary (Brief)</option>
            <option value="detailed">📖 Detailed Analysis (Comprehensive)</option>
            <option value="bullet_points">📝 Bullet Points Only (Structured)</option>
            <option value="academic">🎓 Academic Style (Formal)</option>
          </select>
        </div>
      </form>

      {error && (
        <div style={{ color: '#ff6b6b', marginTop: '1rem' }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div className="results">
          <div style={{
            display: 'inline-block',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            background: result.content_type === 'youtube' ? '#F38181' : '#95E1D3',
            color: result.content_type === 'youtube' ? '#fff' : '#2c3e50',
            marginBottom: '1rem',
            fontSize: '0.9rem',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            border: '2px solid rgba(0,0,0,0.1)',
            boxShadow: '4px 4px 0 rgba(0,0,0,0.1)'
          }}>
            {result.content_type === 'youtube' ? '📺 YouTube Video' : '📄 Article'}
          </div>

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

      {result && sessionId && (
        <div className="qa-section" style={{ marginTop: '2rem' }}>
          <h2>💬 Ask Questions About This Content</h2>
          <p style={{ marginBottom: '1rem', color: '#7f8c8d' }}>
            Ask follow-up questions about the summarized content. The AI remembers the context and our conversation.
          </p>

          <form onSubmit={askQuestion} style={{ marginBottom: '2rem' }}>
            <div className="input-group">
              <input
                type="text"
                placeholder="Ask a question about this content..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                required
                disabled={qaLoading}
              />
              <button type="submit" disabled={qaLoading || !question.trim()}>
                {qaLoading ? (
                  <>
                    Thinking <span className="loading"></span>
                  </>
                ) : (
                  'Ask'
                )}
              </button>
            </div>
          </form>

          {conversation.length > 0 && (
            <div className="conversation">
              <h3>Conversation History</h3>
              {conversation.map((item, index) => (
                <div key={index} className="qa-pair">
                  <div style={{
                    marginBottom: '0.5rem',
                    fontWeight: '700',
                    color: '#F38181'
                  }}>
                    <strong>Q:</strong> {item.question}
                  </div>
                  <div style={{
                    color: '#2c3e50',
                    lineHeight: '1.5'
                  }}>
                    <strong>A:</strong> {item.answer}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <footer className="footer">
        Made with &lt;3 by <a href="https://x.com/as1fansar1" target="_blank" rel="noopener noreferrer">Asif</a>
      </footer>
    </div>
  )
}

export default App
