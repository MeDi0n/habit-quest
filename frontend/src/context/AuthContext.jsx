import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    try {
      const profile = await api.get("/profile");
      setUser(profile);
    } catch (err) {
      console.error("Не удалось загрузить профиль", err);
      localStorage.removeItem("token");
      setToken(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      loadUser();
    } else {
      setUser(null);
      setLoading(false);
    }
  }, [token]);

  async function login(email, password) {
    const data = await api.login({ email, password });
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  }

  async function register(email, username, password) {
    await api.register({ email, username, password });
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth нужно использовать внутри AuthProvider");
  }
  return context;
}
