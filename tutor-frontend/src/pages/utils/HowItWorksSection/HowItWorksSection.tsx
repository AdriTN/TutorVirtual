import React from "react";
import styles from "./HowItWorksSection.module.css";

const HowItWorksSection: React.FC = () => {
  return (
    <section className={styles.howContainer}>
      <h2 className={styles.howTitle}>Cómo Funciona</h2>
      <div className={styles.howSteps}>
        <div className={styles.howStep}>
          <img
            src="/assets/step1.svg"
            alt="Paso 1"
            className={styles.howIcon}
          />
          <h4 className={styles.stepTitle}>1. Regístrate</h4>
          <p className={styles.stepText}>
            Crea tu cuenta y realiza un test de diagnóstico inicial.
          </p>
        </div>
        <div className={styles.howStep}>
          <img
            src="/assets/step2.svg"
            alt="Paso 2"
            className={styles.howIcon}
          />
          <h4 className={styles.stepTitle}>2. Recibe Ejercicios</h4>
          <p className={styles.stepText}>
            La IA determina contenidos adaptados a tu nivel.
          </p>
        </div>
        <div className={styles.howStep}>
          <img
            src="/assets/step3.svg"
            alt="Paso 3"
            className={styles.howIcon}
          />
          <h4 className={styles.stepTitle}>3. Monitorea tu Progreso</h4>
          <p className={styles.stepText}>
            Revisa estadísticas y sigue tu evolución en tiempo real.
          </p>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
