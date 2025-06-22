import type { ViewMode } from "./ViewModeContext";


export interface ViewModeContextValue {
  ready: boolean;
  mode: ViewMode;
  setMode: (m: ViewMode) => void;
}
