import { useState } from 'react'
import type { Conversation } from '../types'
import ConversationList from '../components/chat/ConversationList'
import ChatWindow from '../components/chat/ChatWindow'
import { useAuth } from '../context/AuthContext'

export default function ChatPage(){
    const { logout, user } = useAuth()
    const [ activeConversation, setActiveConversation ] = useState<Conversation | null>(null)
    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Sidebar */}
            <div className="w-64 bg-gray-800 flex flex-col">
                <div className="p-4 border-b border-gray-700">
                    <h1 className="text-yellow-400 font-bold text-lg">Commander's Counsel</h1>
                    <p className="text-gray-400 text-xs mt-1">{user?.email}</p>
                </div>
                <ConversationList
                    activeConversation={activeConversation}
                    onSelect={setActiveConversation}
                    />
                <div className="p-4 border-t border-gray-700">
                    <button
                        onClick={logout}
                        className="w-full text-gray-400 hover:text-white text-sm"
                    >
                        Logout
                    </button>
                </div>
            </div>

            {/* Main chat area */}
            <div className="flex-1 flex flex-col">
                {activeConversation
                ? <ChatWindow conversation={activeConversation} />
                : (
                    <div className="flex-1 flex items-center justify-center text-gray-500">
                        <div className="text-center">
                            <p className="text-2xl mb-2">🧙‍♂️</p>
                            <p>Select a conversation or start a new one</p>
                        </div>
                    </div>
                )
                }
            </div>
        </div>
  )
}