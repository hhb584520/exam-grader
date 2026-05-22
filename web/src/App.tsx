import { useState } from 'react'
import Header from './components/Header/Header'
import UploadPanel from './components/UploadPanel/UploadPanel'
import GradePanel from './components/GradePanel/GradePanel'
import WrongQuestions from './components/WrongQuestions/WrongQuestions'
import ReviewSuggestionPanel from './components/ReviewSuggestion/ReviewSuggestion'
import QuizGenerator from './components/QuizGenerator/QuizGenerator'
import StepAnalysis from './components/StepAnalysis/StepAnalysis'

export default function App() {
  const [currentPage, setCurrentPage] = useState('upload')

  const renderPage = () => {
    switch (currentPage) {
      case 'upload':
        return <UploadPanel />
      case 'grade':
        return <GradePanel />
      case 'step':
        return <StepAnalysis />
      case 'wrong':
        return <WrongQuestions />
      case 'review':
        return <ReviewSuggestionPanel />
      case 'quiz':
        return <QuizGenerator />
      default:
        return <UploadPanel />
    }
  }

  return (
    <div className="app">
      <Header currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="main-content">
        {renderPage()}
      </main>
      <footer className="footer">
        <p>ExamGrader - 智能试卷批改系统 | Powered by OPEA</p>
      </footer>
    </div>
  )
}
