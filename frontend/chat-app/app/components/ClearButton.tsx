import React from 'react';
import { TrashIcon } from '@heroicons/react/20/solid'; 


interface ClearButtonProps {
  onClick: () => void;
}

const ClearButton: React.FC<ClearButtonProps> = ({ onClick }) => {
  return (
    <button
      className="text-gray-600 text-sm hover:text-gray-800 hover:shadow-sm focus:outline-none flex items-center"
      onClick={onClick}
    >
      Clear Conversation
      <TrashIcon className="w-4 h-4 mr-1" />
    </button>
  );
};

export default ClearButton;