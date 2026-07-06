import { createContext, useContext, useState, useCallback } from "react";
import { api, setToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [username, setUsername] = useState(localStorage.getItem("sgl_username"));

  const login = useCallback(async (uname, password) => {
    const data = await api.post("/auth/login", { username: uname, password });
    setToken(data.access_token);
    localStorage.setItem("sgl_username", uname);
    setUsername(uname);
  }, []);

  const register = useCallback(async (uname, password) => {
    const data = await api.post("/auth/register", { username: uname, password });
    setToken(data.access_token);
    localStorage.setItem("sgl_username", uname);
    setUsername(uname);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    localStorage.removeItem("sgl_username");
    setUsername(null);
  }, []);

  return (
    <AuthContext.Provider value={{ username, isAuthenticated: !!username, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
