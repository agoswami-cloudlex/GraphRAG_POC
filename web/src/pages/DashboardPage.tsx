import { useAuth } from '@/auth/AuthContext'

export default function DashboardPage() {
  const { username } = useAuth()
  return (
    <div className="card" style={{ maxWidth: 700, margin: '40px auto', padding: '32px 24px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: 8 }}>🚀 Welcome to <span style={{ color: '#4f8cff' }}>GraphRAG</span></h1>
      <p style={{ textAlign: 'center', fontSize: '1.15em', color: '#555', marginBottom: 32 }}>
        Your AI-powered platform for document management, knowledge graph exploration, and smart queries.
      </p>
      <div style={{ display: 'flex', gap: 24, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 32 }}>
        <div className="feature-card" style={{ background: '#f6f8fa', borderRadius: 12, padding: 24, minWidth: 180, textAlign: 'center', boxShadow: '0 2px 8px #0001' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Upload Documents</div>
          <div style={{ fontSize: 14, color: '#666' }}>Easily add files to your cases and build your knowledge base.</div>
        </div>
        <div className="feature-card" style={{ background: '#f6f8fa', borderRadius: 12, padding: 24, minWidth: 180, textAlign: 'center', boxShadow: '0 2px 8px #0001' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🔎</div>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Query Knowledge Graph</div>
          <div style={{ fontSize: 14, color: '#666' }}>Ask questions and get instant, AI-powered answers from your data.</div>
        </div>
        <div className="feature-card" style={{ background: '#f6f8fa', borderRadius: 12, padding: 24, minWidth: 180, textAlign: 'center', boxShadow: '0 2px 8px #0001' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🔐</div>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Secure & Private</div>
          <div style={{ fontSize: 14, color: '#666' }}>Your data is protected with secure authentication and privacy controls.</div>
        </div>
      </div>
      {!username ? (
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a href="/login" className="button" style={{ marginRight: 12, fontSize: 16, padding: '10px 28px' }}>Login</a>
          <a href="/login" className="button secondary" style={{ fontSize: 16, padding: '10px 28px' }}>Sign Up</a>
          <div style={{ marginTop: 18, color: '#888', fontSize: 15 }}>
            <span>New here? Create an account to get started!</span>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', marginTop: 32, fontSize: 18 }}>
          👋 Hello, <b>{username}</b>! You are logged in.<br />
          <span style={{ color: '#4f8cff' }}>Explore your cases, upload documents, and start querying!</span>
        </div>
      )}
    </div>
  )
}
