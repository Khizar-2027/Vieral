import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const [videos, setVideos] = useState([]);
  const [title, setTitle] = useState("");
  const [scriptText, setScriptText] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadVideos() {
    const res = await api.get(`/projects/${projectId}/videos`);
    setVideos(res.data);
  }

  useEffect(() => {
    loadVideos();
  }, [projectId]);

  // Poll for status updates every 3 seconds while any video is still processing
  useEffect(() => {
    const hasProcessing = videos.some((v) => v.status === "processing");
    if (!hasProcessing) return;

    const interval = setInterval(loadVideos, 3000);
    return () => clearInterval(interval);
  }, [videos, projectId]);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const formData = new FormData();
    formData.append("title", title);
    formData.append("script_text", scriptText);
    formData.append("background_video", file);

    try {
      await api.post(`/projects/${projectId}/videos`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTitle("");
      setScriptText("");
      setFile(null);
      loadVideos();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

    async function handleDownload(videoId, title) {
    const res = await api.get(`/projects/${projectId}/videos/${videoId}/download`, {
        responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${title}.mp4`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto" }}>
      <Link to="/projects">&larr; Back to Projects</Link>
      <h2>Videos</h2>

      <form onSubmit={handleCreate}>
        <input
          placeholder="Video title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <br />
        <textarea
          placeholder="Script text"
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          rows={4}
          style={{ width: "100%" }}
          required
        />
        <br />
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <br />
        <button type="submit" disabled={submitting}>
          {submitting ? "Uploading..." : "Create Video"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}

        <ul>
        {videos.map((v) => (
            <li key={v.id} style={{ marginBottom: 10 }}>
            <strong>{v.title}</strong> — {v.status}

            {v.status === "done" && (
            <>
                {" "}
                <button onClick={() => handleDownload(v.id, v.title)}>Download</button>
            </>
            )}

            {v.status === "failed" && (
                <span style={{ color: "red" }}> — {v.error_message}</span>
            )}
            </li>
        ))}
        </ul>
    </div>
  );
}