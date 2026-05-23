import { useState } from 'react';
import { gradeExam } from '../../services/api';
interface QuestionResult {
 question_id: string;
 question_type: string;
 student_answer: string;
 correct_answer: string;
 score: number;
 max_score: number;
 is_correct: boolean;
 error_reason: string;
 knowledge_points: string[];
 difficulty: string;
}
export default function GradePanel() {
 const [paperId, setPaperId] = useState('');
 const [studentId, setStudentId] = useState(() => localStorage.getItem('studentId') || '');
 const [answers, setAnswers] = useState('');
 const [loading, setLoading] = useState(false);
 const [result, setResult] = useState<{
 score: number;
 total_score: number;
 results: QuestionResult[];
 } | null>(null);
 const [message, setMessage] = useState('');
 const handleSubmit = async () => {
 if (!paperId || !studentId || !answers) {
 setMessage('Please fill in all fields');
 return;
 }
 setLoading(true);
 setMessage('');
 setResult(null);
 try {
 const gradingResult = await gradeExam(paperId, studentId, answers);
 setResult(gradingResult);
 setMessage(`✅ Grading completed! Score: ${gradingResult.score}/${gradingResult.total_score}`);
 }
 catch (error) {
 setMessage('❌ Grading failed, please try again');
 console.error(error);
 }
 finally {
 setLoading(false);
 }
 };
 return (<div className="grade-panel">
 <h2>✏️ Grade Exam</h2>
 <div className="form-group">
 <label>Paper ID</label>
 <input type="text" value={paperId} onChange={(e) => setPaperId(e.target.value)} placeholder="Enter paper ID to grade" className="text-input"/>
 </div>
 <div className="form-group">
 <label>Student ID</label>
 <input type="text" value={studentId} onChange={(e) => {
 setStudentId(e.target.value);
 localStorage.setItem('studentId', e.target.value);
 }} placeholder="Enter student ID" className="text-input"/>
 </div>
 <div className="form-group">
 <label>Student Answers (JSON format)</label>
 <textarea value={answers} onChange={(e) => setAnswers(e.target.value)} placeholder='{"question_1": "answer1", "question_2": "answer2", ...}' className="textarea-input" rows={6}/>
 </div>
 <button onClick={handleSubmit} disabled={loading} className="submit-btn">
 {loading ? 'Grading...' : 'Start Grading'}
 </button>
 {message && <div className="message">{message}</div>}

 {result && (<div className="result-panel">
 <div className="score-summary">
 <div className="score-circle">
 <span className="score-value">{result.score}</span>
 <span className="score-total">/ {result.total_score}</span>
 </div>
 <div className="score-info">
 <p className="score-label">Total Score</p>
 <p className="score-percentage">
 {((result.score / result.total_score) * 100).toFixed(1)}%
 </p>
 </div>
 </div>
 <h3>Grading Details</h3>
 <div className="question-results">
 {result.results.map((question, index) => (<div key={index} className={`question-result ${question.is_correct ? 'correct' : 'wrong'}`}>
 <div className="question-header">
 <span className="question-type">{question.question_type}</span>
 <span className="question-score">
 {question.score}/{question.max_score}
 </span>
 <span className={`question-status ${question.is_correct ? 'correct' : 'wrong'}`}>
 {question.is_correct ? '✓ Correct' : '✗ Wrong'}
 </span>
 </div>
 <div className="question-content">
 <p><strong>Question ID:</strong> {question.question_id}</p>
 <p><strong>Student Answer:</strong> {question.student_answer}</p>
 <p><strong>Correct Answer:</strong> {question.correct_answer}</p>
 {!question.is_correct && (<>
 <p><strong>Error Reason:</strong> {question.error_reason}</p>
 <p><strong>Knowledge Points:</strong> {question.knowledge_points.join(', ')}</p>
 <p><strong>Difficulty:</strong> {question.difficulty}</p>
 </>)}
 </div>
 </div>))}
 </div>
 </div>)}
 </div>);
}