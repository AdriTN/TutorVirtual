import { useNavigate } from "react-router-dom";
import NavBar              from "@components/organisms/NavBar/NavBar";
import Footer              from "@components/organisms/Footer/Footer";
import HeroSection         from "../components/HeroSection/HeroSection";
import HowItWorksSection   from "../components/HowItWorksSection/HowItWorksSection";
import BenefitsSection     from "../components/BenefitsSection/BenefitsSection";


export default function HomePage() {
  const navigate = useNavigate();
  const goToRegister = () => navigate("/register", { replace:false });

  return (
    <>
      <NavBar />

      {/* Contenido principal semántico */}
      <main>
        <HeroSection
          title="Tu tutor inteligente"
          subtitle="Combina IA y enseñanza personalizada. Aprende lo que quieras, cuando quieras, a tu propio ritmo."
          imageUrl="/tutor-hero.png"
          ctaLabel="Empieza gratis"
          onButtonClick={goToRegister}
        />

        <HowItWorksSection />
        <BenefitsSection />
      </main>

      <Footer />
    </>
  );
}
