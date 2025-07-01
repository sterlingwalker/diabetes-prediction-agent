import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import styled, { keyframes } from "styled-components";

const ChatContainer = styled.div`
  max-width: 900px;
  min-width: 700px;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 500px;
  margin: 0 auto;
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
  p {
    margin: 0;
  }
`;

const blink = keyframes`
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
`;

const Dot = styled.span`
  animation: ${blink} 1.4s infinite both;
  margin-right: 2px;
  font-size: 1.75rem;
  line-height: 0.75;
  &:nth-child(1) {
    animation-delay: 0s;
  }
  &:nth-child(2) {
    animation-delay: 0.2s;
  }
  &:nth-child(3) {
    animation-delay: 0.4s;
  }
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
  }, [history, loading]);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const updatedHistory = [...history, { role: "user", content: userInput }];
    setHistory(updatedHistory);

    //Delay the loading indicator for a more realistic feel
    setTimeout(() => {
      setLoading(true);
    }, 500);

    try {
      const response = await axios.post(
        "https://diabetes-675059836631.us-central1.run.app/chat",
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
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </MessageBubble>
        ))}
        {loading && (
          <MessageBubble isUser={false} key="typing-indicator">
            <Dot>•</Dot>
            <Dot>•</Dot>
            <Dot>•</Dot>
          </MessageBubble>
        )}
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
