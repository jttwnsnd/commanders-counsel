import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'

export default function LoginForm() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setError('');
        setLoading(true);
        try{
            await login(email, password);
        } catch {
            setError('Invalid email or password');
        } finally {
            setLoading(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
                <label className="text-gray-300 text-sm mb-1 block">Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={ event => setEmail(event.target.value) }
                    className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
            </div>
            <div>
                <label className="text-gray-300 text-sm mb-1 block">Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={ event => setPassword(event.target.value) }
                    className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button
                type="submit"
                disabled={loading}
                className="bg-yellow-400 text-gray-900 font-bold py-2 rounded hover:bg-yellow-300 disabled:opacity-50"
            >
                {loading ? "Logging in..." : "Login"}
            </button>
        </form>
    )
}