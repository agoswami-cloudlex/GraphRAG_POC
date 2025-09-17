import { useEffect, useState } from 'react'
import { api } from '@/api/client'

interface Case { id: string; name: string }

export default function UploadPage() {
const [cases, setCases] = useState<Case[]>([])
const [caseId, setCaseId] = useState('')
const [files, setFiles] = useState<FileList | null>(null)
const [result, setResult] = useState<string[] | null>(null)
const [error, setError] = useState<string | null>(null)
// Removed document selection state

useEffect(() => {
	(async () => {
		const { data } = await api.get('/cases');
		setCases(data.cases || [])
	})()
}, [])

useEffect(() => {
	// Removed document fetching effect
	}, [caseId])

async function upload() {
	setError(null)
	setResult(null)
	if (!caseId) return setError('Select a case or enter new case name')
	if (!files || files.length === 0) return setError('Select files')
	const form = new FormData()
	form.append('case_id', caseId)
	Array.from(files).forEach(f => form.append('files', f))
	try {
		const { data } = await api.post('/documents/upload', form)
		setResult(data.document_ids)
	} catch (e: any) {
		setError(e?.response?.data?.detail || 'Failed')
	}
}

   return (
	   <div className="upload-container">
		   <div className="upload-card">
			   <h3>Upload documents</h3>
			   <div className="grid">
				   <select className="select" value={caseId} onChange={e => setCaseId(e.target.value)}>
					   <option value="">Select case</option>
					   {cases.map(c => <option value={c.id} key={c.id}>{c.name} ({c.id})</option>)}
				   </select>
				   {/* Removed select document field */}
				   <input className="input" type="file" multiple accept=".pdf,.docx,.txt" onChange={e => setFiles(e.target.files)} />
				   <button className="button" onClick={upload}>Upload</button>
				   {error && <div className="muted">{error}</div>}
				   {result && <div>Uploaded: {result.join(', ')}</div>}
			   </div>
		   </div>
	   </div>
   )
}
