import { useEffect, useState } from "react";
import api from "../../api/client";
import LevelBar from "../../components/LevelBar/LevelBar";
import "./ManageHabitsPage.css";
const ICONS = [
  "🏃",
  "📚",
  "💧",
  "🧘",
  "🚫",
  "🏋️",
  "🎨",
  "✍️",
  "🎵",
  "💤",
  "🥗",
  "🎯",
];

export default function ManageHabitsPage() {
  const [habits, setHabits] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const [newName, setNewName] = useState("");
  const [newIcon, setNewIcon] = useState("🎯");
  const [newXp, setNewXp] = useState(20);

  const [stats, setStats] = useState(null);

  async function loadData() {
    try {
      const [habitsData, statsData] = await Promise.all([
        api.get("/habits/"),
        api.get("/stats"),
      ]);
      setHabits(habitsData);
      setStats(statsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await api.post("/habits/", {
        name: newName,
        icon: newIcon,
        base_xp: newXp,
      });
      setNewName("");
      setNewIcon("🎯");
      setNewXp(20);
      setShowForm(false);
      await loadData();
    } catch (err) {
      alert(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Удалить привычку?")) return;
    try {
      await api.delete(`/habits/${id}`);
      await loadData();
    } catch (err) {
      alert(err.message);
    }
  }

  if (loading) return <p>Загрузка...</p>;

  return (
    <div>
      <LevelBar stats={stats} />
      <div className="manage-header">
        <h2>Manage Habits</h2>
        <button className="add-btn" onClick={() => setShowForm(!showForm)}>
          + Add
        </button>
      </div>

      {showForm && (
        <form className="create-form" onSubmit={handleCreate}>
          <h3>New Habit</h3>

          <div className="icon-picker">
            {ICONS.map((icon) => (
              <button
                key={icon}
                type="button"
                className={`icon-option ${newIcon === icon ? "selected" : ""}`}
                onClick={() => setNewIcon(icon)}
              >
                {icon}
              </button>
            ))}
          </div>

          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Habit name..."
            className="create-input"
            required
          />

          <div className="xp-row">
            <label>Base XP: {newXp}</label>
            <input
              type="range"
              min="5"
              max="100"
              step="5"
              value={newXp}
              onChange={(e) => setNewXp(Number(e.target.value))}
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="submit-btn">
              + Add Habit
            </button>
            <button
              type="button"
              className="cancel-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="habits-list">
        {habits.map((habit) => (
          <div key={habit.id} className="manage-habit-card">
            <span className="manage-habit-icon">{habit.icon}</span>
            <div className="manage-habit-info">
              <div className="manage-habit-name">{habit.name}</div>
              <div className="manage-habit-meta">{habit.base_xp} XP</div>
            </div>
            <button
              onClick={() => handleDelete(habit.id)}
              className="delete-btn"
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
