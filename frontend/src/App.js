import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import axios from 'axios'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [isSignUp, setIsSignUp] = useState(false)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleSignUp = async (e) => {
    e.preventDefault()
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) alert(error.message)
    else alert('Check your email for confirmation!')
  }

  const handleSignIn = async (e) => {
    e.preventDefault()
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) alert(error.message)
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setResult('')
    setPrompt('')
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt')
      return
    }

    setLoading(true)
    setResult('')
    
    try {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token

      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/generate`,
        { prompt },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      setResult(response.data.result)
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message))
    }
    
    setLoading(false)
  }

  if (!user) {
    return (
      <div className="App">
        <h1>🤖 AI SaaS</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px' }}>
          {isSignUp ? 'Create your account' : 'Sign in to continue'}
        </p>
        
        <form onSubmit={isSignUp ? handleSignUp : handleSignIn}>
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password (min 6 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">
            {isSignUp ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <div className="auth-toggle">
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}
          {' '}
          <button onClick={() => setIsSignUp(!isSignUp)}>
            {isSignUp ? 'Sign In' : 'Sign Up'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="App">
      <h1>🤖 AI Content Generator</h1>
      
      <div className="user-info">
        <p>Logged in as: <strong>{user.email}</strong></p>
        <button className="sign-out-button" onClick={handleSignOut}>
          Sign Out
        </button>
      </div>

      <div className="generator-section">
        <h2>Generate AI Content</h2>
        <textarea
          placeholder="Enter your prompt here... (e.g., 'Write a short story about a robot learning to paint')"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button 
          className="primary-button"
          onClick={handleGenerate} 
          disabled={loading}
        >
          {loading ? '✨ Generating...' : '✨ Generate'}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <p>AI is thinking...</p>
        </div>
      )}

      {result && (
        <div className="result-container">
          <h3>✅ Generated Result:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  )
}

export default App