import { useRef } from "react";

const ChatForm = ({ setChatHistory, chatHistory, clientInfo, setIsTyping }) => {
    const inputRef = useRef();

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        const userMessage = inputRef.current.value.trim();
        if (!userMessage) return;
        inputRef.current.value = "";

        setChatHistory(prev => [...prev, { role: "user", text: userMessage }]);
        setIsTyping(true);

        const historique = chatHistory.map(msg => ({
            role: msg.role === "user" ? "user" : "assistant",
            content: msg.text
        }));

        const response = await fetch("https://cca-chatbot.onrender.com/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                message: userMessage,
                historique,
                client: clientInfo
            }),
        });

        const data = await response.json();
        setIsTyping(false);
        setChatHistory(prev => [...prev, { role: "model", text: data.reponse }]);
    };

    return (
        <form action="#" className="chat-form" onSubmit={handleFormSubmit}>
            <button type="button" className="material-symbols-rounded attach-btn">
                attach_file
            </button>
            <input
                ref={inputRef}
                type="text"
                placeholder="Écrivez votre message..."
                className="message-input"
                required
            />
            <button type="submit" className="send-btn material-symbols-rounded">
                send
            </button>
        </form>
    );
};

export default ChatForm;