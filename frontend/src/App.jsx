import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import { sendInterviewMessage } from "./api/interviewAPI";

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

  // --- Derived display-only values (no functional / API impact) ---
  const questionNumber = history.filter((m) => m.role === "interviewer").length;
  const candidateInitial = (candidateId || "?").trim().charAt(0).toUpperCase();

  return (
    <div className="app-container">
      {/* AMBIENT BACKGROUND */}
      <div className="ambient-bg" aria-hidden="true">
        <div className="ambient-glow ambient-glow-1"></div>
        <div className="ambient-glow ambient-glow-2"></div>
      </div>

      {/* GLOBAL HEADER */}
      <header className="header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="9" fill="url(#brandGradient)" />
              <path d="M10 20.5 L16 9.5 L22 20.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M12.4 16.5 H19.6" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="16" cy="9.5" r="1.4" fill="white" />
              <defs>
                <linearGradient id="brandGradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#6366f1" />
                  <stop offset="1" stopColor="#4338ca" />
                </linearGradient>
              </defs>
            </svg>
          </span>
          <span className="brand-name">AI Interview Agent</span>
        </div>

        {view === "ACTIVE" && (
          <div className="header-status">
            <span className="live-pill">
              <span className="status-dot"></span> Interview in Progress
            </span>
            <span className="header-divider">|</span>
            <span className="session-chip">Session: <strong>{sessionId}</strong></span>
          </div>
        )}
      </header>

      <main className="main-content">
        {error && (
          <div className="error-banner" role="alert">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* VIEW 1: START SCREEN */}
        {view === "START" && (
          <div className="start-screen">
            {/* HERO */}
            <section className="hero">
              <div className="hero-copy">
                <span className="eyebrow">AI-Powered Technical Interviews</span>
                <h1>AI Interview Agent</h1>
                <p className="hero-subtitle">
                  Practice smarter. Interview better. Get actionable AI-powered feedback.
                </p>
                <ul className="hero-chips">
                  <li>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    Adaptive questioning
                  </li>
                  <li>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    Real-time evaluation
                  </li>
                  <li>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    Personalized feedback
                  </li>
                </ul>
              </div>

              <div className="hero-visual" aria-hidden="true">
                <svg viewBox="0 0 320 320" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="160" cy="160" r="130" fill="url(#ringGradient)" opacity="0.12" />
                  <circle cx="160" cy="160" r="98" stroke="url(#ringGradient)" strokeWidth="1.5" opacity="0.4" />
                  <circle cx="160" cy="160" r="66" fill="url(#coreGradient)" />
                  <g className="orbit-node orbit-node-1">
                    <circle cx="160" cy="34" r="9" fill="#8b5cf6" />
                  </g>
                  <g className="orbit-node orbit-node-2">
                    <circle cx="286" cy="160" r="7" fill="#6366f1" />
                  </g>
                  <g className="orbit-node orbit-node-3">
                    <circle cx="70" cy="252" r="6" fill="#a78bfa" />
                  </g>
                  <path d="M136 168 L152 184 L188 138" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                  <defs>
                    <linearGradient id="ringGradient" x1="30" y1="30" x2="290" y2="290" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#6366f1" />
                      <stop offset="1" stopColor="#1e1b4b" />
                    </linearGradient>
                    <linearGradient id="coreGradient" x1="94" y1="94" x2="226" y2="226" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#4f46e5" />
                      <stop offset="1" stopColor="#1e1b4b" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </section>

            {/* SETUP CARD */}
            <section className="card setup-card">
              <div className="setup-card-header">
                <h2>Start Your Interview</h2>
                <p>Set up your session to begin a personalized technical interview.</p>
              </div>

              <form onSubmit={handleStartInterview}>
                <div className="form-section">
                  <div className="form-section-label">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M20 21a8 8 0 1 0-16 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.8" /></svg>
                    Interview Configuration
                  </div>

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
                    
                  </div>
              

                <button type="submit" className="btn-primary btn-start" disabled={loading || !sessionId || !candidateId}>
                  {loading ? (
                    <>
                      <span className="spinner" aria-hidden="true"></span>
                      Preparing your interview...
                    </>
                  ) : (
                    <>
                      Start Interview
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </>
                  )}
                </button>
                <span className="note">Your responses will be evaluated dynamically throughout the interview.</span>
              </form>
            </section>
          </div>
        )}

        {/* VIEW 2: ACTIVE INTERVIEW */}
        {view === "ACTIVE" && (
          <div className="interview-grid">
            {/* LEFT SIDEBAR */}
            <aside className="sidebar">
              <div className="candidate-card">
                <div className="candidate-avatar">{candidateInitial}</div>
                <div>
                  <div className="sidebar-label">Candidate</div>
                  <div className="sidebar-value">{candidateId}</div>
                </div>
              </div>

              <div className="sidebar-section">
                <div className="sidebar-label">Interview Type</div>
                <div className="sidebar-value">Technical Interview</div>
              </div>
              <div className="sidebar-section">
                <div className="sidebar-label">Status</div>
                <div className="sidebar-value status-value">
                  <span className="status-dot"></span> In Progress
                </div>
              </div>

              <div className="sidebar-section sidebar-progress">
                <div className="sidebar-label">Progress</div>
                <div className="sidebar-value">Question {questionNumber}</div>
                <div className="progress-track">
                  <div className={`progress-fill ${loading ? "progress-fill-active" : ""}`}></div>
                </div>
              </div>
            </aside>

            {/* RIGHT CHAT AREA */}
            <div className="chat-container">
              <div className="chat-header">
                <span className="ai-avatar" aria-hidden="true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2 4 6v6c0 5 3.4 8.4 8 10 4.6-1.6 8-5 8-10V6l-8-4Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" /><path d="M9.5 12l1.8 1.8L15 10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
                </span>
                AI Interviewer
              </div>

              <div className="chat-history">
                {history.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role === "interviewer" ? "msg-interviewer" : "msg-candidate"}`}>
                    <div className="msg-header">
                      {msg.role === "interviewer" ? (
                        <>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M12 2 4 6v6c0 5 3.4 8.4 8 10 4.6-1.6 8-5 8-10V6l-8-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></svg>
                          AI INTERVIEWER
                        </>
                      ) : (
                        <>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.8" /><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>
                          YOU
                        </>
                      )}
                    </div>
                    <div className="msg-content">{msg.text}</div>
                  </div>
                ))}
                {loading && history.length > 0 && (
                  <div className="message msg-interviewer msg-typing">
                    <div className="msg-header">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M12 2 4 6v6c0 5 3.4 8.4 8 10 4.6-1.6 8-5 8-10V6l-8-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></svg>
                      AI INTERVIEWER
                    </div>
                    <div className="typing-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
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
                    {loading ? (
                      <>
                        <span className="spinner" aria-hidden="true"></span>
                        Evaluating Answer...
                      </>
                    ) : (
                      <>
                        Submit Answer
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                      </>
                    )}
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
              <div className="feedback-badge">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M9 12.75 11.25 15 15 9.75M12 21a8.96 8.96 0 0 0 6.36-2.64A8.96 8.96 0 0 0 21 12a8.96 8.96 0 0 0-2.64-6.36A8.96 8.96 0 0 0 12 3a8.96 8.96 0 0 0-6.36 2.64A8.96 8.96 0 0 0 3 12a8.96 8.96 0 0 0 2.64 6.36A8.96 8.96 0 0 0 12 21Z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </div>
              <h2>Interview Completed</h2>
              <p>Here's your personalized AI-powered interview assessment.</p>
            </div>

            <div className="card summary-card">
              <div className="feedback-section summary-section">
                <h3>Overall Assessment</h3>
                <p>{feedback.summary}</p>
              </div>
            </div>

            <div className="feedback-columns">
              <div className="card feedback-col">
                <div className="feedback-section">
                  <h3 className="section-title-strength">
                    <span className="section-icon icon-strength">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </span>
                    Strengths
                  </h3>
                  <ul className="feedback-list">
                    {feedback.strengths?.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    )) || <li>No strengths recorded.</li>}
                  </ul>
                </div>
              </div>

              <div className="card feedback-col">
                <div className="feedback-section">
                  <h3 className="section-title-gap">
                    <span className="section-icon icon-gap">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </span>
                    Areas for Improvement
                  </h3>
                  <ul className="feedback-list">
                    {feedback.gaps?.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    )) || <li>No gaps recorded.</li>}
                  </ul>
                </div>
              </div>
            </div>

            <div className="card next-steps-card">
              <div className="feedback-section" style={{ marginBottom: 0 }}>
                <h3 className="section-title-next">
                  <span className="section-icon icon-next">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  </span>
                  Recommended Next Steps
                </h3>
                <ul className="feedback-list">
                  {feedback.next?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  )) || <li>No next steps recorded.</li>}
                </ul>
              </div>
            </div>

            <div className="action-bar">
              <button className="btn-primary btn-restart" onClick={handleReset}>
                Start New Interview
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        AI Interview Agent — Adaptive technical interviews, evaluated in real time.
      </footer>
    </div>
  );
}

export default App;
