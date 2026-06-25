import { create } from "zustand";

type UIState = {
  dark: boolean;
  toggleDark: () => void;
};

export const useUIStore = create<UIState>((set) => ({
  dark: false,
  toggleDark: () => set((s) => ({ dark: !s.dark })),
}));
