import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";

function VideoEditRow({ video, projectId, onEdit, onDownload }) {
  const [crop, setCrop] = useState(video.crop_aspect === "9:16");
  const [silence, setSilence] = useState(video.remove_silence || false);
  const [captions, setCaptions] = useState(video.add_captions ?? true);
  const [trimStart, setTrimStart] = useState(video.trim_start ?? null);
  const [trimEnd, setTrimEnd] = useState(video.trim_end ?? null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const videoRef = useRef(null);

  // Revoke the blob URL when this row unmounts, so we don't leak memory.
  useEffect(() => {
    return () => {
      if (previewUrl) window.URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  async function loadPreview() {
    if (previewUrl) return; // already fetched, don't re-download
    setLoadingPreview(true);
    try {
      const res = await api.get(
        `/projects/${projectId}/videos/${video.id}/source`,
        { responseType: "blob" }
      );
      setPreviewUrl(window.URL.createObjectURL(new Blob([res.data])));
    } finally {
      setLoadingPreview(false);
    }
  }

  function handleSetStart() {
    if (videoRef.current) setTrimStart(videoRef.current.currentTime);
  }

  function handleSetEnd() {
    if (videoRef.current) setTrimEnd(videoRef.current.currentTime);
  }

  return (
    <div>
      {!previewUrl ? (
        <button className="btn btn-secondary" onClick={loadPreview} disabled={loadingPreview} style={{ marginBottom: 10 }}>
          {loadingPreview ? "Loading preview..." : "Preview & Trim"}
        </button>
      ) : (
        <div style={{ marginBottom: 12 }}>
          <video ref={videoRef} src={previewUrl} controls style={{ width: "100%", borderRadius: 8 }} />
          <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center", fontSize: 13 }}>
            <button className="btn btn-secondary" onClick={handleSetStart}>Set Start</button>
            <button className="btn btn-secondary" onClick={handleSetEnd}>Set End</button>
            <span style={{ color: "var(--text-secondary)" }}>
              Start: {trimStart !== null ? trimStart.toFixed(1) + "s" : "—"}
              {"  "}End: {trimEnd !== null ? trimEnd.toFixed(1) + "s" : "—"}
            </span>
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 16, fontSize: 14 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input type="checkbox" checked={crop} onChange={(e) => setCrop(e.target.checked)} />
            Crop to 9:16
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input type="checkbox" checked={silence} onChange={(e) => setSilence(e.target.checked)} />
            Remove silence
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input type="checkbox" checked={captions} onChange={(e) => setCaptions(e.target.checked)} />
            Add captions
          </label>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className="btn btn-secondary"
            onClick={() => onEdit(video.id, crop ? "9:16" : null, silence, trimStart, trimEnd, captions)}
          >
            Apply Edits
          </button>
          {video.status === "done" && (
            <button className="btn btn-primary" onClick={() => onDownload(video.id, video.title)}>Download</button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ProjectDetail() {
  const { projectId } = useParams();
  const [videos, setVideos] = useState([]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadVideos() {
    const res = await api.get(`/projects/${projectId}/videos`);
    setVideos(res.data);
  }

  useEffect(() => { loadVideos(); }, [projectId]);

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
    formData.append("background_video", file);
    try {
      await api.post(`/projects/${projectId}/videos`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTitle(""); setFile(null);
      loadVideos();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDownload(videoId, videoTitle) {
    const res = await api.get(`/projects/${projectId}/videos/${videoId}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${videoTitle}.mp4`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  async function handleEdit(videoId, cropAspect, removeSilence, trimStart, trimEnd, addCaptions) {
    await api.patch(`/projects/${projectId}/videos/${videoId}/edit`, {
      crop_aspect: cropAspect,
      remove_silence: removeSilence,
      trim_start: trimStart,
      trim_end: trimEnd,
      add_captions: addCaptions,
    });
    loadVideos();
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "48px 24px" }}>
      <Link to="/projects" style={{ color: "var(--text-secondary)", fontSize: 14, textDecoration: "none" }}>&larr; Back to Projects</Link>
      <h1 style={{ fontSize: 24, margin: "16px 0 24px" }}>Videos</h1>

      <form onSubmit={handleCreate} className="card" style={{ padding: 20, marginBottom: 28 }}>
        <input className="input" placeholder="Video title" value={title}
          onChange={(e) => setTitle(e.target.value)} required />
        <input className="input" type="file" accept="video/*"
          onChange={(e) => setFile(e.target.files[0])} required />
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? "Uploading..." : "Upload Video"}
        </button>
      </form>
      {error && <p style={{ color: "var(--danger)", fontSize: 13, marginBottom: 16 }}>{error}</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {videos.map((v) => (
          <div key={v.id} className="card" style={{ padding: "16px 20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <div style={{ fontWeight: 500 }}>{v.title}</div>
              <span className={`pill pill-${v.status}`}>{v.status}</span>
            </div>
            {v.status === "failed" && <p style={{ color: "var(--danger)", fontSize: 12, marginBottom: 8 }}>{v.error_message}</p>}
            <VideoEditRow video={v} projectId={projectId} onEdit={handleEdit} onDownload={handleDownload} />
          </div>
        ))}
        {videos.length === 0 && <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>No videos yet — upload one above.</p>}
      </div>
    </div>
  );
}