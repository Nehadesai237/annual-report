import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SimpleLogin from './SimpleLogin';

function SimpleApp() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-center mb-8">Annual Report Portal</h1>
          <Routes>
            <Route path="/" element={<SimpleLogin />} />
            <Route path="/login" element={<SimpleLogin />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default SimpleApp;
