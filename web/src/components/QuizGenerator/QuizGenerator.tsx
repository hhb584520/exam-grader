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
      setMessage('Please enter student ID first')
      return
    }

    setLoading(true)
    setMessage('')
    setQuiz(null)

    try {
      const result = await generateQuiz(studentId, questionCount)
      setQuiz(result)
    } catch (error) {
      setMessage('❌ Failed to generate quiz, please try again')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const getQuestionTypeName = (type: string) => {
    switch (type) {
      case 'choice': return 'Multiple Choice'
      case 'fill': return 'Fill in the Blank'
      case 'short': return 'Short Answer'
      case 'essay': return 'Essay'
      default: return type
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'difficulty-easy'
      case 'Medium': return 'difficulty-medium'
      case 'Hard': return 'difficulty-hard'
      default: return 'difficulty-medium'
    }
  }

  return (
    <div className="quiz-panel">
      <h2>📝 Generate Quiz</h2>
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
        <div className="form-group">
          <label>Question Count</label>
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
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>
      {message && <div className="message">{message}</div>}

      {quiz && (
        <div className="quiz-content">
          <div className="quiz-header">
            <h3>{quiz.title}</h3>
            <p className="quiz-meta">
              <span>Subject: {quiz.subject}</span>
              <span>Total Score: {quiz.total_score} points</span>
              <span>Questions: {quiz.questions.length}</span>
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
                  <span className="question-score">{question.score} points</span>
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
                  <strong>Reference Answer:</strong> {question.correct_answer}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}