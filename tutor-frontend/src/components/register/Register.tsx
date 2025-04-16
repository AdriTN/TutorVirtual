import React, { useState } from "react";
import { api } from "../../services/apis/backend-api/api";
import styles from "./Register.module.css";
import { Link, useNavigate } from "react-router-dom";

interface RegisterFormProps {
  endpointUrl: string;
}

const Register: React.FC<RegisterFormProps> = ({ endpointUrl }) => {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  // Estado del checkbox de términos y condiciones
  const [agreed, setAgreed] = useState(false);

  // Manejo de envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }

    // Verificar que se acepten términos y condiciones
    if (!agreed) {
      alert("Debe aceptar los Términos y condiciones para registrarse.");
      return;
    }

    try {
      const response = await api.post(endpointUrl, {
        username: nombre,
        email: correo,
        password: password,
        confirmPassword: confirmPassword,
      });
      console.log("Usuario creado:", response.data);
      alert("Registrado con éxito");

      navigate("/login");
    } catch (error) {
      console.error("Error en registro:", error);
      alert("Error en el registro");
    }
  };

  return (
    <section className={styles.formRegister}>
      <h4>Formulario Registro</h4>

      <form onSubmit={handleSubmit}>
        <input
          className={styles.controls}
          type="text"
          name="nombre"
          placeholder="Ingrese su Nombre*"
          value={nombre}
          required
          onChange={(e) => setNombre(e.target.value)}
        />

        <input
          className={styles.controls}
          type="email"
          name="correo"
          placeholder="Ingrese su Correo*"
          value={correo}
          required
          onChange={(e) => setCorreo(e.target.value)}
        />

        <input
          className={styles.controls}
          type="password"
          name="password"
          placeholder="Ingrese su Contraseña*"
          value={password}
          required
          onChange={(e) => setPassword(e.target.value)}
        />

        <input
          className={styles.controls}
          type="password"
          placeholder="Repita su Contraseña*"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          style={{ width: "100%", padding: "0.5rem" }}
        />

        <div className={styles.agreementWrapper}>
          <label className={styles.checkboxContainer}>
            <input type="checkbox" defaultChecked={false} onChange={(e) => setAgreed(e.target.checked)}/>
            <div className={styles.checkmark} />
            <span className={styles.checkboxLabel}>
              Estoy de acuerdo con <a href="#">Terminos y Condiciones</a>
            </span>
          </label>
        </div>

        <input
          className={styles.botons}
          type="submit"
          value="Registrar"
        />
      </form>

      <div className={styles.haveAccount}>
        <Link to="/login">Ya tengo cuenta</Link>
      </div>

    </section>
  );
};

export default Register;
