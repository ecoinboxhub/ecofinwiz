import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import client from "../api/client";

interface User {
  id: string; email: string; full_name: string; is_active: boolean; is_admin: boolean;
  created_at: string; plan?: string; persona_type?: string; onboarding_completed?: boolean;
  is_email_verified?: boolean;
}

interface AuthContextType {
  user: User | null; loading: boolean; login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void; googleLogin: (token: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      client.get("/users/me").then(({ data }) => setUser(data)).catch(() => logout()).finally(() => setLoading(false));
    } else setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await client.post("/auth/login", { email, password });
    localStorage.setItem("access_token", data.tokens.access_token);
    localStorage.setItem("refresh_token", data.tokens.refresh_token);
    const { data: userData } = await client.get("/users/me");
    setUser(userData);
  };

  const register = async (email: string, password: string, full_name: string) => {
    const { data } = await client.post("/auth/register", { email, password, full_name });
    localStorage.setItem("access_token", data.tokens.access_token);
    localStorage.setItem("refresh_token", data.tokens.refresh_token);
    setUser({ ...data.user, is_email_verified: false, onboarding_completed: false });
  };

  const googleLogin = async (idToken: string) => {
    const { data } = await client.post("/auth/google", { id_token: idToken });
    localStorage.setItem("access_token", data.tokens.access_token);
    localStorage.setItem("refresh_token", data.tokens.refresh_token);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    window.location.href = "/login";
  };

  return <AuthContext.Provider value={{ user, loading, login, register, logout, googleLogin }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
