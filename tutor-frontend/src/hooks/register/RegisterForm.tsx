import { useState } from "react";

import { registerUser } from "../../services/endpoints/authservice";

export function RegisterForm() {
  // Estados
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Lógica del submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await registerUser(username, email, password);
      setMessage(response.data.message);
      console.log(response.data.message);
    } catch (err: any) {
      if (err.response) {
        setError(err.response.data.message);
        console.log(err.response.data.message);
      } else {
        setError("Error de conexión");
        console.log("Error de conexión");
      }
    }
  };

  return {
    // Estados
    username,
    setUsername,
    email,
    setEmail,
    password,
    setPassword,
    message,
    error,

    // Métodos
    handleSubmit,
  };
}
