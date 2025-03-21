import { BrowserRouter, Routes, Route } from "react-router-dom";
import RegisterPage from "./pages/register/RegisterPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* <Route path="/" element={<Home />} /> */}
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
