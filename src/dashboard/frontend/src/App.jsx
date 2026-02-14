import { useState } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import PriceChart from './components/PriceChart'
import EventHighlight from './components/EventHighlight'
import HomePage from './components/Home'
function App() {
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pricechart" element={<PriceChart />} />
        <Route path="/eventhighlight" element={<EventHighlight />} />
      </Routes>
    </Router>
  )
}

export default App
