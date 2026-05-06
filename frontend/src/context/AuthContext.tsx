import { createContext, useContext, useEffect, useState } from "react"
import type { ReactNode } from "react"
import api from "../api/axios"
import type { User } from "../types"

interface AuthContextType {
    user: User | null
    loading: boolean
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    // We only need this to run once on app load to check if the user is already logged in
    useEffect(() => {
        api.get('/auth/me')
            .then(res => setUser(res.data))
            .catch(()=> setUser(null))
            .finally( () => setLoading(false))
    }, [])

    const login = async (email: string, password: string) => {
        await api.post('/auth/login', { email, password })
        const res = await api.get('/auth/me')
        setUser(res.data)
    }

    const register = async (email: string, password: string) => {
        await api.post('/auth/register', { email, password })
        const res = await api.get('/auth/me')
        setUser(res.data)
    }

    const logout = async () => {
        await api.post('/auth/logout')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) throw new Error("useAuth must be used within an AuthProvider")
    return context
}