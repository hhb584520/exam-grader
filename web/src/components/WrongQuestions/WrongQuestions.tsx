import { useState, useEffect } from 'react'
import { getWrongQuestions, WrongQuestion } from '../../services/api'

export default function WrongQuestions() {
  const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '')
  const [wrongQuestions, setWrongQuestions] = useState<WrongQuestion[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchWrongQuestions = async () => {
    if (!studentId) {
      setMessage('请先输入学生ID')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const questions = await getWrongQuestions(studentId)
      setWrongQuestions(questions)
      if (questions.length === 0) {
        setMessage('🎉 暂无错题，继续保持！')
      }
    } catch (error) {
      setMessage('❌ 获取错题失败，请重试')
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
      case '简单': return 'difficulty-easy'
      case '中等': return 'difficulty-medium'
      case '困难': return 'difficulty-hard'
      default: return 'difficulty-medium'
    }
  }

  return (
    <div className="wrong-questions-panel">
      <h2>📚 错题本</h2>
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
        <button onClick={fetchWrongQuestions} disabled={loading} className="submit-btn">
          {loading ? '加载中...' : '查询错题'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {wrongQuestions.length > 0 && (
        <div className="questions-list">
          <p className="count-info">共 {wrongQuestions.length} 道错题</p>
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
                    <span className="label">你的答案</span>
                    <span className="value">{question.student_answer}</span>
                  </div>
                  <div className="answer-item correct">
                    <span className="label">正确答案</span>
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
