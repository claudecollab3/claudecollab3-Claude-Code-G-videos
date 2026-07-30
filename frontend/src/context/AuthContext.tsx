import React, { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { apiJson, getAccessToken, setTokens } from "../api";

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  totp_enabled: boolean;
  created_at: string;
}

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string, totpCode?: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    try {
      const me = await apiJson<CurrentUser>("/users/me");
      setUser(me);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (getAccessToken()) {
      fetchMe().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [fetchMe]);

  const login = useCallback(
    async (email: string, password: string, totpCode?: string) => {
      const body: Record<string, string> = { email, password };
      if (totpCode) body.totp_code = totpCode;
      const tokens = await apiJson<TokenPair>("/auth/login", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setTokens(tokens.access_token, tokens.refresh_token);
      await fetchMe();
    },
    [fetchMe],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      await apiJson("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    setTokens(null, null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
