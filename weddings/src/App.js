import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from "./pages/Login";
import { Uploader } from './pages/Uploader';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={ <Login/> }/>
        <Route path="/" element={ <Uploader/> }/>
      </Routes>
    </Router>
  );
}

export default App;
