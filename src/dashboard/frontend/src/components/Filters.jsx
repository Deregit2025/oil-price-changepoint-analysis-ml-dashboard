import React, { useState } from "react";

function Filters({ onFilter }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const handleApply = () => {
    onFilter({ startDate, endDate });
  };

  const handleReset = () => {
    setStartDate("");
    setEndDate("");
    onFilter({ startDate: "", endDate: "" });
  };

  return (
    <div className="flex flex-col md:flex-row items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg shadow-sm">
      <div className="flex flex-col">
        <label className="text-gray-700 font-medium mb-1">Start Date:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="border border-gray-300 rounded-md p-2"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-gray-700 font-medium mb-1">End Date:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="border border-gray-300 rounded-md p-2"
        />
      </div>
      <div className="flex gap-2 mt-2 md:mt-0">
        <button
          onClick={handleApply}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-md"
        >
          Apply
        </button>
        <button
          onClick={handleReset}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-md"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

export default Filters;
