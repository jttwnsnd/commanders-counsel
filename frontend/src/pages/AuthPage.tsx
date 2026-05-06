import { useState } from 'react'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

export default function AuthPage() {
    const [isLogin, setIsLogin] = useState(true)

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-900">
            <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
                <h1 className="text-3xl font-bold text-center text-yellow-400 mb-2">
                    Commander's Counsel
                </h1>
                <p className="text-gray-400 text-center mb-6">
                    Your MTG Deck Building Assistant
                </p>

                { isLogin ? <LoginForm /> : <RegisterForm /> }

                <p className="text-gray-400 text-center mt-4">
                    { isLogin ? "Don't have an account?" : "Already have an account"}
                    <button 
                    onClick={()=> setIsLogin(!isLogin)}
                    className="text-yellow-400 ml-2 hover:underline">
                        { isLogin ? "Register" : "Login" }
                    </button>
                </p>
            </div>
        </div>
    )
}