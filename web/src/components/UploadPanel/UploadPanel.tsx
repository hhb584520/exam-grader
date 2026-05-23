import { useState, useRef } from 'react'
import { uploadPaper } from '../../services/api'

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [paperId, setPaperId] = useState('')
  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleChooseFile = () => {
    fileInputRef.current?.click()
  }

  const handleSubmit = async () => {
    if (!file || !paperId || !title || !subject) {
      setMessage('Please fill in all fields')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const result = await uploadPaper(file, paperId, title, subject)
      setMessage(`✅ Upload successful! Paper ID: ${result.paper_id}`)
      setFile(null)
      setPaperId('')
      setTitle('')
      setSubject('')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      setMessage('❌ Upload failed, please try again')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-panel">
      <h2>📤 Upload Exam Paper</h2>
      <div className="form-group">
        <label>Paper File</label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button onClick={handleChooseFile} className="file-choose-btn">
          Choose File
        </button>
        {file && <span className="file-name">Selected: {file.name}</span>}
      </div>
      <div className="form-group">
        <label>Paper ID</label>
        <input
          type="text"
          value={paperId}
          onChange={(e) => setPaperId(e.target.value)}
          placeholder="Enter paper unique ID"
          className="text-input"
        />
      </div>
      <div className="form-group">
        <label>Paper Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter paper title"
          className="text-input"
        />
      </div>
      <div className="form-group">
        <label>Subject</label>
        <select value={subject} onChange={(e) => setSubject(e.target.value)} className="select-input">
          <option value="">Select subject</option>
          <option value="Mathematics">Mathematics</option>
          <option value="Chinese">Chinese</option>
          <option value="English">English</option>
          <option value="Physics">Physics</option>
          <option value="Chemistry">Chemistry</option>
          <option value="Biology">Biology</option>
          <option value="History">History</option>
          <option value="Geography">Geography</option>
          <option value="Politics">Politics</option>
        </select>
      </div>
      <button onClick={handleSubmit} disabled={loading} className="submit-btn">
        {loading ? 'Uploading...' : 'Upload Paper'}
      </button>
      {message && <div className="message">{message}</div>}
    </div>
  )
}