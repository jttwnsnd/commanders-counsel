import { useState, useEffect, useRef } from 'react'
import type { Message, Conversation } from '../../types'
import api from '../../api/axios'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

interface Props {
    conversation: Conversation
}

export default function ChatWindow({ conversation }: Props) {
    const [ messages, setMessages ] = useState<Message[]>([])
    const [ streaming, setStreaming ] = useState(false)
    const [streamingContent, setStreamingContent] = useState('')
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        fetchMessages()
    }, [conversation.id])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, streamingContent])

    const fetchMessages = async () => {
        try {
            const res = await api.get(`/chat/conversations/${conversation.id}/messages`)
            setMessages(res.data)
        } catch {
            console.error('Failed to fetch messages')
        }
    }

    const sendMessage = async (content: string) => {
        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content,
            created_at: new Date().toISOString()
        }
        setMessages(prev => [...prev, userMessage])
        setStreaming(true)
        setStreamingContent('')

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                conversation_id: conversation.id,
                message: content
                })
            })

            const reader = response.body!.getReader()
            const decoder = new TextDecoder()
            let fullContent = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                const chunk = decoder.decode(value)
                fullContent += chunk
                setStreamingContent(fullContent)
            }

            const assistantMessage: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: fullContent,
                created_at: new Date().toISOString()
            }
            setMessages(prev => [...prev, assistantMessage])
            setStreamingContent('')
        } catch {
            console.error('Failed to send message')
        } finally {
            setStreaming(false)
        }
    }

    return (
        <div className="flex flex-col h-full">
            <div className="p-4 border-b border-gray-700">
                <h2 className="font-bold text-gray-200">{conversation.title}</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
                {messages.map(msg => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                {streaming && streamingContent && (
                    <div className="flex mb-4 justify-start">
                        <div className="max-w-[70%] rounded-lg px-4 py-3 text-sm bg-gray-700 text-gray-100 whitespace-pre-wrap">
                            <p className="text-yellow-400 font-bold text-xs mb-1">Commander's Counsel</p>
                            {streamingContent}
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>
            <ChatInput onSend={sendMessage} disabled={streaming} />
        </div>
    )
}