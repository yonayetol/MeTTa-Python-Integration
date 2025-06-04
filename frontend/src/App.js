import { useState } from "react";
import "./styles.css";

export default function App() {
  const [chromosome, setChromosome] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setSummary("");

    try {
      const response = await fetch("http://localhost:5000/summarize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ term: chromosome }),
      });

      const data = await response.json();
      setSummary(`🧬 Summary for ${data.chromosome}:\n\n${data.summary}`);
    } catch (error) {
      console.error("Error:", error);
      setSummary("❌ Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <div className="card shadow card-container">
        <div className="card-body">
          <h3 className="card-title mb-4 text-center">🧬 Gene Summarizer 🧠</h3>

          <div className="mb-3">
            <label className="form-label">Enter Chromosome</label>
            <input
              type="text"
              className="form-control"
              value={chromosome}
              onChange={(e) => setChromosome(e.target.value)}
              placeholder="e.g. chr21"
            />
          </div>

          <button className="btn btn-primary w-100" onClick={handleSubmit} disabled={loading}>
            {loading ? "Processing..." : "Summarize"}
          </button>

          {loading && (
            <div className="d-flex justify-content-center mt-3">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}

          {summary && !loading && (
            <div className="mt-4">
              <label className="form-label">Summary:</label>
              <div className="summary-box">
                <pre>{summary}</pre>
              </div>
              <button
                className="btn btn-success mt-3"
                onClick={() => alert("✅ Saved to server-side file automatically.")}
              >
                Save this to file
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
