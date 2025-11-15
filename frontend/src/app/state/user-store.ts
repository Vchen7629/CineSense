// This file contains the "store" or global state relating to users
import { create } from 'zustand'

interface AuthState {
    loggedIn: boolean
    login: () => void
    logout: () => void
}

export const useAuthState = create<AuthState>((set) => ({
    loggedIn: false, // current logged in state
    login: () => set({ loggedIn: true }),
    logout: () => set({ loggedIn: false })
}))
