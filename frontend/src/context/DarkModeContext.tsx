import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

interface DarkModeContextType {
  dark: boolean;
  toggle: () => void;
}

const DarkModeContext = createContext<DarkModeContextType>({ dark: false, toggle: () => {} });

export function DarkModeProvider({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) return saved === "true";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) { root.classList.add("dark"); } else { root.classList.remove("dark"); }
    localStorage.setItem("darkMode", String(dark));
  }, [dark]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) => {
      if (localStorage.getItem("darkMode") === null) setDark(e.matches);
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  return (
    <DarkModeContext.Provider value={{ dark, toggle: () => setDark((d) => !d) }}>
      {children}
    </DarkModeContext.Provider>
  );
}

export function useDarkMode() {
  return useContext(DarkModeContext);
}
