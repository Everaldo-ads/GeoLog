import axios from 'axios'

// Endereço do backend. Vem do .env (VITE_API_URL) e, se não existir, usa localhost:8000.
export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// http://... vira ws://... e https://... vira wss://...
export const WS_URL = API_URL.replace(/^http/, 'ws')

export const api = axios.create({ baseURL: API_URL })
