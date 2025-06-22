import React, { createContext, useContext, useEffect, useState } from "react";
import { useAuth } from "@/context/auth";
import { ViewModeContextValue } from "./view-mode.types";

export type ViewMode = "admin" | "user";

const ViewModeCtx = createContext<ViewModeContextValue | undefined>(undefined);

export const ViewModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAdmin, loading: authLoading } = useAuth();

  const [mode,  setModeState] = useState<ViewMode>("user");
  const [ready, setReady]     = useState(false);

  useEffect(() => {
    if (authLoading) return;

    const stored = localStorage.getItem("viewMode") as ViewMode | null;

    if (isAdmin) {
      setModeState("admin");
    } else if (stored) {
      setModeState(stored);
    } else {
      setModeState("user");
    }
    setReady(true);
  }, [authLoading, isAdmin]);

  useEffect(() => {
    if (ready) localStorage.setItem("viewMode", mode);
  }, [mode, ready]);

  useEffect(() => {
    if (!authLoading && !isAdmin && mode === "admin") setModeState("user");
  }, [isAdmin, authLoading, mode]);

  const setMode = (m: ViewMode) => {
    if (m === "admin" && !isAdmin) return;
    setModeState(m);
  };

  return (
    <ViewModeCtx.Provider value={{ ready, mode, setMode }}>
      {children}
    </ViewModeCtx.Provider>
  );
};

/* ---------- Hooks públicos ---------- */
export const useViewMode = () => {
  const ctx = useContext(ViewModeCtx);
  if (!ctx) throw new Error("useViewMode must be used within ViewModeProvider");
  return ctx;
};

export const useActingAsAdmin = () => {
  const { isAdmin } = useAuth();
  const { mode }    = useViewMode();
  return isAdmin && mode === "admin";
};
