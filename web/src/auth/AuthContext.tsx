import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { api } from '@/api/client'

interface AuthContextType {
	token: string | null
	username: string | null
	login: (username: string, token: string) => void
	logout: () => void
}

const AuthContext = createContext<AuthContextType>({ token: null, username: null, login: () => {}, logout: () => {} })

export function AuthProvider({ children }: { children: React.ReactNode }) {
	const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
	// Helper to check JWT expiry
	function isTokenExpired(token: string | null): boolean {
		if (!token) return true;
		try {
			const payload = JSON.parse(atob(token.split('.')[1]));
			if (!payload.exp) return false;
			return Date.now() >= payload.exp * 1000;
		} catch {
			return true;
		}
	}

	// On mount, check if token is expired and clear if so
	useEffect(() => {
		if (token && isTokenExpired(token)) {
			setToken(null);
			setUsername(null);
			// Only redirect if token was present and expired
			window.location.href = '/dashboard';
		}
	}, [token]);
	const [username, setUsername] = useState<string | null>(() => localStorage.getItem('username'))


	useEffect(() => {
		if (token) {
			localStorage.setItem('token', token)
			axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
			api.defaults.headers.common['Authorization'] = `Bearer ${token}`
		} else {
			localStorage.removeItem('token')
			delete axios.defaults.headers.common['Authorization']
			delete api.defaults.headers.common['Authorization']
		}
	}, [token])
	useEffect(() => {
		if (username) localStorage.setItem('username', username)
		else localStorage.removeItem('username')
	}, [username])

	useEffect(() => {
		axios.interceptors.response.use(
			resp => resp,
			err => {
				if (err?.response?.status === 401) {
					setToken(null)
					setUsername(null)
				}
				return Promise.reject(err)
			}
		)
	}, [])

	const value = useMemo(() => ({
		token,
		username,
		login: (uname: string, t: string) => {
			setUsername(uname);
			setToken(t);
			window.location.href = '/upload';
		},
		logout: () => {
			setUsername(null);
			setToken(null);
			window.location.href = '/dashboard';
		}
	}), [token, username])
	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() { return useContext(AuthContext) }
