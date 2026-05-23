import { useState, useEffect } from 'react'
import { getWrongQuestions, WrongQuestion } from '../../services/api'

export default function WrongQuestions() {
  const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '')
  const [wrongQuestions, setWrongQuestions] = useState<WrongQuestion[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchWrongQuestions = async () => {
    if (!studentId) {
      setMessage('Please enter student ID first')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const questions = await getWrongQuestions(studentId)
      setWrongQuestions(questions)
      if (questions.length === 0) {
        setMessage('🎉 No wrong questions yet, keep up the good work!')
      }
    } catch (error) {
      setMessage('❌ Failed to get wrong questions, please try again')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (studentId) {
      fetchWrongQuestions()
    }
  }, [studentId])

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'difficulty-easy'
      case 'Medium': return 'difficulty-medium'
      case 'Hard': return 'difficulty-hard'
      default: return 'difficulty-medium'
    }
  }

  return (
    <div className="wrong-questions-panel">
      <h2>📚 Wrong Questions Collection</h2>
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
        <button onClick={fetchWrongQuestions} disabled={loading} className="submit-btn">
          {loading ? 'Loading...' : 'Query Wrong Questions'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {wrongQuestions.length > 0 && (
        <div className="questions-list">
          <p className="count-info">Total {wrongQuestions.length} wrong questions</p>
          {wrongQuestions.map((question) => (
            <div key={question.id} className="question-card">
              <div className="question-meta">
                <span className={`difficulty ${getDifficultyColor(question.difficulty)}`}>
                  {question.difficulty}
                </span>
                <span className="timestamp">{new Date(question.timestamp).toLocaleString()}</span>
              </div>
              <div className="question-body">
                <p className="question-content">{question.question_content}</p>
                <div className="answer-comparison">
                  <div className="answer-item wrong">
                    <span className="label">Your Answer</span>
                    <span className="value">{question.student_answer}</span>
                  </div>
                  <div className="answer-item correct">
                    <span className="label">Correct Answer</span>
                    <span className="value">{question.correct_answer}</span>
                  </div>
                </div>
                <div className="knowledge-tags">
                  {question.knowledge_points.map((point, index) => (
                    <span key={index} className="tag">{point}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}