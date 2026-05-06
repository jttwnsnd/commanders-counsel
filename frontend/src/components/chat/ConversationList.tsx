import { useState, useEffect } from 'react'
import type { Conversation } from '../../types'
import api from '../../api/axios'

interface Props {
    activeConversation: Conversation | null
    onSelect: (conversation: Conversation) => void
}

export default function ConversationList({ activeConversation, onSelect }: Props) {
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        fetchConversations()
    }, [])

    const fetchConversations = async () => {
        try{
            const res = await api.get('/chat/conversations')
            setConversations(res.data)
        } catch {
            console.error('Failed to fetch conversations');
        }
    }
    const createConversation = async () => {
        setLoading(true)
        try {
            const res = await api.post('/chat/conversations', {
                title: 'New Conversation'
            })
            setConversations(prev => [res.data, ...prev])
            onSelect(res.data)
        } catch {
            console.error('Failed to create conversation')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            <div className="p-3">
                <button
                onClick={createConversation}
                disabled={loading}
                className="w-full bg-yellow-400 text-gray-900 font-bold py-2 rounded hover:bg-yellow-300 disabled:opacity-50 text-sm"
                >
                + New Conversation
                </button>
            </div>
            <div className="flex-1 overflow-y-auto">
                {conversations.map(conv => (
                <button
                    key={conv.id}
                    onClick={() => onSelect(conv)}
                    className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-700 border-b border-gray-700 ${
                    activeConversation?.id === conv.id ? 'bg-gray-700 text-yellow-400' : 'text-gray-300'
                    }`}
                >
                    {conv.title}
                </button>
                ))}
            </div>
        </div>
    )
}