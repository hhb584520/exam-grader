import { useState } from 'react'

interface StepAnalysisResult {
  question_type: string
  knowledge_points: string[]
  student_steps: { step_number: number; content: string; is_correct: boolean }[]
  error_step_index: number
  error_step_content: string
  error_reason: string
  error_type: string
  correct_steps: string[]
  correct_method: string
  common_mistakes: { mistake: string; reason: string }[]
  teaching_suggestions: string
  learning_tips: string
  related_resources: string[]
}

export default function StepAnalysis() {
  const [questionContent, setQuestionContent] = useState('')
  const [studentAnswer, setStudentAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<StepAnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState('student-steps')

  const mockAnalysis: StepAnalysisResult = {
    question_type: 'Problem Solving',
    knowledge_points: ['Derivative Calculation', 'Extremum Judgment', 'Equation Solving'],
    student_steps: [
      { step_number: 1, content: 'Derive f(x) to get f\'(x) = 3x² - 6x', is_correct: true },
      { step_number: 2, content: 'Set f\'(x) = 0, i.e., 3x² - 6x = 0', is_correct: true },
      { step_number: 3, content: 'Solve to get x = 0', is_correct: false },
      { step_number: 4, content: 'So x=0 is the extreme point', is_correct: false },
    ],
    error_step_index: 2,
    error_step_content: 'Solve to get x = 0',
    error_reason: 'Only found one solution x=0 when solving the equation, missed x=2; did not use second derivative to determine extremum type',
    error_type: 'Step Omission',
    correct_steps: [
      'Derive f(x): f\'(x) = 3x² - 6x = 3x(x-2)',
      'Set f\'(x) = 0, solve 3x(x-2) = 0',
      'Solutions: x = 0 or x = 2',
      'Find second derivative: f\'\'(x) = 6x - 6',
      'Determine extremum: f\'\'(0) = -6 < 0, x=0 is local maximum; f\'\'(2) = 6 > 0, x=2 is local minimum',
    ],
    correct_method: 'Derivative Method for Extremum',
    common_mistakes: [
      { mistake: 'Missed solutions when solving equations', reason: 'Students often miss solutions due to incomplete factorization or careless calculation' },
      { mistake: 'Ignored second derivative test', reason: 'Some students directly judge extremum based on first derivative being zero' },
      { mistake: 'Calculation errors', reason: 'Arithmetic errors in derivative calculation or equation solving' },
    ],
    teaching_suggestions: 'When teaching derivative extremum finding, emphasize the necessity of each step; demonstrate common error cases; design exercises specifically for equation solving completeness; emphasize step completeness in homework grading.',
    learning_tips: 'Develop step-by-step problem-solving habits, do not skip steps; check for missed solutions after solving equations; review complete steps for derivative extremum finding; organize similar errors in wrong question collection and review regularly.',
    related_resources: ['"Derivative Applications Special Training"', 'Quadratic Equation Factorization Review Notes', 'Second Derivative Extremum Judgment Micro-video'],
  }

  const handleAnalysis = async () => {
    if (!questionContent || !studentAnswer) {
      alert('Please enter question content and student answer')
      return
    }

    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setResult(mockAnalysis)
    setLoading(false)
  }

  return (
    <div className="step-analysis-panel">
      <h2>🔍 Step-level Error Analysis</h2>
      <div className="form-group">
        <label>Question Content</label>
        <textarea
          value={questionContent}
          onChange={(e) => setQuestionContent(e.target.value)}
          placeholder="Enter question content"
          className="textarea-input"
        />
      </div>
      <div className="form-group">
        <label>Student Answer</label>
        <textarea
          value={studentAnswer}
          onChange={(e) => setStudentAnswer(e.target.value)}
          placeholder="Enter student's solution process (one step per line)"
          className="textarea-input"
        />
      </div>
      <button onClick={handleAnalysis} disabled={loading} className="submit-btn">
        {loading ? 'Analyzing...' : 'Analyze Steps'}
      </button>

      {result && (
        <div className="analysis-result">
          <div className="tab-container">
            <button
              className={`tab-btn ${activeTab === 'student-steps' ? 'active' : ''}`}
              onClick={() => setActiveTab('student-steps')}
            >
              Student's Steps
            </button>
            <button
              className={`tab-btn ${activeTab === 'correct-steps' ? 'active' : ''}`}
              onClick={() => setActiveTab('correct-steps')}
            >
              RAG Correct Steps
            </button>
            <button
              className={`tab-btn ${activeTab === 'error-analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('error-analysis')}
            >
              Error Analysis
            </button>
            <button
              className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''}`}
              onClick={() => setActiveTab('suggestions')}
            >
              Teaching Suggestions
            </button>
          </div>

          <div className={`tab-content ${activeTab === 'student-steps' ? 'active' : ''}`}>
            <h3>📝 Student's Solution Steps Analysis</h3>
            <div className="steps-list">
              {result.student_steps.map((step, index) => (
                <div key={index} className={`step-item ${step.is_correct ? 'correct' : 'wrong'}`}>
                  <span className="step-number">Step {step.step_number}</span>
                  <span className="step-content">{step.content}</span>
                  <span className="step-status">{step.is_correct ? '✓' : '✗'}</span>
                  {!step.is_correct && (
                    <span className="error-tag">{result.error_type}</span>
                  )}
                </div>
              ))}
            </div>
            <div className="knowledge-summary">
              <h4>Involved Knowledge Points</h4>
              {result.knowledge_points.map((point, index) => (
                <span key={index} className="tag">{point}</span>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'correct-steps' ? 'active' : ''}`}>
            <h3>📚 RAG Knowledge Base - Correct Solution Method</h3>
            <div className="method-info">
              <strong>🔧 Correct Method:</strong> {result.correct_method}
            </div>
            <div className="steps-list expected">
              {result.correct_steps.map((step, index) => (
                <div key={index} className="step-item">
                  <span className="step-number">Step {index + 1}</span>
                  <span className="step-content">{step}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'error-analysis' ? 'active' : ''}`}>
            <h3>🔍 Error Deep Analysis</h3>
            <div className="error-summary">
              <div className="error-item">
                <span className="label">Error Type:</span>
                <span className="value error">{result.error_type}</span>
              </div>
              <div className="error-item">
                <span className="label">Error Location:</span>
                <span className="value">Step {result.error_step_index + 1}</span>
              </div>
              <div className="error-item">
                <span className="label">Error Reason:</span>
                <span className="value">{result.error_reason}</span>
              </div>
            </div>
            <div className="common-mistakes">
              <h4>📊 Common Mistakes Reference (from RAG)</h4>
              {result.common_mistakes.map((item, index) => (
                <div key={index} className="mistake-item">
                  <strong>{index + 1}. {item.mistake}</strong>
                  <p>{item.reason}</p>
                </div>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'suggestions' ? 'active' : ''}`}>
            <h3>🎯 Teaching and Learning Suggestions</h3>
            <div className="teaching-card">
              <h4>👨‍🏫 Teacher Suggestions</h4>
              <p>{result.teaching_suggestions}</p>
            </div>
            <div className="learning-card">
              <h4>📖 Student Learning Tips</h4>
              <p>{result.learning_tips}</p>
            </div>
            <div className="resources-card">
              <h4>📚 Recommended Resources</h4>
              <ul>
                {result.related_resources.map((resource, index) => (
                  <li key={index}>{resource}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}