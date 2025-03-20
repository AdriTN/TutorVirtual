// src/pages/RegisterPage.tsx
import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
} from "@mui/material";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      // Llamamos al endpoint de registro en el backend
      const resp = await axios.post(`${baseURL}/api/register/`, {
        username,
        email,
        password,
      });
      setMessage("Usuario registrado correctamente");
    } catch (err: any) {
      // Capturamos un posible error (422, 400, etc.)
      setError(err?.response?.data?.detail || "Error desconocido al registrar");
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Registro de Usuario
      </Typography>

      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: "flex", flexDirection: "column", gap: 2 }}
      >
        <TextField
          label="Nombre de Usuario"
          variant="outlined"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <TextField
          label="Correo Electrónico"
          type="email"
          variant="outlined"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <TextField
          label="Contraseña"
          type="password"
          variant="outlined"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button variant="contained" color="primary" type="submit">
          Registrarse
        </Button>
      </Box>
    </Container>
  );
};

export default RegisterPage;
