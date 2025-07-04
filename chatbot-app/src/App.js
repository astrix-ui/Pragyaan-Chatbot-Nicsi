import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { text: "Hi! How can I help you today?", sender: "bot" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isMiniChatOpen, setIsMiniChatOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null); // ✅ NEW
  const resizingRef = useRef(null); // ✅ NEW

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ Refocus input after loading finishes
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    await saveQueryToBackend(input);

    const userMessage = { text: input, sender: "user" };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: input,
          chat_history: messages.filter(m => m.sender !== "bot").map(m => m.text)
        })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, sender: "bot" }]);
    } catch (error) {
      console.error('Error calling API:', error);
      setMessages(prev => [...prev, {
        text: "Sorry, I'm having trouble connecting to the assistant.",
        sender: "bot"
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const saveQueryToBackend = async (query) => {
    try {
      await fetch('http://localhost:8000/api/save-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query })
      });
    } catch (error) {
      console.error('Error saving query:', error);
    }
  };

  // const handleFileUpload = async (e) => {
  //   const file = e.target.files[0];
  //   if (!file) return;

  //   const formData = new FormData();
  //   formData.append("file", file);

  //   try {
  //     const response = await fetch("http://localhost:8000/api/upload-pdf", {
  //       method: "POST",
  //       body: formData,
  //     });

  //     const result = await response.json();
  //     if (response.ok) {
  //       alert("✅ PDF uploaded and company data updated!");
  //     } else {
  //       alert("❌ Error: " + result.detail);
  //     }
  //   } catch (error) {
  //     console.error("Upload error:", error);
  //     alert("❌ Failed to upload PDF");
  //   }
  // };

  const toggleMiniChat = () => {
    setIsMiniChatOpen(!isMiniChatOpen);
  };

  // ✅ Resize Logic
  const handleResizeMouseDown = (e) => {
    const container = e.target.closest('.mini-chat-container');
    if (!container) return;

    resizingRef.current = container;

    const startX = e.clientX;
    const startWidth = container.offsetWidth;

    const handleMouseMove = (moveEvent) => {
      const dx = startX - moveEvent.clientX;
      const newWidth = Math.max(280, startWidth + dx);
      container.style.width = `${newWidth}px`;
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      resizingRef.current = null;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <>
      {/* UPLOAD FILES BTN */}
      {/* <div className="pdf-upload">
        <label>
          Upload PDF:&nbsp;
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileUpload}
          />
        </label>
      </div> */}

      {!isMiniChatOpen && (
        <div className="chatbot-container">
          {/* Optional full-size chat UI */}
        </div>
      )}

      <button className="floating-chat-button" onClick={toggleMiniChat}>
        {isMiniChatOpen ? '✕' : '💬'}
      </button>

      {isMiniChatOpen && (
        <div className="mini-chat-container">
          <div className="mini-chat-header">
            <h3>Pragyaan AI Assistant</h3>
            <button onClick={toggleMiniChat} className="close-mini-chat">✕</button>
          </div>

          <div className="mini-chat-window">
            {messages.map((msg, index) => (
              <div key={index} className={`mini-chat-message ${msg.sender}`}>
                <div className="mini-message-content">
                  {msg.text.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}<br />
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="mini-chat-message bot">
                <div className="mini-message-content typing-indicator">
                  <span className="dot">.</span>
                  <span className="dot">.</span>
                  <span className="dot">.</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="mini-chat-input">
            <textarea
              ref={inputRef} // ✅ Keeps focus
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your question..."
              disabled={isLoading}
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? <span className="spinner"></span> : 'Send'}
            </button>
          </div>

          {/* ✅ Left Resize Handle */}
          <div
            className="resize-handle-left"
            onMouseDown={handleResizeMouseDown}
          />
        </div>
      )}
    </>
  );
}

export default App;
