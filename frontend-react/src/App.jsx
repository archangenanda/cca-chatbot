import { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import ChatForm from './components/ChatForm';
import ChatMessage from './components/ChatMessage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// ── Page Chatbot ───────────────────────────────────────────────
const Chatbot = () => {
  const [chatHistory, setChatHistory] = useState([
    { role: "model", text: "Bonjour ! 👋\nComment puis-je vous aider aujourd'hui ?" }
  ]);

  const navigate = useNavigate();

  const handleQuickAction = (text) => {
    setChatHistory(prev => [...prev, { role: "user", text }]);
  };

  return (
    <div className="container">
      <div className="chatbot-popup">

        {/* Header */}
        <div className="chatbot-header">
          <div className="header-info">
            <div className="cca-logo">
              <span className="logo-cca">CCA</span>
              <span className="logo-bank">BANK</span>
            </div>
            <div className="header-text">
              <h2 className="logo-text">CCA Assistance</h2>
              <span className="status-online">
                <span className="status-dot"></span>
                En ligne
              </span>
            </div>
          </div>
          <button
            className="material-symbols-rounded header-menu"
            onClick={() => navigate("/admin")}
          >
            more_vert
          </button>
        </div>

        {/* Body */}
        <div className="chat-body">
          {chatHistory.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </div>

        {/* Boutons rapides */}
        <div className="quick-actions">
          <button onClick={() => handleQuickAction("Je veux ouvrir un compte")}>
            <span className="material-symbols-rounded">person_add</span>
            Ouvrir un compte
          </button>
          <button onClick={() => handleQuickAction("Je veux prendre un rendez-vous")}>
            <span className="material-symbols-rounded">calendar_month</span>
            Prendre RDV
          </button>
          <button onClick={() => handleQuickAction("Où sont vos agences ?")}>
            <span className="material-symbols-rounded">location_on</span>
            Nos agences
          </button>
          <button onClick={() => handleQuickAction("Je veux vous contacter")}>
            <span className="material-symbols-rounded">headset_mic</span>
            Nous contacter
          </button>
        </div>

        {/* Footer */}
        <div className="chat-footer">
          <ChatForm setChatHistory={setChatHistory} />
          <p className="security-text">
            <span className="material-symbols-rounded">security</span>
            Vos données sont sécurisées
          </p>
        </div>

      </div>
    </div>
  );
};

// ── App principale avec les routes ────────────────────────────
const App = () => {
  const navigate = useNavigate();

  return (
    <Routes>
      <Route path="/" element={<Chatbot />} />
      <Route path="/admin" element={
        localStorage.getItem("token")
          ? <Dashboard onLogout={() => {
              localStorage.removeItem("token");
              navigate("/");
            }} />
          : <Login onLogin={() => navigate("/admin")} />
      } />
    </Routes>
  );
};

export default App;