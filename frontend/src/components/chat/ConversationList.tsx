import { useState, useEffect, useRef } from 'react'
import type { Conversation } from '../../types'
import api from '../../api/axios'

interface Props {
    activeConversation: Conversation | null
    onSelect: (conversation: Conversation) => void
    onConversationUpdate: (conversation: Conversation) => void
    onConversationDelete: (id: string) => void
}

export default function ConversationList({ activeConversation, onSelect, onConversationUpdate, onConversationDelete }: Props) {
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [loading, setLoading] = useState(false)
    const [editingId, setEditingId] = useState<string | null>(null)
    const [editingTitle, setEditingTitle] = useState('')
    const inputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        fetchConversations()
    }, [])

    useEffect(() => {
        if (editingId && inputRef.current) {
            inputRef.current.focus()
        }
    }, [editingId])

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

    const startEditing = (conv: Conversation, e: React.MouseEvent) => {
        e.stopPropagation()
        setEditingId(conv.id)
        setEditingTitle(conv.title)
    }

    const saveTitle = async (conv: Conversation) => {
        if (!editingTitle.trim() || editingTitle === conv.title) {
            setEditingId(null)
            return
        }
        try {
            const res = await api.patch(`/chat/conversations/${conv.id}/title`, {
                title: editingTitle.trim()
            })
            setConversations(prev => prev.map(c => c.id === conv.id ? res.data : c))
            onConversationUpdate(res.data)
        } catch {
        console.error('Failed to update title')
        } finally {
            setEditingId(null)
        }
    }

    const deleteConversation = async (conv: Conversation, e: React.MouseEvent) => {
        e.stopPropagation()
        if (!confirm(`Delete "${conv.title}"?`)) return
        try {
            await api.delete(`/chat/conversations/${conv.id}`)
            setConversations(prev => prev.filter(c => c.id !== conv.id))
            onConversationDelete(conv.id)
        } catch {
            console.error('Failed to delete conversation')
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
                <div
                    key={conv.id}
                    onClick={() => onSelect(conv)}
                    className={`group flex items-center gap-1 px-2 py-3 text-sm cursor-pointer hover:bg-gray-700 border-b border-gray-700 ${
                        activeConversation?.id === conv.id ? 'bg-gray-700 text-yellow-400' : 'text-gray-300'
                    }`}
                >
                    {editingId === conv.id ? (
                        <input
                        ref={inputRef}
                        value={editingTitle}
                        onChange={e => setEditingTitle(e.target.value)}
                        onBlur={() => saveTitle(conv)}
                        onKeyDown={e => {
                            if (e.key === 'Enter') saveTitle(conv)
                            if (e.key === 'Escape') setEditingId(null)
                        }}
                        onClick={e => e.stopPropagation()}
                        className="flex-1 bg-gray-600 text-white rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-yellow-400"
                        />
                    ) : (
                        <span className="flex-1 truncate">{conv.title}</span>
                    )}
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={e => startEditing(conv, e)}
                            className="text-gray-400 hover:text-yellow-400 px-1"
                            title="Rename"
                        >
                        ✏️
                        </button>
                        <button
                            onClick={e => deleteConversation(conv, e)}
                            className="text-gray-400 hover:text-red-400 px-1"
                            title="Delete"
                        >
                        🗑️
                        </button>
                    </div>
                </div>
            ))}
        </div>
    </div>
  )
}