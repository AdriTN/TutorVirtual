import React from "react";
import styles from "./HowItWorksSection.module.css";
import { useNavigate } from "react-router-dom";

const HowItWorksSection: React.FC = () => {
  const navigate = useNavigate();

  const handleRegisterClick = () => {
    navigate("/register");
  };

  return (
    <section className={styles.howContainer}>
      <h2 className={styles.howTitle}>¿Cómo Funciona?</h2>

      <div className={styles.cardsWrapper}>
        <div className={styles.card}>
          <svg
            viewBox="0 0 16 9"
            xmlns="http://www.w3.org/2000/svg"
            className={styles.cardSvg}
          >
            <image
              href="/step1.png"
              width="100%"
              height="100%"
              preserveAspectRatio="xMidYMid slice"
            />
          </svg>
          <div className={styles.card__content}>
            <p className={styles.card__title}>Regístrate</p>
            <p className={styles.card__description}>
            Regístrate gratis y accede a una plataforma impulsada por inteligencia artificial que se adapta a ti.
            Desde el primer momento, tu tutor virtual analizará tus intereses, tu ritmo y tu nivel para ofrecerte una experiencia única y personalizada.
            </p>
            <button className={styles.card__button} onClick={handleRegisterClick}>
              Sign up
              <div className={styles.arrowwrapper}>
                <div className={styles.arrow} />
              </div>
            </button>
          </div>
        </div>

        <div className={styles.card}>
          <svg
            viewBox="0 0 16 9"
            xmlns="http://www.w3.org/2000/svg"
            className={styles.cardSvg}
          >
            <image
              href="/step2.png"
              width="100%"
              height="100%"
              preserveAspectRatio="xMidYMid slice"
            />
          </svg>
          <div className={styles.card__content}>
            <p className={styles.card__title}>Busca Tu curso</p>
            <p className={styles.card__description}>
            Desde habilidades técnicas hasta desarrollo personal, encuentra exactamente lo que necesitas para crecer. Nuestra plataforma utiliza inteligencia artificial para recomendarte cursos que se ajustan a tus intereses, nivel de conocimiento y objetivos.
            <br /><br />
            Ya sea que estés empezando desde cero o quieras perfeccionar tus habilidades, aquí tienes el curso ideal esperándote.
            </p>
            <button className={styles.card__button} onClick={handleRegisterClick}>
              Sign up
              <div className={styles.arrowwrapper}>
                <div className={styles.arrow} />
              </div>
            </button>
          </div>
        </div>

        <div className={styles.card}>
          <svg
            viewBox="0 0 16 9"
            xmlns="http://www.w3.org/2000/svg"
            className={styles.cardSvg}
          >
            <image
              href="/step3.png"
              width="100%"
              height="100%"
              preserveAspectRatio="xMidYMid slice"
            />
          </svg>
          <div className={styles.card__content}>
            <p className={styles.card__title}>Mira Tu Progreso</p>
            <p className={styles.card__description}>
            Haz un seguimiento claro y motivador de todo lo que has aprendido. Tu panel de progreso te muestra los cursos completados, los temas dominados y tus avances día a día.
            <br /><br />
            Con cada paso, tu tutor virtual adapta los contenidos para que sigas evolucionando de forma eficiente, manteniéndote siempre en el camino correcto.
            </p>
            <button className={styles.card__button} onClick={handleRegisterClick}>
              Sign up
              <div className={styles.arrowwrapper}>
                <div className={styles.arrow} />
              </div>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
