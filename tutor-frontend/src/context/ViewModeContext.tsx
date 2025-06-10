/* ViewModeContext.tsx – versión estable */
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

  const [mode,  setModeState] = useState<ViewMode>("user");
  const [ready, setReady]     = useState(false);

  /* decide cuando Auth terminó */
  useEffect(() => {
    if (authLoading) return;

    const stored = localStorage.getItem("viewMode") as ViewMode | null;

    if (isAdmin) {
      setModeState("admin");          // ← SIEMPRE admin si el rol lo permite
    } else if (stored) {
      setModeState(stored);           // usuario normal mantiene su elección
    } else {
      setModeState("user");
    }
    setReady(true);
  }, [authLoading, isAdmin]);

  /* persiste cada cambio */
  useEffect(() => {
    if (ready) localStorage.setItem("viewMode", mode);
  }, [mode, ready]);

  /* si el rol baja de admin → user */
  useEffect(() => {
    if (!authLoading && !isAdmin && mode === "admin") setModeState("user");
  }, [isAdmin, authLoading, mode]);

  /* setter seguro */
  const setMode = (m: ViewMode) => {
    if (m === "admin" && !isAdmin) return;   // impedir escalada
    setModeState(m);
  };

  return (
    <Ctx.Provider value={{ ready, mode, setMode }}>
      {children}
    </Ctx.Provider>
  );
};

/* hooks */
export const useViewMode      = () => useContext(Ctx)!;
export const useActingAsAdmin = () => {
  const { isAdmin }   = useAuth();
  const { mode }      = useViewMode();
  return isAdmin && mode === "admin";
};
