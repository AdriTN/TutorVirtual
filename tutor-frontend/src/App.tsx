import { BrowserRouter, Link, Routes, Route } from "react-router-dom";
import Home from "./pages/home/Home";
import RegisterPage from "./pages/RegisterPage";

function App() {
  return (
    <BrowserRouter>
      {/* Pequeña barra de navegación de ejemplo */}
      <nav style={{ padding: "1rem" }}>
        <Link to="/" style={{ marginRight: "1rem" }}>Inicio</Link>
        <Link to="/register">Registro</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
