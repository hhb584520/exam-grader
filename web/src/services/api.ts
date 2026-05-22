import axios from 'axios'

const API_BASE_URL = '/api'

export interface Paper {
  paper_id: string
  title: string
  subject: string
  content: string
  created_at: string
}

export interface GradingResult {
  score: number
  total_score: number
  results: QuestionResult[]
}

export interface QuestionResult {
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

export interface WrongQuestion {
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

export interface ReviewSuggestion {
  analysis: string
  weak_points: string[]
  suggestions: string[]
  resources: string[]
  study_plan: string
}

export interface Quiz {
  title: string
  subject: string
  total_score: number
  questions: QuizQuestion[]
}

export interface QuizQuestion {
  question_id: string
  question_type: string
  content: string
  options?: string[]
  correct_answer: string
  score: number
  knowledge_points: string[]
  difficulty: string
}

export async function uploadPaper(
  file: File,
  paperId: string,
  title: string,
  subject: string
): Promise<{ status: number; message: string; paper_id: string }> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('paper_id', paperId)
  formData.append('title', title)
  formData.append('subject', subject)

  const response = await axios.post(`${API_BASE_URL}/upload_paper`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function uploadAnswers(
  paperId: string,
  studentId: string,
  answers: string
): Promise<{ status: number; message: string }> {
  const formData = new FormData()
  formData.append('paper_id', paperId)
  formData.append('student_id', studentId)
  formData.append('answers', answers)

  const response = await axios.post(`${API_BASE_URL}/upload_answers`, formData)
  return response.data
}

export async function gradeExam(
  paperId: string,
  studentId: string,
  answers: string
): Promise<GradingResult> {
  const response = await axios.post(`${API_BASE_URL}/grade`, {
    paper_id: paperId,
    student_id: studentId,
    answers: answers,
  })
  return response.data
}

export async function getWrongQuestions(studentId: string): Promise<WrongQuestion[]> {
  const formData = new FormData()
  formData.append('student_id', studentId)

  const response = await axios.post(`${API_BASE_URL}/wrong_questions`, formData)
  return response.data.data
}

export async function getReviewSuggestion(studentId: string): Promise<ReviewSuggestion> {
  const formData = new FormData()
  formData.append('student_id', studentId)

  const response = await axios.post(`${API_BASE_URL}/review_suggestion`, formData)
  return response.data
}

export async function generateQuiz(
  studentId: string,
  questionCount: number
): Promise<Quiz> {
  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('question_count', questionCount.toString())

  const response = await axios.post(`${API_BASE_URL}/generate_quiz`, formData)
  return response.data
}
