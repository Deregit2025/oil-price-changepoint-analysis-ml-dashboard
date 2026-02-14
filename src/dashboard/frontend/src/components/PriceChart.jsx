import React, { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import Filters from "./Filters";

function PriceChart() {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/historical_prices")
      .then((res) => {
        setData(res.data);
        setFilteredData(res.data);
      })
      .catch((err) => {
        console.error("Error fetching historical prices:", err);
      });
  }, []);

  const handleFilter = ({ startDate, endDate }) => {
    let filtered = data;
    if (startDate) {
      filtered = filtered.filter((d) => d.Date >= startDate);
    }
    if (endDate) {
      filtered = filtered.filter((d) => d.Date <= endDate);
    }
    setFilteredData(filtered);
  };

  if (data.length === 0) {
    return <div>Loading price data...</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Brent Oil Price History</h1>

      {/* Filters */}
      <Filters onFilter={handleFilter} />

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={filteredData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            formatter={(value) => value.toFixed(2)} 
            labelFormatter={(label) => `Date: ${label}`} 
          />
          <Line type="monotone" dataKey="Price" stroke="#8884d8" dot={false} />
        </LineChart>
      </ResponsiveContainer>

      {/* Optional: show number of points */}
      <p className="mt-2 text-gray-600">
        Showing {filteredData.length} records
      </p>
    </div>
  );
}

export default PriceChart;
