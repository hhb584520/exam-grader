import { useState } from 'react'
import { getReviewSuggestion, ReviewSuggestion } from '../../services/api'

export default function ReviewSuggestionPanel() {
  const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '')
  const [suggestion, setSuggestion] = useState<ReviewSuggestion | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchSuggestion = async () => {
    if (!studentId) {
      setMessage('请先输入学生ID')
      return
    }

    setLoading(true)
    setMessage('')
    setSuggestion(null)

    try {
      const result = await getReviewSuggestion(studentId)
      setSuggestion(result)
    } catch (error) {
      setMessage('❌ 获取复习建议失败，请重试')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="review-panel">
      <h2>🎯 复习建议</h2>
      <div className="form-row">
        <div className="form-group">
          <label>学生ID</label>
          <input
            type="text"
            value={studentId}
            onChange={(e) => {
              setStudentId(e.target.value)
              localStorage.setItem('studentId', e.target.value)
            }}
            placeholder="请输入学生ID"
            className="text-input"
          />
        </div>
        <button onClick={fetchSuggestion} disabled={loading} className="submit-btn">
          {loading ? '分析中...' : '获取建议'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {suggestion && (
        <div className="suggestion-content">
          <div className="section">
            <h3>📊 知识点分析</h3>
            <p>{suggestion.analysis}</p>
          </div>

          <div className="section">
            <h3>⚠️ 薄弱知识点</h3>
            <div className="weak-points">
              {suggestion.weak_points.map((point, index) => (
                <span key={index} className="weak-point">{point}</span>
              ))}
            </div>
          </div>

          <div className="section">
            <h3>💡 复习建议</h3>
            <ul className="suggestion-list">
              {suggestion.suggestions.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h3>📖 推荐资源</h3>
            <ul className="resource-list">
              {suggestion.resources.map((resource, index) => (
                <li key={index}>{resource}</li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h3>📅 学习计划</h3>
            <p>{suggestion.study_plan}</p>
          </div>
        </div>
      )}
    </div>
  )
}
