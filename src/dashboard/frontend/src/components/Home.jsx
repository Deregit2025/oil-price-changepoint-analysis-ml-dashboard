import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-r from-purple-200 via-pink-100 to-yellow-100 flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold mb-6 text-gray-800 text-center">
        Welcome to the Brent Oil Analysis Dashboard
      </h1>
      <p className="text-lg mb-10 text-gray-700 text-center max-w-xl">
        Explore historical Brent oil prices and visualize detected change points in an interactive dashboard.
      </p>
      <div className="flex gap-6">
        <button
          onClick={() => navigate("/pricechart")}
          className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-colors duration-300"
        >
          View Price Chart
        </button>
        <button
          onClick={() => navigate("/eventhighlight")}
          className="bg-pink-500 hover:bg-pink-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-colors duration-300"
        >
          View Change Points
        </button>
      </div>
    </div>
  );
}

export default HomePage;
