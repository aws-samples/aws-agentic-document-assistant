'use client';

import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ClearButton from './ClearButton';
import { PaperAirplaneIcon } from '@heroicons/react/20/solid';
import { fetchAuthSession, fetchUserAttributes } from 'aws-amplify/auth';

interface Message {
  content: string;
  isUser: boolean;
}

const ChatApp: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [clean_history, setCleanHistory] = useState<boolean>(false);
    const messageContainerRef = useRef<HTMLDivElement>(null);

    const handleSendMessage = async (message: string) => {
        // fetch the cognito authentication tokens to use with the API call.
        const authToken = (await fetchAuthSession()).tokens?.idToken?.toString()
        const userAttributes = (await fetchUserAttributes())
        // Append the user's input message to the message container immediately
        const userMessage = {"content": message, "isUser": true}
        setMessages([...messages, userMessage]);

        // Scroll to the bottom of the message container
        if (messageContainerRef.current) {
          messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
        }

        // Call the API to get the response
        const rest_api_endpoint = process.env.NEXT_PUBLIC_API_ENDPOINT || ""
        await fetch(rest_api_endpoint, {
          // mode: "no-cors",
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': authToken || ""
          },
          // Currently we use the cognito user.sub as a session_id
          // this needs to be updated if one wants to store multiple chats for the same user.
          body: JSON.stringify({
            "user_input": message ,
            "session_id": userAttributes.sub,
            "clean_history": clean_history
          })
        })
          .then(response => response.json())
          .then(responseData => {
            // Add the response to the messages state after receiving it
            let AIMessage: Message;
            if (responseData.errorMessage) {
              AIMessage = {
                "content": `Error: ${responseData.errorMessage}\n\nDetails: \n\n\`\`\`\n\n${JSON.stringify(responseData, null, 2)}\n\n\`\`\``,
                "isUser": false
              };
            } else {
              AIMessage = {"content": responseData.response, "isUser": false};
            }
            setMessages(prevMessages => [...prevMessages, AIMessage]);

            // Scroll to the bottom of the message container again after adding the response
            if (messageContainerRef.current) {
              messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
            }
          })
          .catch(error => {
            let AIMessage: Message = {
              "content": "Error while preparing your answer. Check your connectivity to the backend",
              "isUser": false
            }
            setMessages(prevMessages => [...prevMessages, AIMessage]);

            // Scroll to the bottom of the message container again after adding the response
            if (messageContainerRef.current) {
              messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
            }
          });
      };

    // below useEffect handles automatic scroll down when the messages content
    // overflows the container.
    useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
    }, [messages]);

    return (
    <div className="flex flex-col justify-center items-center">
        <div className="bg-white p-6 rounded-lg shadow-sm w-full">
        <div className="space-y-4">
            <div
            ref={messageContainerRef} 
            className="h-[68vh] overflow-hidden hover:overflow-y-scroll border-b border-gray-200">
            {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  content={message.content}
                  isUser={message.isUser}
                />
            ))}
            </div>
            <div className="flex space-x-2">
            <input
                id="chat-message-input"
                className="flex-1 p-2 border rounded-lg border-gray-300 focus:outline-none focus:ring focus:border-blue-500"
                type="text"
                placeholder="Type your message..."
                onKeyDown={(e) => {
                    // send message on enter if not empty
                    if (e.key === 'Enter') {
                        if (e.currentTarget.value !== '') {
                            handleSendMessage(e.currentTarget.value);
                            e.currentTarget.value = '';
                        }
                    }
                }}
                autoComplete="off"
                />
            <button
                className="px-2 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring focus:bg-blue-600 flex items-center"
                onClick={() => {
                    const inputElement = document.getElementById('chat-message-input') as HTMLInputElement;
                    const message = inputElement.value.trim();
                    // send message on button click if not empty
                    if (message !== '') {
                        handleSendMessage(message);
                        inputElement.value = '';
                    }
                }}
                >
                Send
                <PaperAirplaneIcon className="h-5 w-5 text-white ml-2" />
            </button>
            </div>
            <div className="flex justify-center mt-2">
              <ClearButton
                onClick={() => {
                  // Handle clearing the conversation
                  setMessages([]);
                  setCleanHistory(true);
                }}
              />
            </div>
        </div>
        </div>
    </div>
  );
};

export default ChatApp;
