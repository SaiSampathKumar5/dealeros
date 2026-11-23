import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000/api/disagreements/";
const REASONS = ["MISSING_IN_B", "ORPHAN_IN_B", "DUPLICATE_IN_B", "VALUE_MISMATCH",
  "LOCATION_MISMATCH", "DATE_MISMATCH", "VOIDED_IN_B"];

export default function App() {
  const [org, setOrg] = useState("ORG-A");
  const [reason, setReason] = useState("");
  const [sort, setSort] = useState(""); // "", "value", "-value"
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams({ org });
    if (reason) params.set("reason", reason);
    if (sort) params.set("sort", sort);
    fetch(`${API}?${params}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((data) => { setRows(data); setError(""); })
      .catch((e) => { setRows([]); setError(e.message); });
  }, [org, reason, sort]);

  const cycleSort = () => setSort(sort === "" ? "value" : sort === "value" ? "-value" : "");
  const arrow = sort === "value" ? " ▲" : sort === "-value" ? " ▼" : "";
  const cell = (v) => (v === null || v === undefined ? "" : v); // empty, never 0 or "null"

  return (
    <div style={{ fontFamily: "sans-serif", padding: 16 }}>
      <h2>A vs B disagreements</h2>
      <label>Org: <select value={org} onChange={(e) => setOrg(e.target.value)}>
        <option>ORG-A</option><option>ORG-B</option></select></label>{" "}
      <label>Reason: <select value={reason} onChange={(e) => setReason(e.target.value)}>
        <option value="">All</option>{REASONS.map((r) => <option key={r}>{r}</option>)}</select></label>
      {error && <p style={{ color: "crimson" }}>Could not load: {error}</p>}
      {!error && rows.length === 0 && <p>No disagreements for this selection.</p>}
      {rows.length > 0 && (
        <table border="1" cellPadding="6" style={{ borderCollapse: "collapse", marginTop: 12 }}>
          <thead><tr>
            <th>Reason</th><th>Record ID</th><th>Location</th><th>System A value</th>
            <th onClick={cycleSort} style={{ cursor: "pointer" }}>System B value{arrow}</th>
            <th>Difference</th></tr></thead>
          <tbody>{rows.map((r, i) => (
            <tr key={r.reason + r.record_id + i}>
              <td>{r.reason}</td><td>{r.record_id}</td>
              <td>{r.location}{r.cross_org ? " (B side in another org: hidden)" : ""}</td>
              <td>{cell(r.a_value)}</td><td>{cell(r.b_value)}</td><td>{cell(r.difference)}</td>
            </tr>))}</tbody>
        </table>)}
    </div>
  );
}
