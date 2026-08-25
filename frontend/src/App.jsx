import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Visitors from "./pages/Visitors";
import VisitorDetail from "./pages/VisitorDetail";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="page-container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/visitors" element={<Visitors />} />
          <Route path="/visitors/:visitorId" element={<VisitorDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
