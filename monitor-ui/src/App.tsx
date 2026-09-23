import { useEffect, useState } from "react";
import "./App.css";

const API = "http://localhost:8787/api/stats";

interface TokenTotals {
  input: number;
  output: number;
}

interface Mismatch {
  file: string;
  description: string;
  claim: string;
}

interface Stats {
  today: string | null;
  tokens: TokenTotals;
  blocked: string[];
  mismatches: Mismatch[];
}

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const poll = () => {
      fetch(API)
        .then((res) => res.json())
        .then(setStats)
        .catch(() => setError("Can't reach the backend — is server.py running?"));
    };
    poll();
    const id = setInterval(poll, 3000);
    return () => clearInterval(id);
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!stats) return <p>Loading…</p>;

  return (
    <div className="dashboard">
      <h1>Agent Monitor</h1>
      <p className="subtitle">Refreshes every 3s · {stats.today ?? "no sessions yet"}</p>

      <div className="tile">
        <span className="label">Tokens today</span>
        <span className="value">{stats.tokens.input} in / {stats.tokens.output} out</span>
      </div>

      <div className="panel">
        <h2>Blocked commands</h2>
        {stats.blocked.length === 0 ? (
          <p className="empty">Nothing blocked yet.</p>
        ) : (
          <ul>{stats.blocked.map((line, i) => <li key={i}>{line}</li>)}</ul>
        )}
      </div>

      <div className="panel">
        <h2>Subagent mismatches</h2>
        {stats.mismatches.length === 0 ? (
          <p className="empty">No flagged claims.</p>
        ) : (
          <ul>{stats.mismatches.map((m, i) => (
            <li key={i}><b>{m.description}</b> — {m.claim}</li>
          ))}</ul>
        )}
      </div>
    </div>
  );
}