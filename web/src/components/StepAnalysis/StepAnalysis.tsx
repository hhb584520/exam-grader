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
    question_type: '解答题',
    knowledge_points: ['导数计算', '极值判断', '解方程'],
    student_steps: [
      { step_number: 1, content: '对f(x)求导得f\'(x) = 3x² - 6x', is_correct: true },
      { step_number: 2, content: '令f\'(x) = 0，即 3x² - 6x = 0', is_correct: true },
      { step_number: 3, content: '解得 x = 0', is_correct: false },
      { step_number: 4, content: '所以x=0是极值点', is_correct: false },
    ],
    error_step_index: 2,
    error_step_content: '解得 x = 0',
    error_reason: '解方程时只找到一个解x=0，遗漏了x=2；没有使用二阶导数判断极值类型',
    error_type: '步骤遗漏',
    correct_steps: [
      '对f(x)求导：f\'(x) = 3x² - 6x = 3x(x-2)',
      '令f\'(x) = 0，解方程 3x(x-2) = 0',
      '解得 x = 0 或 x = 2',
      '求二阶导数：f\'\'(x) = 6x - 6',
      '判断极值：f\'\'(0) = -6 < 0，x=0是极大值点；f\'\'(2) = 6 > 0，x=2是极小值点',
    ],
    correct_method: '导数求极值法',
    common_mistakes: [
      { mistake: '解方程遗漏解', reason: '学生常因因式分解不彻底或计算粗心导致漏解' },
      { mistake: '忽略二阶导数判断', reason: '部分学生直接根据一阶导数为零判断极值' },
      { mistake: '计算错误', reason: '导数计算或解方程过程中的算术错误' },
    ],
    teaching_suggestions: '在讲解导数求极值时，强调每一步的必要性；展示常见错误案例；设计专门训练解方程完整性的练习题；在作业评分中重视解题步骤的完整性。',
    learning_tips: '养成按步骤解题的习惯，不要跳步；解方程后检查是否有遗漏的解；复习导数求极值的完整步骤；将同类错误整理到错题本，定期回顾。',
    related_resources: ['《导数应用专题训练》', '一元二次方程因式分解复习讲义', '二阶导数判断极值微课视频'],
  }

  const handleAnalysis = async () => {
    if (!questionContent || !studentAnswer) {
      alert('请输入题目内容和学生解答')
      return
    }

    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setResult(mockAnalysis)
    setLoading(false)
  }

  return (
    <div className="step-analysis-panel">
      <h2>🔍 步骤级错误分析</h2>
      <div className="form-group">
        <label>题目内容</label>
        <textarea
          value={questionContent}
          onChange={(e) => setQuestionContent(e.target.value)}
          placeholder="请输入题目内容"
          className="textarea-input"
        />
      </div>
      <div className="form-group">
        <label>学生解答</label>
        <textarea
          value={studentAnswer}
          onChange={(e) => setStudentAnswer(e.target.value)}
          placeholder="请输入学生的解答过程（按步骤分行）"
          className="textarea-input"
        />
      </div>
      <button onClick={handleAnalysis} disabled={loading} className="submit-btn">
        {loading ? '分析中...' : '分析步骤'}
      </button>

      {result && (
        <div className="analysis-result">
          <div className="tab-container">
            <button
              className={`tab-btn ${activeTab === 'student-steps' ? 'active' : ''}`}
              onClick={() => setActiveTab('student-steps')}
            >
              学生解题步骤
            </button>
            <button
              className={`tab-btn ${activeTab === 'correct-steps' ? 'active' : ''}`}
              onClick={() => setActiveTab('correct-steps')}
            >
              RAG正确步骤
            </button>
            <button
              className={`tab-btn ${activeTab === 'error-analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('error-analysis')}
            >
              错误分析
            </button>
            <button
              className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''}`}
              onClick={() => setActiveTab('suggestions')}
            >
              教学建议
            </button>
          </div>

          <div className={`tab-content ${activeTab === 'student-steps' ? 'active' : ''}`}>
            <h3>📝 学生解题步骤分析</h3>
            <div className="steps-list">
              {result.student_steps.map((step, index) => (
                <div key={index} className={`step-item ${step.is_correct ? 'correct' : 'wrong'}`}>
                  <span className="step-number">步骤{step.step_number}</span>
                  <span className="step-content">{step.content}</span>
                  <span className="step-status">{step.is_correct ? '✓' : '✗'}</span>
                  {!step.is_correct && (
                    <span className="error-tag">{result.error_type}</span>
                  )}
                </div>
              ))}
            </div>
            <div className="knowledge-summary">
              <h4>涉及知识点</h4>
              {result.knowledge_points.map((point, index) => (
                <span key={index} className="tag">{point}</span>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'correct-steps' ? 'active' : ''}`}>
            <h3>📚 RAG知识库 - 正确解题方法</h3>
            <div className="method-info">
              <strong>🔧 正确解题方法：</strong>{result.correct_method}
            </div>
            <div className="steps-list expected">
              {result.correct_steps.map((step, index) => (
                <div key={index} className="step-item">
                  <span className="step-number">步骤{index + 1}</span>
                  <span className="step-content">{step}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'error-analysis' ? 'active' : ''}`}>
            <h3>🔍 错误深度分析</h3>
            <div className="error-summary">
              <div className="error-item">
                <span className="label">错误类型：</span>
                <span className="value error">{result.error_type}</span>
              </div>
              <div className="error-item">
                <span className="label">错误位置：</span>
                <span className="value">第{result.error_step_index + 1}步</span>
              </div>
              <div className="error-item">
                <span className="label">错误原因：</span>
                <span className="value">{result.error_reason}</span>
              </div>
            </div>
            <div className="common-mistakes">
              <h4>📊 常见错误参考（来自RAG知识库）</h4>
              {result.common_mistakes.map((item, index) => (
                <div key={index} className="mistake-item">
                  <strong>{index + 1}. {item.mistake}</strong>
                  <p>{item.reason}</p>
                </div>
              ))}
            </div>
          </div>

          <div className={`tab-content ${activeTab === 'suggestions' ? 'active' : ''}`}>
            <h3>🎯 教学与学习建议</h3>
            <div className="teaching-card">
              <h4>👨‍🏫 教师教学建议</h4>
              <p>{result.teaching_suggestions}</p>
            </div>
            <div className="learning-card">
              <h4>📖 学生学习建议</h4>
              <p>{result.learning_tips}</p>
            </div>
            <div className="resources-card">
              <h4>📚 推荐学习资源</h4>
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
