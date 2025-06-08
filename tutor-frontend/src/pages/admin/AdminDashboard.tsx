
import React from "react";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";

const AdminDashboard: React.FC = () => (
  <>
    <NavBar />
    <main style={{ padding: "2rem" }}>
      <h1>Panel de administración</h1>
      <p>Solo visible si estás en modo **admin**.</p>
    </main>
    <Footer />
  </>
);
export default AdminDashboard;
