import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface StudentState {
  studentId: string
  wrongQuestions: WrongQuestion[]
  reviewSuggestion: ReviewSuggestion | null
  quiz: Quiz | null
}

interface WrongQuestion {
  id: number
  question_id: string
  paper_id: string
  question_content: string
  student_answer: string
  correct_answer: string
  knowledge_points: string[]
  difficulty: string
  timestamp: string
}

interface ReviewSuggestion {
  analysis: string
  weak_points: string[]
  suggestions: string[]
  resources: string[]
  study_plan: string
}

interface Quiz {
  title: string
  subject: string
  total_score: number
  questions: QuizQuestion[]
}

interface QuizQuestion {
  question_id: string
  question_type: string
  content: string
  options?: string[]
  correct_answer: string
  score: number
  knowledge_points: string[]
  difficulty: string
}

const initialState: StudentState = {
  studentId: '',
  wrongQuestions: [],
  reviewSuggestion: null,
  quiz: null,
}

const studentSlice = createSlice({
  name: 'student',
  initialState,
  reducers: {
    setStudentId: (state, action: PayloadAction<string>) => {
      state.studentId = action.payload
    },
    setWrongQuestions: (state, action: PayloadAction<WrongQuestion[]>) => {
      state.wrongQuestions = action.payload
    },
    setReviewSuggestion: (state, action: PayloadAction<ReviewSuggestion | null>) => {
      state.reviewSuggestion = action.payload
    },
    setQuiz: (state, action: PayloadAction<Quiz | null>) => {
      state.quiz = action.payload
    },
  },
})

export const { setStudentId, setWrongQuestions, setReviewSuggestion, setQuiz } = studentSlice.actions

export default studentSlice.reducer
