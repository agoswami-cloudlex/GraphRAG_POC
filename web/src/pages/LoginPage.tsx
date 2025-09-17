
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/api/client'
import { useAuth } from '@/auth/AuthContext'

export default function LoginPage() {
	const { login, token } = useAuth()
	const navigate = useNavigate()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [mode, setMode] = useState<'login'|'register'>('login')
	const [error, setError] = useState<string | null>(null)


	useEffect(() => {
		if (token) {
			navigate('/cases') // or your default protected route
		}
	}, [token, navigate])

	async function submit() {
		setError(null)
		try {
			const path = mode === 'login' ? '/auth/login' : '/auth/register'
			const { data } = await api.post(path, { username, password })
			login(data.username, data.access_token)
		} catch (e: any) {
			setError(e?.response?.data?.detail || 'Failed')
		}
	}

	return (
		<div className="card" style={{ maxWidth: 420, margin: '60px auto' }}>
			<h2>{mode === 'login' ? 'Login' : 'Register'}</h2>
			<form className="grid" onSubmit={e => { e.preventDefault(); submit(); }}>
				<input className="input" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
				<input className="input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
				<button className="button" type="submit">{mode === 'login' ? 'Login' : 'Create account'}</button>
				<button className="button secondary" type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
					{mode === 'login' ? 'Need an account?' : 'Have an account?'}
				</button>
				{error && <div className="muted">{error}</div>}
			</form>
		</div>
	)
}
