import React, { createContext, useContext, useEffect, useState } from "react";
import { useAuth } from "./AuthContext";

export type ViewMode = "admin" | "user";

interface ViewModeCtx {
  ready: boolean;
  mode: ViewMode;
  setMode: (m: ViewMode) => void;
}

const Ctx = createContext<ViewModeCtx | undefined>(undefined);

export const ViewModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAdmin, loading: authLoading } = useAuth();

    const stored = localStorage.getItem("viewMode") as ViewMode | null;
    const [mode, setModeState] = useState<ViewMode>("user");
    const [ready, setReady]    = useState(false);

    useEffect(() => {
        if (authLoading) return;
        if (stored && (stored !== "admin" || isAdmin)) {
          setModeState(stored);
        } else {
          setModeState(isAdmin ? "admin" : "user");
        }
        setReady(true);
      }, [authLoading]);

  
    useEffect(() => {
        if (authLoading) return;
        if (stored && (stored !== "admin" || isAdmin)) {
        setModeState(stored);
        } else {
        setModeState(isAdmin ? "admin" : "user");
        }

    }, [authLoading]);


    useEffect(() => {
        if (!authLoading) localStorage.setItem("viewMode", mode);
    }, [mode, authLoading]);


    useEffect(() => {
        if (authLoading) return;
        if (!isAdmin && mode === "admin") setModeState("user");
    }, [isAdmin, mode, authLoading]);

    const setMode = (m: ViewMode) => {
        if (m === "admin" && !isAdmin) return;
        setModeState(m);
    };

    return <Ctx.Provider value={{ ready, mode, setMode }}>{children}</Ctx.Provider>;
};

export const useViewMode = () => {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useViewMode must be used within ViewModeProvider");
  return ctx;
};

export const useActingAsAdmin = () => {
  const { isAdmin } = useAuth();
  const { mode }    = useViewMode();
  return isAdmin && mode === "admin";
};