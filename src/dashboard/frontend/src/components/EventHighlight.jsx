import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";
import Filters from "./Filters";

const API_BASE = "http://127.0.0.1:8000/api";

function EventHighlight() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE}/change_points`)
      .then(res => {
        const formatted = res.data.map(e => ({
          ...e,
          MeanBefore: Number(e.MeanBefore),
          MeanAfter: Number(e.MeanAfter),
          StdDev: Number(e.StdDev)
        }));
        setEvents(formatted);
        setFilteredEvents(formatted); // initialize filtered
      })
      .catch(err => console.error("API error:", err));
  }, []);

  const handleFilter = ({ startDate, endDate }) => {
    let filtered = events;
    if (startDate) filtered = filtered.filter(e => e.Date >= startDate);
    if (endDate) filtered = filtered.filter(e => e.Date <= endDate);
    setFilteredEvents(filtered);
  };

  if (events.length === 0) {
    return <div>Loading event data...</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Event Highlights (Change Points)</h1>

      {/* Filters */}
      <Filters onFilter={handleFilter} />

      {/* Chart */}
      <div style={{ width: "100%", height: 350 }}>
        <ResponsiveContainer>
          <LineChart data={filteredEvents}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip 
              formatter={(value) => value.toFixed(5)}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="MeanBefore"
              name="Mean Before Change"
              strokeWidth={2}
              stroke="#8884d8"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="MeanAfter"
              name="Mean After Change"
              strokeWidth={2}
              stroke="#82ca9d"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Event Table */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3">Detected Structural Breaks</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">Date</th>
                <th className="p-2 border">Mean Before</th>
                <th className="p-2 border">Mean After</th>
                <th className="p-2 border">Std Dev</th>
                <th className="p-2 border">Impact</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((e, i) => {
                const impact = ((e.MeanAfter - e.MeanBefore) * 100).toFixed(2);
                return (
                  <tr key={i} className="text-center">
                    <td className="p-2 border">{e.Date}</td>
                    <td className="p-2 border">{e.MeanBefore.toFixed(5)}</td>
                    <td className="p-2 border">{e.MeanAfter.toFixed(5)}</td>
                    <td className="p-2 border">{e.StdDev.toFixed(5)}</td>
                    <td className="p-2 border font-semibold">{impact}% shift</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default EventHighlight;
