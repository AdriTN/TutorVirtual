import React from "react";

export const Spinner: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       style={{ animation: "rotate 1s linear infinite" }}>
    <circle cx="12" cy="12" r="10"
      stroke="var(--c-border-strong)" strokeWidth="4" opacity=".25"/>
    <path d="M22 12a10 10 0 0 1-10 10" stroke="var(--c-primary)" strokeWidth="4"/>
    <style>{`@keyframes rotate{100%{transform:rotate(360deg)}}`}</style>
  </svg>
);
