import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ChatBubbleProps {
  content: string;
  isUser?: boolean;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ content, isUser }) => {
  return (
    <div
      className={`max-w-[90%] rounded-xl break-words whitespace-pre-wrap prose prose-sm sm:prose lg:prose-base [&>*]:m-0`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
};

export default ChatBubble;
