import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5001"; 


function fetchCounts(filter) {
  return axios.get(`${API_BASE}/api/attendance_counts`, { params: { filter } })
    .then(r => r.data);
}

export default function AttendanceDashboard(){
  const [filter, setFilter] = useState("today");
  const [data, setData] = useState([]); // array of {facility_id, date, count}
  const evtRef = useRef(null);

  // useEffect(() => {
  //   // initial load
  //   fetchCounts(filter).then(setData).catch(console.error);

  //   // open SSE
  //   if (evtRef.current) {
  //     evtRef.current.close();
  //   }
  //   const es = new EventSource(`${API_BASE}/api/attendance_stream?filter=${filter}&interval=5`);
  //   evtRef.current = es;
  //   es.onmessage = (e) => {
  //     try {
  //       const payload = JSON.parse(e.data);
  //       setData(payload);
  //     } catch(err) {
  //       console.error("SSE parse error", err);
  //     }
  //   };
  //   es.onerror = (err) => {
  //     console.error("EventSource error", err);
  //     // optionally try reconnect logic here
  //   };

  //   return () => {
  //     if (es) es.close();
  //   };
  // }, [filter]);

  useEffect(() => {
  // Initial fetch
  fetchCounts(filter)
    .then(setData)
    .catch(err => console.error("API fetch error:", err));

  // SSE (if your backend supports streaming)
  if (evtRef.current) {
    evtRef.current.close();
  }

  const es = new EventSource(`${API_BASE}/api/attendance_stream?filter=${filter}&interval=5`);
  evtRef.current = es;

  es.onmessage = (e) => {
    try {
      const payload = JSON.parse(e.data);
      setData(payload);
    } catch (err) {
      console.error("SSE parse error:", err);
    }
  };

  es.onerror = (err) => {
    console.error("EventSource error:", err);
  };

  return () => {
    if (es) es.close();
  };
}, [filter]);


  // convert data for chart: example—one line per facility (small demo)
  // We'll create a series for one facility or aggregated counts:
  const grouped = data.reduce((acc, r) => {
    const k = r.facility_id;
    if (!acc[k]) acc[k] = [];
    acc[k].push({ date: r.date, count: r.count });
    return acc;
  }, {});

  // For demo we'll flatten for a single facility if available
  const firstFacility = Object.keys(grouped)[0];
  const chartData = (firstFacility ? grouped[firstFacility] : []).map(d => ({ date: d.date, count: d.count }));

  return (
    <div style={{ padding: 16 }}>
      <h2>Attendance Dashboard</h2>
      <div>
        <label>Filter:</label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="last_week">Last week</option>
          <option value="last_month">Last month</option>
        </select>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Chart for facility {firstFacility ?? "(none)"}</h3>
        <LineChart width={800} height={300} data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="count" name="Count" />
        </LineChart>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Raw data</h3>
        <table border="1">
          <thead><tr><th>facility_id</th><th>date</th><th>count</th></tr></thead>
          <tbody>
            {data.map((r,i) => <tr key={i}><td>{r.facility_id}</td><td>{r.date}</td><td>{r.count}</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  );
}
