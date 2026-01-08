import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  largeTextMode: boolean
  toggleLargeText: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      largeTextMode: false,
      toggleLargeText: () => set((state) => ({ largeTextMode: !state.largeTextMode })),
    }),
    {
      name: 'ui-storage',
    }
  )
)
