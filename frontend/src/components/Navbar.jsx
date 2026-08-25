import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">Clickstream Insights</div>
      <div className="navbar-links">
        <NavLink
          to="/"
          end
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/visitors"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Visitors
        </NavLink>
      </div>
    </nav>
  );
}
