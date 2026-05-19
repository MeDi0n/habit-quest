import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Layout.css";
export default function Layout() {
  const { user, logout } = useAuth();

  function navClass({ isActive }) {
    return isActive ? "nav-link active" : "nav-link";
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="sidebar-title">✨ Habit Quest</h1>

        <nav className="sidebar-nav">
          <NavLink to="/today" className={navClass}>
            🏠 Today
          </NavLink>
          <NavLink to="/manage" className={navClass}>
            ⚙️ Manage Habits
          </NavLink>
          <NavLink to="/stats" className={navClass}>
            📊 Statistics
          </NavLink>
          <NavLink to="/profile" className={navClass}>
            👤 Profile
          </NavLink>
        </nav>

        {user && (
          <div className="sidebar-footer">
            <div className="sidebar-level">Lever {user.level}</div>
            <div className="sidebar-xp">{user.total_xp} total XP</div>
            <button onClick={logout} className="logout-btn">
              Выйти
            </button>
          </div>
        )}
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
