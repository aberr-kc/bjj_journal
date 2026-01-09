import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [user, setUser] = useState(null);
  const [entries, setEntries] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setUser({ token });
      loadEntries(token);
      loadQuestions();
    }
  }, []);

  const loadEntries = async (token) => {
    try {
      const response = await axios.get(`${API_BASE}/entries/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEntries(response.data);
    } catch (error) {
      console.error('Failed to load entries:', error);
    }
  };

  const loadQuestions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/questions/`);
      setQuestions(response.data);
    } catch (error) {
      console.error('Failed to load questions:', error);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        username, password
      });
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      setUser({ token });
      loadEntries(token);
      loadQuestions();
    } catch (error) {
      alert('Login failed');
    }
  };

  const register = async (username, password) => {
    try {
      await axios.post(`${API_BASE}/auth/register`, {
        username, password
      });
      alert('Registration successful! Please login.');
    } catch (error) {
      alert('Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setEntries([]);
  };

  if (!user) {
    return <LoginForm onLogin={login} onRegister={register} />;
  }

  return (
    <div className="app">
      <header>
        <h1>BJJ Training Journal</h1>
        <button onClick={logout}>Logout</button>
      </header>
      
      <main>
        <div className="actions">
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'New Entry'}
          </button>
        </div>

        {showForm && (
          <EntryForm 
            questions={questions} 
            onSubmit={(entry) => {
              // Create entry logic here
              setShowForm(false);
              loadEntries(user.token);
            }}
            token={user.token}
          />
        )}

        <div className="entries">
          <h2>Training Entries</h2>
          {entries.map(entry => (
            <EntryCard key={entry.id} entry={entry} />
          ))}
        </div>
      </main>
    </div>
  );
}

function LoginForm({ onLogin, onRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isRegister) {
      onRegister(username, password);
    } else {
      onLogin(username, password);
    }
  };

  return (
    <div className="login-form">
      <h1>BJJ Training Journal</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">
          {isRegister ? 'Register' : 'Login'}
        </button>
        <button type="button" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Switch to Login' : 'Switch to Register'}
        </button>
      </form>
    </div>
  );
}

function EntryForm({ questions, onSubmit, token }) {
  const [sessionType, setSessionType] = useState('gi');
  const [responses, setResponses] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const entryData = {
      date: new Date().toISOString(),
      session_type: sessionType,
      responses: Object.entries(responses).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        answer: answer
      }))
    };

    try {
      await axios.post(`${API_BASE}/entries/`, entryData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      onSubmit();
    } catch (error) {
      alert('Failed to create entry');
    }
  };

  return (
    <form className="entry-form" onSubmit={handleSubmit}>
      <h3>New Training Entry</h3>
      
      <label>
        Session Type:
        <select value={sessionType} onChange={(e) => setSessionType(e.target.value)}>
          <option value="gi">Gi</option>
          <option value="no-gi">No-Gi</option>
          <option value="drilling">Drilling</option>
          <option value="sparring">Sparring</option>
          <option value="competition">Competition</option>
        </select>
      </label>

      {questions.map(question => (
        <label key={question.id}>
          {question.question_text}:
          {question.question_type === 'rating' ? (
            <select 
              onChange={(e) => setResponses({...responses, [question.id]: e.target.value})}
            >
              <option value="">Select rating</option>
              {[1,2,3,4,5,6,7,8,9,10].map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          ) : question.question_type === 'number' ? (
            <input
              type="number"
              onChange={(e) => setResponses({...responses, [question.id]: e.target.value})}
            />
          ) : (
            <textarea
              onChange={(e) => setResponses({...responses, [question.id]: e.target.value})}
            />
          )}
        </label>
      ))}

      <button type="submit">Save Entry</button>
    </form>
  );
}

function EntryCard({ entry }) {
  return (
    <div className="entry-card">
      <h4>{entry.session_type} - {new Date(entry.date).toLocaleDateString()}</h4>
      <div className="responses">
        {entry.responses.map(response => (
          <p key={response.id}>
            <strong>{response.question.question_text}:</strong> {response.answer}
          </p>
        ))}
      </div>
    </div>
  );
}

export default App;