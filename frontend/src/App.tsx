import { AuthProvider } from './context/AuthContext'
import AuthPage from './pages/AuthPage'
import ChatPage from './pages/ChatPage'
import { useAuth } from './context/AuthContext'

function AppContent() {

  const { user, loading } = useAuth()

  if (loading) return (
    <div className="flex items-center justify-center h-center bg-gray-900 text-white">
      Loading...
    </div>
  )
  return user ? <ChatPage /> : <AuthPage />
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}