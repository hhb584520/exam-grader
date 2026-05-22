import { useState } from 'react'
import { generateQuiz, Quiz } from '../../services/api'

export default function QuizGenerator() {
  const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '')
  const [questionCount, setQuestionCount] = useState(10)
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleGenerate = async () => {
    if (!studentId) {
      setMessage('请先输入学生ID')
      return
    }

    setLoading(true)
    setMessage('')
    setQuiz(null)

    try {
      const result = await generateQuiz(studentId, questionCount)
      setQuiz(result)
    } catch (error) {
      setMessage('❌ 生成检查卷失败，请重试')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const getQuestionTypeName = (type: string) => {
    switch (type) {
      case 'choice': return '选择题'
      case 'fill': return '填空题'
      case 'short': return '简答题'
      case 'essay': return '问答题'
      default: return type
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '简单': return 'difficulty-easy'
      case '中等': return 'difficulty-medium'
      case '困难': return 'difficulty-hard'
      default: return 'difficulty-medium'
    }
  }

  return (
    <div className="quiz-panel">
      <h2>📝 生成检查卷</h2>
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
        <div className="form-group">
          <label>题目数量</label>
          <input
            type="number"
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
            min={1}
            max={50}
            className="text-input"
          />
        </div>
        <button onClick={handleGenerate} disabled={loading} className="submit-btn">
          {loading ? '生成中...' : '生成检查卷'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {quiz && (
        <div className="quiz-content">
          <div className="quiz-header">
            <h3>{quiz.title}</h3>
            <p className="quiz-meta">
              <span>科目: {quiz.subject}</span>
              <span>总分: {quiz.total_score}分</span>
              <span>题目数: {quiz.questions.length}道</span>
            </p>
          </div>

          <div className="questions-container">
            {quiz.questions.map((question, index) => (
              <div key={index} className="question-item">
                <div className="question-header">
                  <span className="question-number">{index + 1}.</span>
                  <span className="question-type">{getQuestionTypeName(question.question_type)}</span>
                  <span className={`difficulty ${getDifficultyColor(question.difficulty)}`}>
                    {question.difficulty}
                  </span>
                  <span className="question-score">{question.score}分</span>
                </div>
                <p className="question-text">{question.content}</p>
                {question.options && (
                  <div className="options-list">
                    {question.options.map((option, optIndex) => (
                      <span key={optIndex} className="option">
                        {String.fromCharCode(65 + optIndex)}. {option}
                      </span>
                    ))}
                  </div>
                )}
                <div className="knowledge-tags">
                  {question.knowledge_points.map((point, pIndex) => (
                    <span key={pIndex} className="tag">{point}</span>
                  ))}
                </div>
                <div className="answer-section">
                  <strong>参考答案:</strong> {question.correct_answer}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
