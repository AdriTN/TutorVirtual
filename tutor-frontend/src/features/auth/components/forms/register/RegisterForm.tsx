import { useState }       from "react";
import { Link, useNavigate }    from "react-router-dom";
import { api }            from "@services/api/backend";
import { useNotifications } from "@hooks/useNotifications";
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
  const { notifyError, notifySuccess } = useNotifications();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (pwd !== pwd2)  { 
      notifyError("Las contraseñas no coinciden"); 
      return; 
    }
    if (!agreed)       { 
      notifyError("Debes aceptar los términos y condiciones");  
      return; 
    }

    try {
      setLoading(true);
      try {
        await api.post(endpointUrl, {
          username: name,
          email,
          password: pwd,
          confirm_password: pwd2,
        });
        notifySuccess("¡Registro exitoso! Ahora puedes iniciar sesión.");
        navigate("/login", { replace: true });
      } catch (error) {
        setLoading(false);
        if ((error as any)?.response?.status === 422) {
          const errorDetails = (error as any)?.response?.data?.detail;
          if (errorDetails && errorDetails.length > 0) {
            notifyError(errorDetails[0].msg); 
          } else {
            notifyError("Error de validación. Revisa los datos.");
          }
        } else {
          notifyError("Error inesperado en el registro.");
        }
        if (error instanceof Error) {
          console.error("Error en registro:", (error as any)?.response || error.message);
        } else {
          console.error("Error en registro:", error);
        }
      }
      notifySuccess("¡Registro exitoso! Ahora puedes iniciar sesión.");
      navigate("/login", { replace: true });
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

        <div className={styles.agreementWrapper}>
          <label className={styles.checkboxContainer}>
            <input type="checkbox" defaultChecked={false} onChange={(e) => setAgreed(e.target.checked)}/>
            <div className={styles.checkmark} />
            <span className={styles.checkboxLabel}>
              Estoy de acuerdo con <a href="#">Terminos y Condiciones</a>
            </span>
          </label>
        </div>

      <button className={styles.submit} type="submit" disabled={loading}>
        {loading ? "Registrando…" : "Registrarse"}
      </button>
      
      <div className={styles.haveAccount}>
        <Link to="/login">Ya tengo cuenta</Link>
      </div>
    </form>
  );
};

export default RegisterForm;
