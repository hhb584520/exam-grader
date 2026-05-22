import { useState } from 'react'

interface HeaderProps {
  currentPage: string
  onPageChange: (page: string) => void
}

export default function Header({ currentPage, onPageChange }: HeaderProps) {
  const [studentId, setStudentId] = useState('')

  const handleStudentIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStudentId(e.target.value)
    localStorage.setItem('studentId', e.target.value)
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <h1>📝 ExamGrader</h1>
          <p>智能试卷批改系统</p>
        </div>
        <nav className="nav">
          <button
            className={`nav-btn ${currentPage === 'upload' ? 'active' : ''}`}
            onClick={() => onPageChange('upload')}
          >
            上传试卷
          </button>
          <button
            className={`nav-btn ${currentPage === 'grade' ? 'active' : ''}`}
            onClick={() => onPageChange('grade')}
          >
            试卷批改
          </button>
          <button
            className={`nav-btn ${currentPage === 'step' ? 'active' : ''}`}
            onClick={() => onPageChange('step')}
          >
            步骤分析
          </button>
          <button
            className={`nav-btn ${currentPage === 'wrong' ? 'active' : ''}`}
            onClick={() => onPageChange('wrong')}
          >
            错题本
          </button>
          <button
            className={`nav-btn ${currentPage === 'review' ? 'active' : ''}`}
            onClick={() => onPageChange('review')}
          >
            复习建议
          </button>
          <button
            className={`nav-btn ${currentPage === 'quiz' ? 'active' : ''}`}
            onClick={() => onPageChange('quiz')}
          >
            检查卷
          </button>
        </nav>
        <div className="student-input">
          <input
            type="text"
            placeholder="学生ID"
            value={studentId}
            onChange={handleStudentIdChange}
            className="student-id-input"
          />
        </div>
      </div>
    </header>
  )
}
