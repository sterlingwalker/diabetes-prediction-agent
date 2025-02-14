import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import styled from "styled-components";

const ChatContainer = styled.div`
  max-width: 900px;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 500px;
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const MessageBubble = styled.div`
  display: inline-block;
  max-width: 70%;
  margin-bottom: 10px;
  text-align: left;
  padding: 10px 15px;
  border-radius: 20px;
  word-wrap: break-word;
  align-self: ${(props) => (props.isUser ? "flex-end" : "flex-start")};
  background: ${(props) => (props.isUser ? "#0084ff" : "#e5e5ea")};
  color: ${(props) => (props.isUser ? "#fff" : "#000")};
`;

const InputContainer = styled.div`
  padding: 10px;
  display: flex;
  border-top: 1px solid #ccc;
`;

const InputField = styled.input`
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 20px;
  margin-right: 10px;
  outline: none;
  font-size: 1rem;
`;

const SendButton = styled.button`
  padding: 10px 20px;
  border: none;
  background: #0084ff;
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
  &:hover {
    background: #0070e0;
  }
  &:disabled {
    background: #a0cfff;
    cursor: not-allowed;
  }
`;

function ChatComponent({
  patientData = {},
  recommendations = {},
  predictedRisk = "",
  riskProbability = "",
}) {
  const [history, setHistory] = useState([
    {
      role: "assistant",
      content:
        "Hi there! Feel free to ask me any questions about your diagnosis!",
    },
  ]);
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const updatedHistory = [...history, { role: "user", content: userInput }];
    setHistory(updatedHistory);
    setLoading(true);

    try {
      const response = await axios.post(
        "https://diabetes-prediction-agent.onrender.com/chat",
        {
          history: updatedHistory,
          user_input: userInput,
          patient_data: patientData,
          recommendations: recommendations,
          predicted_risk: predictedRisk,
          risk_probability: riskProbability,
        },
      );

      setHistory(response.data.updated_history);
    } catch (error) {
      console.error("Error sending chat message:", error);
    } finally {
      setUserInput("");
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {history.map((msg, idx) => (
          <MessageBubble key={idx} isUser={msg.role === "user"}>
            {msg.content}
          </MessageBubble>
        ))}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      <InputContainer>
        <InputField
          type="text"
          placeholder={
            loading ? "Waiting for response..." : "Type your message..."
          }
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <SendButton onClick={handleSend} disabled={loading}>
          Send
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
}

export default ChatComponent;
