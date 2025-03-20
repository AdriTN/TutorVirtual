import React from "react";
import styles from "./FeaturesSection.module.css";

const FeaturesSection: React.FC = () => {
  return (
    <div className={styles.features}>
      <div className={styles.featureBox}>
        <img
          src="/assets/personalizado.svg"
          alt="Aprendizaje Personalizado"
          className={styles.icon}
        />
        <h3 className={styles.title}>Aprendizaje Personalizado</h3>
        <p className={styles.text}>
          El sistema se adapta a tus fortalezas y debilidades.
        </p>
      </div>

      <div className={styles.featureBox}>
        <img
          src="/assets/progreso.svg"
          alt="Monitoreo de Progreso"
          className={styles.icon}
        />
        <h3 className={styles.title}>Monitoreo de Progreso</h3>
        <p className={styles.text}>
          Ve tus estadísticas y tu evolución en todo momento.
        </p>
      </div>
      
      {/* ... más features si deseas */}
    </div>
  );
};

export default FeaturesSection;
