import React from "react";
import NavBar from "../utils/NavBar/NavBar";
import HeroSection from "../utils/HeroSection/HeroSection";
import HowItWorksSection from "../utils/HowItWorksSection/HowItWorksSection";
import FeaturesSection from "../utils/FeaturesSection/FeaturesSection";
import Footer from "../utils/Footer/Footer";

// Importa un CSS global si deseas, o uno local
// con .homeContainer por si quieres algo extra.
// Sino, puede quedar vacío.

const HomePage: React.FC = () => {
  const handleHeroButtonClick = () => {
    alert("¡Funcionalidad próximamente!");
  };

  return (
    <>
      <NavBar
        logoUrl="/assets/logo.png"
        brandName="Tutor Virtual"
        links={[
          { label: "Inicio", path: "/" },
          { label: "Cómo Funciona", path: "/how" },
          { label: "Ejercicios", path: "/exercises" },
          { label: "Login", path: "/login" },
        ]}
      />

      <HeroSection
        title="Tutor Virtual"
        subtitle="El portal de aprendizaje adaptativo, impulsado por IA."
        buttonLabel="¡Comienza Ahora!"
        imageUrl="/assets/tutor-hero.png"
        onButtonClick={handleHeroButtonClick}
      />
      <HowItWorksSection />
      <FeaturesSection />
      <Footer />
    </>
  );
};

export default HomePage;
