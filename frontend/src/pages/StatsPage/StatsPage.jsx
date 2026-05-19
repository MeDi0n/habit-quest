import { useEffect, useState } from "react";
import api from "../../api/client";
import LevelBar from "../../components/LevelBar/LevelBar";
import "./StatsPage.css";
export default function StatsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get("/stats");
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <p>Загрузка...</p>;
  if (!stats) return <p>Нет данных</p>;

  const maxStreak = Math.max(...stats.habit_streaks.map((h) => h.streak), 1);

  return (
    <div>
      <LevelBar stats={stats} />
      <h2>Statistics</h2>

      <div className="stats-cards">
        <div className="stats-card">
          <span className="stats-icon">🎯</span>
          <div className="stats-value">{stats.completed_today}</div>
          <div className="stats-label">Completed Today</div>
        </div>
        <div className="stats-card">
          <div className="stats-icon">🔥</div>
          <div className="stats-value">{stats.longest_streak}d</div>
          <div className="stats-label">Longest Streak</div>
        </div>
        <div className="stats-card">
          <span className="stats-icon">⚡</span>
          <div className="stats-value">{stats.total_xp}</div>
          <div className="stats-label">Total XP</div>
        </div>
        <div className="stats-card">
          <span className="stats-icon">🔁 </span>
          <div className="stats-value">{stats.total_streak_days}d</div>
          <div className="stats-label">Total Streaks</div>
        </div>
      </div>

      {stats.habit_streaks.length > 0 && (
        <div className="streaks-section">
          <h3>Habit Streaks</h3>
          {stats.habit_streaks.map((habit) => (
            <div key={habit.id} className="streak-row">
              <span className="streak-icon">{habit.icon}</span>
              <span className="streak-name">{habit.name}</span>
              <div className="streak-bar-track">
                <div
                  className="streak-bar-fill"
                  style={{ width: `${(habit.streak / maxStreak) * 100}%` }}
                />
              </div>
              <span className="streak-days">{habit.streak}d</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
