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
          <p>Intelligent Exam Grading System</p>
        </div>
        <nav className="nav">
          <button
            className={`nav-btn ${currentPage === 'upload' ? 'active' : ''}`}
            onClick={() => onPageChange('upload')}
          >
            Upload Paper
          </button>
          <button
            className={`nav-btn ${currentPage === 'grade' ? 'active' : ''}`}
            onClick={() => onPageChange('grade')}
          >
            Grade Exam
          </button>
          <button
            className={`nav-btn ${currentPage === 'step' ? 'active' : ''}`}
            onClick={() => onPageChange('step')}
          >
            Step Analysis
          </button>
          <button
            className={`nav-btn ${currentPage === 'wrong' ? 'active' : ''}`}
            onClick={() => onPageChange('wrong')}
          >
            Wrong Questions
          </button>
          <button
            className={`nav-btn ${currentPage === 'review' ? 'active' : ''}`}
            onClick={() => onPageChange('review')}
          >
            Review Suggestions
          </button>
          <button
            className={`nav-btn ${currentPage === 'quiz' ? 'active' : ''}`}
            onClick={() => onPageChange('quiz')}
          >
            Quiz Generator
          </button>
        </nav>
        <div className="student-input">
          <input
            type="text"
            placeholder="Student ID"
            value={studentId}
            onChange={handleStudentIdChange}
            className="student-id-input"
          />
        </div>
      </div>
    </header>
  )
}