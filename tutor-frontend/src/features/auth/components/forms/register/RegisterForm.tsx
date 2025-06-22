import { useState }       from "react";
import { useNavigate }    from "react-router-dom";
import { api }            from "@services/api/backend";
import styles             from "./RegisterForm.module.css";

interface Props {
  endpointUrl?: string;
}

const RegisterForm = ({ endpointUrl = "/api/auth/register" }: Props) => {
  const [name,  setName]  = useState("");
  const [email, setEmail] = useState("");
  const [pwd,   setPwd]   = useState("");
  const [pwd2,  setPwd2]  = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (pwd !== pwd2)  { alert("Las contraseñas no coinciden"); return; }
    if (!agreed)       { alert("Debes aceptar los términos");  return; }

    try {
      setLoading(true);
      await api.post(endpointUrl, {
        username: name,
        email,
        password: pwd,
        confirmPassword: pwd2,
      });
      navigate("/login", { replace: true });
    } catch (err) {
      console.error("Register error:", err);
      alert("Error en el registro");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <h1 className={styles.title}>Crear cuenta</h1>

      <input
        className={styles.input}
        type="text"
        placeholder="Nombre"
        autoComplete="name"
        value={name}
        onChange={e => setName(e.target.value)}
        required
      />

      <input
        className={styles.input}
        type="email"
        placeholder="Correo electrónico"
        autoComplete="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />

      <input
        className={styles.input}
        type="password"
        placeholder="Contraseña"
        autoComplete="new-password"
        value={pwd}
        onChange={e => setPwd(e.target.value)}
        required
      />

      <input
        className={styles.input}
        type="password"
        placeholder="Repite la contraseña"
        autoComplete="new-password"
        value={pwd2}
        onChange={e => setPwd2(e.target.value)}
        required
      />

      <label className={styles.checkbox}>
        <input
          type="checkbox"
          checked={agreed}
          onChange={e => setAgreed(e.target.checked)}
        />
        <span className={styles.fakeBox} />
        Acepto los&nbsp;
        <a href="/legal/terms" target="_blank" rel="noopener noreferrer">
          Términos y condiciones
        </a>
      </label>

      <button className={styles.submit} type="submit" disabled={loading}>
        {loading ? "Registrando…" : "Registrarse"}
      </button>
    </form>
  );
};

export default RegisterForm;
