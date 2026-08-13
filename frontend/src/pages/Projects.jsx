import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { useAuth } from "../AuthContext";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const { logout } = useAuth();

  async function loadProjects() {
    const res = await api.get("/projects");
    setProjects(res.data);
  }

  useEffect(() => { loadProjects(); }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/projects", { name });
      setName("");
      loadProjects();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "48px 24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1 style={{ fontSize: 24 }}>Your Projects</h1>
        <button className="btn btn-secondary" onClick={logout}>Log Out</button>
      </div>

      <form onSubmit={handleCreate} className="card" style={{ padding: 20, display: "flex", gap: 10, marginBottom: 28 }}>
        <input className="input" style={{ marginBottom: 0, flex: 1 }} placeholder="New project name"
          value={name} onChange={(e) => setName(e.target.value)} required />
        <button className="btn btn-primary" type="submit">Create</button>
      </form>
      {error && <p style={{ color: "var(--danger)", fontSize: 13, marginBottom: 16 }}>{error}</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <div className="card" style={{ padding: "16px 20px", fontWeight: 500 }}>
              {p.name}
            </div>
          </Link>
        ))}
        {projects.length === 0 && (
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>No projects yet — create one above.</p>
        )}
      </div>
    </div>
  );
}