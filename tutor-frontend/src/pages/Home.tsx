import React from "react";

function Home() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Bienvenido a Tutor Virtual</h1>
      <p style={styles.subtitle}>
        Aquí podrás encontrar ejercicios personalizados y un tutor adaptativo para mejorar tus habilidades.
      </p>
      <div style={styles.actions}>
        <button style={styles.button} onClick={() => alert("¡Funcionalidad en desarrollo!")}>
          Registrarme
        </button>
        <button style={styles.button} onClick={() => alert("¡Funcionalidad en desarrollo!")}>
          Iniciar Sesión
        </button>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    margin: "0 auto",
    maxWidth: "600px",
    padding: "2rem",
    textAlign: "center",
    fontFamily: "sans-serif",
  },
  title: {
    fontSize: "2rem",
    marginBottom: "1rem",
  },
  subtitle: {
    fontSize: "1.2rem",
    marginBottom: "2rem",
    color: "#666",
  },
  actions: {
    display: "flex",
    gap: "1rem",
    justifyContent: "center",
  },
  button: {
    backgroundColor: "#333",
    color: "#fff",
    padding: "0.5rem 1rem",
    border: "none",
    borderRadius: "0.3rem",
    cursor: "pointer",
  },
};

export default Home;
