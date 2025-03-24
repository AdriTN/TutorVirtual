import React, { useState } from "react";
import { api } from "../../services/apis/api";
import styles from "./Login.module.css";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

interface LoginFormProps {
  endpointUrl: string;
}

const Login: React.FC<LoginFormProps> = ({ endpointUrl }) => {
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await api.post(endpointUrl, {
        email: correo,
        password: password,
      });

      // Si llega aquí, es que la autenticación fue exitosa
      login(); // actualiza el estado global de login
      navigate("/dashboard"); // redirige al dashboard
    } catch (error) {
      console.error("Error en login:", error);
      alert("Error al iniciar sesión. Verifica tus credenciales.");
    }
  };

  return (
    <section className={styles.formLogin}>
      <h4>Iniciar Sesión</h4>
      <form onSubmit={handleSubmit}>
        <input
          className={styles.controls}
          type="email"
          name="correo"
          placeholder="Ingrese su Correo"
          value={correo}
          required
          onChange={(e) => setCorreo(e.target.value)}
        />
        <input
          className={styles.controls}
          type="password"
          name="password"
          placeholder="Ingrese su Contraseña"
          value={password}
          required
          onChange={(e) => setPassword(e.target.value)}
        />

        <input
          className={styles.botons}
          type="submit"
          value="Iniciar Sesión"
        />
      </form>

      <div className={styles.haveAccount}>
        <Link to="/register">¿No tienes cuenta? Regístrate</Link>
      </div>
    </section>
  );
};

export default Login;
