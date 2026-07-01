import { useState, useEffect, useRef } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import ChatForm from './components/ChatForm';
import ChatMessage from './components/ChatMessage';
import Welcome from './components/Welcome';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// ── Page Chatbot ───────────────────────────────────────────────
const Chatbot = () => {
  const [chatHistory, setChatHistory] = useState([]);
  const [clientInfo, setClientInfo] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const chatBodyRef = useRef(null); // ← ref pour le scroll

  const navigate = useNavigate();

  // Scroll automatique vers le bas à chaque nouveau message ou indicateur de frappe
  useEffect(() => {
    const timer = setTimeout(() => {
      if (chatBodyRef.current) {
        chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [chatHistory, isTyping]);

  // Scroll automatique vers le bas à chaque nouveau message ou indicateur de frappe
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [chatHistory, isTyping]);

  // Une fois le client identifié, affiche le message de bienvenue
  const handleWelcomeSubmit = (info) => {
    setClientInfo(info);
    setChatHistory([
      { 
        role: "model", 
        text: `Bonjour ${info.prenom} ! 👋\nComment puis-je vous aider aujourd'hui ?` 
      }
    ]);
  };

  const handleQuickAction = async (text) => {
    setChatHistory(prev => [...prev, { role: "user", text }]);
    setIsTyping(true);

    const historique = chatHistory.map(msg => ({
      role: msg.role === "user" ? "user" : "assistant",
      content: msg.text
    }));

    const response = await fetch("http://172.17.255.57:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: text, 
        historique,
        client: clientInfo
      }),
    });

    const data = await response.json();
    setIsTyping(false);
    setChatHistory(prev => [...prev, { role: "model", text: data.reponse }]);
  };

  return (
    <div className="container">
      <div className="chatbot-popup">

        {/* Formulaire de bienvenue si client non identifié */}
        {!clientInfo && <Welcome onSubmit={handleWelcomeSubmit} />}

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

        {/* Body avec ref pour le scroll */}
        <div className="chat-body" ref={chatBodyRef}>
          {chatHistory.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}

          {/* Indicateur de frappe */}
          {isTyping && (
            <div className="message bot-message">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
              </svg>
              <div className="message-content">
                <div className="message-text typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
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
          <ChatForm 
            setChatHistory={setChatHistory} 
            chatHistory={chatHistory}
            clientInfo={clientInfo}
            setIsTyping={setIsTyping}
          />
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