import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";

import { api }     from "@services/api/backend";
import { useAuth } from "@context/auth/AuthContext";

import styles from "./MyGoogleButton.module.css";

interface Props {
  endpointUrl?: string;
}

const MyGoogleButton = ({ endpointUrl = "/api/auth/google" }: Props) => {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [loading, setLoading] = useState(false);

  const googleLogin = useGoogleLogin({
    scope: "profile email",
    onSuccess: async ({ access_token }) => {
      if (!access_token) return;

      try {
        setLoading(true);
        const { data } = await api.post(endpointUrl, { token: access_token });

        const { access_token: jwt, refresh_token } = data;
        login(jwt, refresh_token);

        navigate("/dashboard");
      } catch (err) {
        console.error("Google login error:", err);
      } finally {
        setLoading(false);
      }
    },
    onError: err => {
      console.error("Google OAuth error:", err);
    },
    flow: "implicit",
  });

  return (
    <button
      type="button"
      className={styles.button}
      onClick={() => googleLogin()}
      aria-label="Iniciar sesión con Google"
      disabled={loading}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="xMidYMid"
        viewBox="0 0 256 262"
      >
        {/* …paths… */}
      </svg>
      {loading ? "Conectando…" : "Continuar con Google"}
    </button>
  );
};

export default MyGoogleButton;
