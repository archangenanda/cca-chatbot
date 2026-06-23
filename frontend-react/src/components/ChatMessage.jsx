import ChatbotIcon from "./ChatbotIcon";

const ChatMessage = ({ message }) => {
    const isBot = message.role === "model";
    const time = new Date().toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit"
    });

    return (
        <div className={`message ${isBot ? "bot-message" : "user-message"}`}>
            {isBot && <ChatbotIcon />}
            <div className="message-content">
                <p className="message-text">{message.text}</p>
                <span className="message-time">
                    {time}
                    {!isBot && <span className="material-symbols-rounded check-icon">done_all</span>}
                </span>
            </div>
        </div>
    );
};

export default ChatMessage;
