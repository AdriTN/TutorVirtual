import React from "react";
import { RegisterForm } from "../../hooks/register/RegisterForm";
import styles from "./Register.module.css";

interface RegisterFormProps {
  endpointUrl: string; // se lo pasamos al Hook
}

const Register: React.FC<RegisterFormProps> = () => {
  const {
    username,
    setUsername,
    email,
    setEmail,
    password,
    setPassword,
    message,
    error,
    handleSubmit,
  } = RegisterForm();

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.formTitle}>Registro de Usuario</h2>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Username</label>
          <input
            type="text"
            className={styles.input}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Email</label>
          <input
            type="email"
            className={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Password</label>
          <input
            type="password"
            className={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className={styles.submitButton}>
          Registrarse
        </button>
      </form>

      {/* Mensajes de feedback */}
      {message && (
        <div className={`${styles.message} ${styles.successMessage}`}>
          {message}
        </div>
      )}
      {error && (
        <div className={`${styles.message} ${styles.errorMessage}`}>
          {error}
        </div>
      )}
    </div>
  );
};

export default Register;
