import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from "./pages/Login";
import { Uploader } from './pages/Uploader';
import { Dashboard } from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/j" element={ <Login/> }/>
        <Route path="/uploader" element={ <Uploader/> }/>
        <Route path="/" element={ <Dashboard/> }/>
      </Routes>
    </Router>
  );
}

export default App;