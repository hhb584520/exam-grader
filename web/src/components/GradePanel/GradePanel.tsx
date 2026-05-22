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
 setMessage('请填写所有字段');
 return;
 }
 setLoading(true);
 setMessage('');
 setResult(null);
 try {
 const gradingResult = await gradeExam(paperId, studentId, answers);
 setResult(gradingResult);
 setMessage(`✅ 批改完成！得分: ${gradingResult.score}/${gradingResult.total_score}`);
 }
 catch (error) {
 setMessage('❌ 批改失败，请重试');
 console.error(error);
 }
 finally {
 setLoading(false);
 }
 };
 return (<div className="grade-panel">
 <h2>✏️ 试卷批改</h2>
 <div className="form-group">
 <label>试卷ID</label>
 <input type="text" value={paperId} onChange={(e) => setPaperId(e.target.value)} placeholder="请输入要批改的试卷ID" className="text-input"/>
 </div>
 <div className="form-group">
 <label>学生ID</label>
 <input type="text" value={studentId} onChange={(e) => {
 setStudentId(e.target.value);
 localStorage.setItem('studentId', e.target.value);
 }} placeholder="请输入学生ID" className="text-input"/>
 </div>
 <div className="form-group">
 <label>学生答案（JSON格式）</label>
 <textarea value={answers} onChange={(e) => setAnswers(e.target.value)} placeholder='{"question_1": "答案1", "question_2": "答案2", ...}' className="textarea-input" rows={6}/>
 </div>
 <button onClick={handleSubmit} disabled={loading} className="submit-btn">
 {loading ? '批改中...' : '开始批改'}
 </button>
 {message && <div className="message">{message}</div>}

 {result && (<div className="result-panel">
 <div className="score-summary">
 <div className="score-circle">
 <span className="score-value">{result.score}</span>
 <span className="score-total">/ {result.total_score}</span>
 </div>
 <div className="score-info">
 <p className="score-label">总得分</p>
 <p className="score-percentage">
 {((result.score / result.total_score) * 100).toFixed(1)}%
 </p>
 </div>
 </div>
 <h3>批改详情</h3>
 <div className="question-results">
 {result.results.map((question, index) => (<div key={index} className={`question-result ${question.is_correct ? 'correct' : 'wrong'}`}>
 <div className="question-header">
 <span className="question-type">{question.question_type}</span>
 <span className="question-score">
 {question.score}/{question.max_score}
 </span>
 <span className={`question-status ${question.is_correct ? 'correct' : 'wrong'}`}>
 {question.is_correct ? '✓ 正确' : '✗ 错误'}
 </span>
 </div>
 <div className="question-content">
 <p><strong>题目ID:</strong> {question.question_id}</p>
 <p><strong>学生答案:</strong> {question.student_answer}</p>
 <p><strong>正确答案:</strong> {question.correct_answer}</p>
 {!question.is_correct && (<>
 <p><strong>错误原因:</strong> {question.error_reason}</p>
 <p><strong>知识点:</strong> {question.knowledge_points.join(', ')}</p>
 <p><strong>难度:</strong> {question.difficulty}</p>
 </>)}
 </div>
 </div>))}
 </div>
 </div>)}
 </div>);
}
