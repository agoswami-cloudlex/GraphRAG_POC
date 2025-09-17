import { Routes, Route, Navigate, Link } from 'react-router-dom'
import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import QueryPage from './pages/QueryPage'
import DashboardPage from './pages/DashboardPage'
import { AuthProvider, useAuth } from './auth/AuthContext'
import './theme.css'

function Protected({ children }: { children: JSX.Element }) {
	const { token, username, logout } = useAuth()
	if (!token || !username) {
		logout()
		return <Navigate to="/login" replace />
	}
	return children
}

function Header() {
	const { username, logout } = useAuth()
	const [dark, setDark] = useState(false)
	function toggleTheme() {
		setDark(d => {
			if (!d) document.body.classList.add('dark')
			else document.body.classList.remove('dark')
			return !d
		})
	}
	return (
		<header className="header">
			<div className="brand"><Link to="/dashboard">GraphRAG</Link></div>
			<nav>
				<Link to="/dashboard">Dashboard</Link>
				<Link to="/upload">Upload</Link>
				<Link to="/query">Query</Link>
			</nav>
			<div className="user">
				<button className="button" style={{marginRight:8}} onClick={toggleTheme}>{dark ? 'Light' : 'Dark'} Mode</button>
				{username && <><span>{username}</span><button onClick={logout}>Logout</button></>}
			</div>
		</header>
	)
}

export default function App() {
	return (
		<AuthProvider>
			<div className="app">
				<Header />
				<main className="main">
					<Routes>
						<Route path="/login" element={<LoginPage />} />
						<Route path="/dashboard" element={<DashboardPage />} />
						<Route path="/upload" element={<Protected><UploadPage /></Protected>} />
						<Route path="/query" element={<Protected><QueryPage /></Protected>} />
						<Route path="/" element={<Navigate to="/dashboard" replace />} />
					</Routes>
				</main>
			</div>
		</AuthProvider>
	)
}
