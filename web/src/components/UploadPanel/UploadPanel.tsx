import { useState } from 'react'
import { uploadPaper } from '../../services/api'

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [paperId, setPaperId] = useState('')
  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleSubmit = async () => {
    if (!file || !paperId || !title || !subject) {
      setMessage('请填写所有字段')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const result = await uploadPaper(file, paperId, title, subject)
      setMessage(`✅ 上传成功！试卷ID: ${result.paper_id}`)
      setFile(null)
      setPaperId('')
      setTitle('')
      setSubject('')
    } catch (error) {
      setMessage('❌ 上传失败，请重试')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-panel">
      <h2>📤 上传试卷</h2>
      <div className="form-group">
        <label>试卷文件</label>
        <input
          type="file"
          accept=".txt,.md,.pdf"
          onChange={handleFileChange}
          className="file-input"
        />
        {file && <span className="file-name">已选择: {file.name}</span>}
      </div>
      <div className="form-group">
        <label>试卷ID</label>
        <input
          type="text"
          value={paperId}
          onChange={(e) => setPaperId(e.target.value)}
          placeholder="请输入试卷唯一标识"
          className="text-input"
        />
      </div>
      <div className="form-group">
        <label>试卷标题</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="请输入试卷标题"
          className="text-input"
        />
      </div>
      <div className="form-group">
        <label>科目</label>
        <select value={subject} onChange={(e) => setSubject(e.target.value)} className="select-input">
          <option value="">请选择科目</option>
          <option value="数学">数学</option>
          <option value="语文">语文</option>
          <option value="英语">英语</option>
          <option value="物理">物理</option>
          <option value="化学">化学</option>
          <option value="生物">生物</option>
          <option value="历史">历史</option>
          <option value="地理">地理</option>
          <option value="政治">政治</option>
        </select>
      </div>
      <button onClick={handleSubmit} disabled={loading} className="submit-btn">
        {loading ? '上传中...' : '上传试卷'}
      </button>
      {message && <div className="message">{message}</div>}
    </div>
  )
}
