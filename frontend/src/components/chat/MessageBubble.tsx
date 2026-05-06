import type { Message } from '../../types'

interface Props {
    message: Message
}

export default function MessageBubble({ message }: Props) {
    const isUser = message.role === 'user'

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 text-sm whitespace-pre-wrap ${
          isUser
            ? 'bg-yellow-400 text-gray-900'
            : 'bg-gray-700 text-gray-100'
        }`}
      >
        {!isUser && (
          <p className="text-yellow-400 font-bold text-xs mb-1">Commander's Counsel</p>
        )}
        {message.content}
      </div>
    </div>
  )
}