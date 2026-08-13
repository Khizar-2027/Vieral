import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Auth() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (mode === "register") await register(email, password);
      await login(email, password);
      navigate("/projects");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="card" style={{ width: 360, padding: 32 }}>
        <h2 style={{ marginBottom: 4 }}>{mode === "login" ? "Welcome back" : "Create an account"}</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24 }}>
          {mode === "login" ? "Log in to your projects" : "Start editing your shorts"}
        </p>
        <form onSubmit={handleSubmit}>
          <input className="input" type="email" placeholder="Email" value={email}
            onChange={(e) => setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="Password" value={password}
            onChange={(e) => setPassword(e.target.value)} required />
          <button className="btn btn-primary" style={{ width: "100%" }} type="submit">
            {mode === "login" ? "Log In" : "Register"}
          </button>
        </form>
        {error && <p style={{ color: "var(--danger)", fontSize: 13, marginTop: 12 }}>{error}</p>}
        <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 20, textAlign: "center" }}>
          {mode === "login" ? "New here? " : "Already have an account? "}
          <span style={{ color: "var(--accent)", cursor: "pointer" }}
            onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "Register" : "Log in"}
          </span>
        </p>
      </div>
    </div>
  );
}