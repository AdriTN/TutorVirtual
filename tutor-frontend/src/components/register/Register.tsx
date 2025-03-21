import React, { useState } from "react";
import { api } from "../../services/apis/api";
import styles from "./Register.module.css";

interface RegisterFormProps {
  endpointUrl: string; // se lo pasamos si deseas, por ejemplo
}

const Register: React.FC<RegisterFormProps> = () => {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");

  // Manejo de envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Ajusta la URL del endpoint para tu backend real:
      const response = await api.post("/api/register", {
        nombre,
        correo,
        password,
      });
      console.log("Usuario creado:", response.data);
      alert("Registrado con éxito");
      // Podrías resetear estados o redirigir tras registrar
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
          placeholder="Ingrese su Nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
        />

        <input
          className={styles.controls}
          type="email"
          name="correo"
          placeholder="Ingrese su Correo"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />

        <input
          className={styles.controls}
          type="password"
          name="password"
          placeholder="Ingrese su Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {/* CHECKBOX + TEXTO EN UNA SOLA LÍNEA */}
        <div className={styles.agreementWrapper}>
          <label className={styles.checkboxContainer}>
            <input type="checkbox" defaultChecked={false} />
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
        <a href="#">Ya tengo cuenta</a>
      </div>

    </section>
  );
};

export default Register;
