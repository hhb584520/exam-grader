import { useState } from 'react'
import { getReviewSuggestion, ReviewSuggestion } from '../../services/api'

export default function ReviewSuggestionPanel() {
  const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '')
  const [suggestion, setSuggestion] = useState<ReviewSuggestion | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchSuggestion = async () => {
    if (!studentId) {
      setMessage('Please enter student ID first')
      return
    }

    setLoading(true)
    setMessage('')
    setSuggestion(null)

    try {
      const result = await getReviewSuggestion(studentId)
      setSuggestion(result)
    } catch (error) {
      setMessage('❌ Failed to get review suggestions, please try again')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="review-panel">
      <h2>🎯 Review Suggestions</h2>
      <div className="form-row">
        <div className="form-group">
          <label>Student ID</label>
          <input
            type="text"
            value={studentId}
            onChange={(e) => {
              setStudentId(e.target.value)
              localStorage.setItem('studentId', e.target.value)
            }}
            placeholder="Enter student ID"
            className="text-input"
          />
        </div>
        <button onClick={fetchSuggestion} disabled={loading} className="submit-btn">
          {loading ? 'Analyzing...' : 'Get Suggestions'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {suggestion && (
        <div className="suggestion-content">
          <div className="section">
            <h3>📊 Knowledge Points Analysis</h3>
            <p>{suggestion.analysis}</p>
          </div>

          <div className="section">
            <h3>⚠️ Weak Knowledge Points</h3>
            <div className="weak-points">
              {suggestion.weak_points.map((point, index) => (
                <span key={index} className="weak-point">{point}</span>
              ))}
            </div>
          </div>

          <div className="section">
            <h3>💡 Review Suggestions</h3>
            <ul className="suggestion-list">
              {suggestion.suggestions.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h3>📖 Recommended Resources</h3>
            <ul className="resource-list">
              {suggestion.resources.map((resource, index) => (
                <li key={index}>{resource}</li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h3>📅 Study Plan</h3>
            <p>{suggestion.study_plan}</p>
          </div>
        </div>
      )}
    </div>
  )
}