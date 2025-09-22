import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { api } from '@/api/client';

interface Case { id: string; name: string }
interface RetrievedChunk { text: string; score: number; metadata: Record<string, any> }
interface GraphPath { nodes: string[]; relationships: string[] }

export default function QueryPage() {
	const [cases, setCases] = useState<Case[]>([])
	const [caseId, setCaseId] = useState<string>('')
	const [documents, setDocuments] = useState<{id: string, filename: string}[]>([])
	const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([])
	const [showDocModal, setShowDocModal] = useState(false)
	const [question, setQuestion] = useState('')
	const [k, setK] = useState(5)
	const [answer, setAnswer] = useState('')
	const [chunks, setChunks] = useState<RetrievedChunk[]>([])
	const [paths, setPaths] = useState<GraphPath[]>([])
	const [refs, setRefs] = useState<string[]>([])
	const [error, setError] = useState<string | null>(null)
	const [deleteStatus, setDeleteStatus] = useState<string | null>(null)

	useEffect(() => {
		(async () => {
			const { data } = await api.get('/cases');
			setCases(data.cases || [])
		})()
	}, [])

	useEffect(() => {
		if (!caseId) {
			setDocuments([])
			setSelectedDocumentIds([])
			return
		}
		(async () => {
			try {
				const { data } = await api.get(`/documents/case/${caseId}`)
				setDocuments(data)
			} catch {
				setDocuments([])
			}
		})()
	}, [caseId])

	async function ask() {
		setError(null)
		setAnswer('')
		setChunks([])
		setPaths([])
		setRefs([])
		try {
			const payload: any = { user_id: '', question, k }
			if (caseId) payload.case_id = caseId
			if (selectedDocumentIds.length > 0) payload.document_ids = selectedDocumentIds
			const { data } = await api.post('/query', payload)
			setAnswer(data.answer)
			setChunks(data.chunks || [])
			setPaths(data.graph_paths || [])
			setRefs(data.references || [])
		} catch (e) {
			setError('Failed to get answer.')
		}
	}

	async function deleteHistory() {
		if (!window.confirm('Are you sure you want to delete ALL history (input and output folders)? This cannot be undone.')) return;
		setDeleteStatus(null);
		try {
			await api.delete('/documents/delete_history');
			setDeleteStatus('History deleted successfully.');
		} catch (e: any) {
			setDeleteStatus('Failed to delete history.');
		}
	}

	return (
		<div className="grid">
			<div className="card">
				<h3>Ask a question</h3>
				<div className="grid">
					<label htmlFor="case-select" className="muted">Select case</label>
					<select id="case-select" className="select" value={caseId} onChange={e => setCaseId(e.target.value)}>
						<option value="">No selection</option>
						{cases.map(c => <option value={c.id} key={c.id}>{c.name} ({c.id})</option>)}
					</select>
					<label className="muted" style={{marginTop: '0.5em'}}>Select documents</label>
					<button className="button" type="button" style={{marginBottom: '0.5em'}} disabled={!caseId || documents.length === 0} onClick={() => setShowDocModal(true)}>
						{selectedDocumentIds.length > 0 ? `${selectedDocumentIds.length} selected` : 'Choose documents'}
					</button>
					{showDocModal && (
						<div style={{position: 'fixed', top:0, left:0, width:'100vw', height:'100vh', background:'rgba(0,0,0,0.3)', zIndex:1000, display:'flex', alignItems:'center', justifyContent:'center'}}>
							<div style={{background:'#fff', padding:'2em', borderRadius:'8px', minWidth:'300px'}}>
								<h4>Select documents</h4>
								<div style={{maxHeight:'300px', overflowY:'auto'}}>
									{documents.map(doc => (
										<div key={doc.id} style={{marginBottom:'0.5em', display:'flex', alignItems:'center', justifyContent:'space-between'}}>
											<div>
												<label>
													<input
														type="checkbox"
														checked={selectedDocumentIds.includes(doc.id)}
														onChange={e => {
															if (e.target.checked) {
																setSelectedDocumentIds(ids => [...ids, doc.id])
															} else {
																setSelectedDocumentIds(ids => ids.filter(id => id !== doc.id))
															}
														}}
													/>
													{' '}{doc.filename}
												</label>
											</div>
											<button
												className="button"
												type="button"
												style={{marginLeft:'1em', background:'#e74c3c', color:'#fff', padding:'0.2em 0.6em', fontSize:'0.9em'}}
												onClick={async () => {
													if (window.confirm(`Delete document '${doc.filename}'? This cannot be undone.`)) {
														try {
															await api.delete(`/documents/delete/${doc.id}`)
															setDocuments(docs => docs.filter(d => d.id !== doc.id))
															setSelectedDocumentIds(ids => ids.filter(id => id !== doc.id))
														} catch (err) {
															alert('Failed to delete document.')
														}
													}
												}}
											>Delete</button>
										</div>
									))}
								</div>
								<div style={{marginTop:'1em', textAlign:'right'}}>
									<button className="button" type="button" onClick={() => setShowDocModal(false)}>Done</button>
								</div>
							</div>
						</div>
					)}
					<label htmlFor="question-input" className="muted" style={{marginTop: '0.5em'}}>Enter your question</label>
					<input id="question-input" className="input" placeholder="Your question" value={question} onChange={e => setQuestion(e.target.value)} />
					<div className="flex" style={{flexDirection: 'column', alignItems: 'flex-start'}}>
						<label htmlFor="topk-input" className="muted" style={{marginBottom: '0.25em'}}>Top K results</label>
						<div style={{display: 'flex', gap: '0.5em'}}>
							<input id="topk-input" className="input" type="number" min={1} max={10} value={k} onChange={e => setK(parseInt(e.target.value || '5'))} />
							<button className="button" onClick={ask}>Ask</button>
						</div>
					</div>
					{error && <div className="muted">{error}</div>}
					<button className="button" style={{marginTop: '1em', background: '#e74c3c', color: '#fff'}} onClick={deleteHistory}>
						Delete All History
					</button>
					{deleteStatus && <div className="muted">{deleteStatus}</div>}
				</div>
			</div>
			<div className="card">
				<h3>Answer</h3>
				<div className="textarea" style={{ 
					whiteSpace: 'normal', 
					padding: '1rem', 
					border: '1px solid #ddd', 
					borderRadius: '4px', 
					backgroundColor: '#f9f9f9',
					lineHeight: '1.6'
				}}>
					{answer ? (
						<ReactMarkdown
							components={{
								// Custom styling for markdown elements
								h1: ({node, ...props}) => <h1 style={{fontSize: '1.5em', marginBottom: '0.5em', borderBottom: '2px solid #eee', paddingBottom: '0.3em'}} {...props} />,
								h2: ({node, ...props}) => <h2 style={{fontSize: '1.3em', marginBottom: '0.5em', marginTop: '1em'}} {...props} />,
								h3: ({node, ...props}) => <h3 style={{fontSize: '1.1em', marginBottom: '0.5em', marginTop: '0.8em'}} {...props} />,
								p: ({node, ...props}) => <p style={{marginBottom: '0.8em'}} {...props} />,
								ul: ({node, ...props}) => <ul style={{marginBottom: '0.8em', paddingLeft: '1.5em'}} {...props} />,
								ol: ({node, ...props}) => <ol style={{marginBottom: '0.8em', paddingLeft: '1.5em'}} {...props} />,
								li: ({node, ...props}) => <li style={{marginBottom: '0.3em'}} {...props} />,
								code: ({node, ...props}: any) => {
									const inline = props.inline;
									return inline ? 
										<code style={{backgroundColor: '#f1f1f1', padding: '0.2em 0.4em', borderRadius: '3px', fontSize: '0.9em'}} {...props} /> :
										<code style={{display: 'block', backgroundColor: '#f8f8f8', padding: '1em', borderRadius: '4px', border: '1px solid #e1e1e1', fontSize: '0.9em', overflow: 'auto'}} {...props} />
								},
								blockquote: ({node, ...props}) => <blockquote style={{borderLeft: '4px solid #ddd', paddingLeft: '1em', margin: '1em 0', fontStyle: 'italic', color: '#666'}} {...props} />,
								strong: ({node, ...props}) => <strong style={{fontWeight: 'bold'}} {...props} />,
								em: ({node, ...props}) => <em style={{fontStyle: 'italic'}} {...props} />
							}}
						>
							{answer}
						</ReactMarkdown>
					) : (
						<span style={{ color: '#999' }}>—</span>
					)}
				</div>
			</div>
			<div className="card">
				<h3>Sources</h3>
				<ul>
					{refs.map(r => <li key={r}>{r}</li>)}
				</ul>
				<div className="grid">
					{chunks.map((c, i) => (
						<div key={i} className="card">
							<div className="muted">{c.metadata?.filename} • score: {c.score?.toFixed?.(3)}</div>
							<div>{c.text}</div>
						</div>
					))}
				</div>
			</div>
			<div className="card">
				<h3>Graph Paths</h3>
				<ul>
					{paths.map((p, i) => <li key={i}>{p.nodes.join(' → ')}</li>)}
				</ul>
			</div>
		</div>
	)
}
