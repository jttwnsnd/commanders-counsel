import { useState } from 'react'

interface Props {
    onSend: (message: string) => void
    disabled: boolean
}

export default function ChatInput({ onSend, disabled }: Props) {
    const [input, setInput] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || disabled) return
        onSend(input.trim())
        setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSubmit(e as unknown as React.FormEvent)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t border-gray-700">
        <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask about cards, rules, deck building..."
            rows={2}
            className="flex-1 bg-gray-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-yellow-400 resize-none disabled:opacity-50"
        />
        <button
            type="submit"
            disabled={disabled || !input.trim()}
            className="bg-yellow-400 text-gray-900 font-bold px-4 rounded hover:bg-yellow-300 disabled:opacity-50"
        >
            Send
        </button>
    </form>
  )
}