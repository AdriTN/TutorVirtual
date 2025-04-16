import React, { useState } from "react";
import styles from "./BenefitsSection.module.css";

interface Benefit {
  title: string;
  description: string;
  image: string;
}

type Direction = "left" | "right";

const BenefitsSection: React.FC = () => {
  const benefits: Benefit[] = [
    {
      title: "Aprendizaje Personalizado",
      description: "Con un sistema que analiza tu nivel de dominio en cada tema, nuestras herramientas adaptan los contenidos y ejercicios a tus fortalezas y debilidades. De esta manera, evitas avanzar demasiado rápido en áreas críticas y ahorras tiempo en conceptos que ya dominas. Al personalizar tu ruta de aprendizaje, mejoras tu rendimiento y motivación, pues cada tarea se ajusta a tu ritmo y objetivos concretos.",
      image: "/benefit1.png",
    },
    {
      title: "Retroalimentación Constante",
      description: "Recibir respuestas detalladas en tiempo real es clave para un progreso sólido. Nuestro sistema de retroalimentación no se limita a decirte si la respuesta es correcta o incorrecta: también te ofrece sugerencias, ejemplos adicionales y enlaces a recursos útiles. De este modo, corriges tus errores de inmediato, aclaras dudas y refuerzas lo aprendido, transformando cada equivocación en una oportunidad de crecimiento.",
      image: "/benefit2.png",
    },
    {
      title: "Seguimiento de Progreso y Metas",
      description: "Con paneles de estadísticas sencillos de leer, mides tu evolución de forma transparente. Observa cuántos ejercicios has resuelto, cuánto tiempo has dedicado a cada tema y cuáles áreas te generan más dificultad. Estas métricas te ayudan a plantear metas específicas, priorizar asignaturas y analizar tu desempeño en distintos periodos. Tener una visión global te motiva a avanzar paso a paso, celebrando tus logros y enfocando tus esfuerzos en lo que más lo requiere.",
      image: "/benefit3.png",
    },
  ];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState<Direction>("right");

  const handlePrev = () => {
    setDirection("left");
    setCurrentIndex((prev) => (prev === 0 ? benefits.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setDirection("right");
    setCurrentIndex((prev) => (prev === benefits.length - 1 ? 0 : prev + 1));
  };

  return (
    <section className={styles.benefitsSection}>
      <h2 className={styles.sectionTitle}>Beneficios</h2>

      <div className={styles.carouselWrapper}>
        <button className={styles.arrowLeft} onClick={handlePrev}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#fff"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="50"
            height="50"
          >
            <path d="M15 6L9 12L15 18" />
          </svg>
        </button>

        <div
          key={currentIndex}
          className={`${styles.contentBox} ${
            direction === "right" ? styles.slideRight : styles.slideLeft
          }`}
        >
          <div className={styles.textContainer}>
            <h3 className={styles.benefitTitle}>
              {benefits[currentIndex].title}
            </h3>
            <p className={styles.benefitDescription}>
              {benefits[currentIndex].description}
            </p>
          </div>

          <div className={styles.imageContainer}>
            <img
              src={benefits[currentIndex].image}
              alt={benefits[currentIndex].title}
            />
          </div>
        </div>

        <button className={styles.arrowRight} onClick={handleNext}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#fff"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="50"
            height="50"
          >
            <path d="M9 6L15 12L9 18" />
          </svg>
        </button>
      </div>

      <div className={styles.indicators}>
        {benefits.map((_, idx) => (
          <span
            key={idx}
            className={
              idx === currentIndex
                ? `${styles.dot} ${styles.active}`
                : styles.dot
            }
            onClick={() => {
              setDirection(idx > currentIndex ? "right" : "left");
              setCurrentIndex(idx);
            }}
          />
        ))}
      </div>
    </section>
  );
};

export default BenefitsSection;
