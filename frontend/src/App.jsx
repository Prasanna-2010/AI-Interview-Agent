import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import { sendInterviewMessage } from "./api/interviewApi";

function App() {
  // App States: 'START', 'ACTIVE', 'FEEDBACK'
  const [view, setView] = useState("START");
  
  // Session Data
  const [sessionId, setSessionId] = useState("");
  const [candidateId, setCandidateId] = useState("");
  
  // Interview Data
  const [history, setHistory] = useState([]);
  const [feedback, setFeedback] = useState(null);
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Input State
  const [answerText, setAnswerText] = useState("");

  const chatEndRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [history]);

  const handleStartInterview = async (e) => {
    e.preventDefault();
    if (!sessionId.trim() || !candidateId.trim()) return;

    setLoading(true);
    setError(null);
    setHistory([]);

    try {
      const data = await sendInterviewMessage(sessionId, candidateId, null);
      setHistory([{ role: "interviewer", text: data.reply }]);
      setView("ACTIVE");
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answerText.trim() || loading) return;
    const currentAnswer = answerText;

    // Optimistically add user answer to UI
    setHistory((prev) => [...prev, { role: "candidate", text: currentAnswer }]);
    setAnswerText("");
    setLoading(true);
    setError(null);

    try {
      const data = await sendInterviewMessage(sessionId, candidateId, currentAnswer);
      
      if (data.done) {
        setFeedback(data.feedback);
        setView("FEEDBACK");
      } else {
        setHistory((prev) => [...prev, { role: "interviewer", text: data.reply }]);
      }
    } catch (err) {
      setError("Something went wrong while evaluating your answer. Please try again.");
      // Restore user text so they don't lose it
      setAnswerText(currentAnswer);
      // Remove the optimistic candidate message
      setHistory((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setView("START");
    setSessionId("");
    setCandidateId("");
    setHistory([]);
    setFeedback(null);
    setError(null);
  };

  return (
    <div className="app-container">
      {/* GLOBAL HEADER */}
      <header className="header">
        <h1>AI Interview Agent</h1>
        {view === "ACTIVE" && (
          <div className="header-status">
            <span><span className="status-dot"></span> Interview in Progress</span>
            <span style={{ color: "var(--border)" }}>|</span>
            <span>Session: {sessionId}</span>
          </div>
        )}
      </header>

      <main className="main-content">
        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        {/* VIEW 1: START SCREEN */}
        {view === "START" && (
          <div className="start-screen card">
            <h2>Start Your Interview</h2>
            <p>Personalized technical interviews powered by AI</p>
            
            <form onSubmit={handleStartInterview}>
              <div className="input-group">
                <label htmlFor="sessionId">Session ID</label>
                <input
                  id="sessionId"
                  type="text"
                  placeholder="e.g. interview-001"
                  value={sessionId}
                  onChange={(e) => setSessionId(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
              <div className="input-group">
                <label htmlFor="candidateId">Candidate ID</label>
                <input
                  id="candidateId"
                  type="text"
                  placeholder="e.g. CAND-010"
                  value={candidateId}
                  onChange={(e) => setCandidateId(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
              <button type="submit" className="btn-primary" disabled={loading || !sessionId || !candidateId}>
                {loading ? "Preparing your interview..." : "Start Interview"}
              </button>
              <span className="note">Your responses will be evaluated dynamically throughout the interview.</span>
            </form>
          </div>
        )}

        {/* VIEW 2: ACTIVE INTERVIEW */}
        {view === "ACTIVE" && (
          <div className="interview-grid">
            {/* LEFT SIDEBAR */}
            <aside className="sidebar">
              <div className="sidebar-section">
                <div className="sidebar-label">Candidate</div>
                <div className="sidebar-value">{candidateId}</div>
              </div>
              <div className="sidebar-section">
                <div className="sidebar-label">Interview Type</div>
                <div className="sidebar-value">Technical Interview</div>
              </div>
              <div className="sidebar-section">
                <div className="sidebar-label">Status</div>
                <div className="sidebar-value" style={{ color: "var(--primary)" }}>In Progress</div>
              </div>
            </aside>

            {/* RIGHT CHAT AREA */}
            <div className="chat-container">
              <div className="chat-history">
                {history.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role === "interviewer" ? "msg-interviewer" : "msg-candidate"}`}>
                    <div className="msg-header">
                      {msg.role === "interviewer" ? "🤖 INTERVIEWER" : "👤 YOU"}
                    </div>
                    <div className="msg-content">{msg.text}</div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              <div className="input-area">
                <label htmlFor="answerInput">Your Answer</label>
                <div className="textarea-wrapper">
                  <textarea
                    id="answerInput"
                    placeholder="Explain your approach clearly. You can include technical details, examples, trade-offs, and implementation considerations."
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    maxLength={5000}
                    disabled={loading}
                  />
                  <span className="char-count">{answerText.length} / 5000</span>
                </div>
                <div className="input-actions">
                  <button 
                    className="btn-primary" 
                    onClick={handleSubmitAnswer}
                    disabled={loading || answerText.trim().length === 0}
                  >
                    {loading ? "Evaluating Answer..." : "Submit Answer"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 3: FINAL FEEDBACK */}
        {view === "FEEDBACK" && feedback && (
          <div className="feedback-screen">
            <div className="feedback-header">
              <h2>Interview Completed</h2>
              <p style={{ color: "var(--text-muted)" }}>Here's your personalized interview assessment.</p>
            </div>

            <div className="card">
              <div className="feedback-section">
                <h3>Overall Assessment</h3>
                <p>{feedback.summary}</p>
              </div>

              <div className="feedback-section">
                <h3>Strengths</h3>
                <ul>
                  {feedback.strengths?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  )) || <li>No strengths recorded.</li>}
                </ul>
              </div>

              <div className="feedback-section">
                <h3>Areas for Improvement</h3>
                <ul>
                  {feedback.gaps?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  )) || <li>No gaps recorded.</li>}
                </ul>
              </div>

              <div className="feedback-section" style={{ marginBottom: 0, borderBottom: "none" }}>
                <h3 style={{ borderBottom: "none" }}>Recommended Next Steps</h3>
                <ul>
                  {feedback.next?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  )) || <li>No next steps recorded.</li>}
                </ul>
              </div>
            </div>

            <div className="action-bar">
              <button className="btn-primary" onClick={handleReset}>
                Start New Interview
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;