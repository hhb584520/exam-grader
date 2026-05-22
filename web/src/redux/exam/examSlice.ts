import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ExamState {
  papers: Paper[]
  currentPaper: Paper | null
  gradingResult: GradingResult | null
  isGrading: boolean
}

interface Paper {
  paper_id: string
  title: string
  subject: string
  content: string
  created_at: string
}

interface GradingResult {
  score: number
  total_score: number
  results: QuestionResult[]
}

interface QuestionResult {
  question_id: string
  question_type: string
  student_answer: string
  correct_answer: string
  score: number
  max_score: number
  is_correct: boolean
  error_reason: string
  knowledge_points: string[]
  difficulty: string
}

const initialState: ExamState = {
  papers: [],
  currentPaper: null,
  gradingResult: null,
  isGrading: false,
}

const examSlice = createSlice({
  name: 'exam',
  initialState,
  reducers: {
    setPapers: (state, action: PayloadAction<Paper[]>) => {
      state.papers = action.payload
    },
    setCurrentPaper: (state, action: PayloadAction<Paper | null>) => {
      state.currentPaper = action.payload
    },
    setGradingResult: (state, action: PayloadAction<GradingResult | null>) => {
      state.gradingResult = action.payload
    },
    setIsGrading: (state, action: PayloadAction<boolean>) => {
      state.isGrading = action.payload
    },
  },
})

export const { setPapers, setCurrentPaper, setGradingResult, setIsGrading } = examSlice.actions

export default examSlice.reducer
