import React from 'react';
import Markdown from 'react-markdown';

interface ChatMessageProps {
  content: string;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ content, isUser }) => {
  const initials = isUser ? 'You' : 'AI';
  // Use green for user, blue for AI
  const bgColor = isUser ? 'bg-green-700':'bg-blue-500';

  return (
    <div className="my-4">
    {isUser ? (
      <div className="flex items-start space-x-2">
        <div className="w-10 h-10"></div>
          <div className="bg-gray-100 p-3 rounded-lg shadow-sm flex-grow">
            <div className="text-gray-600"><Markdown>{content}</Markdown></div>
          </div>
        <div
          className={`w-10 h-10 flex-shrink-0 flex items-center justify-center ${bgColor} rounded-full text-white`}
        >
          {initials}
        </div>
      </div>
    ) : (
      <div className="flex items-start space-x-2">
        <div
          className={`w-10 h-10 flex-shrink-0 flex items-center justify-center ${bgColor} rounded-full text-white`}
        >
          {initials}
        </div>
        <div className="bg-white p-3 rounded-lg shadow-sm flex-grow">
          <div className="text-gray-600"><Markdown>{content}</Markdown></div>
        </div>
        <div className="w-10 h-10"></div>
      </div>
    )}
  </div>
  );
};

export default ChatMessage;
