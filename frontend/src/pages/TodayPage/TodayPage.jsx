import { useEffect, useState } from "react";
import api from "../../api/client";
import LevelBar from "../../components/LevelBar/LevelBar";
import "./TodayPage.css";

export default function TodayPage() {
  const [habits, setHabits] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [habitsData, statsData] = await Promise.all([
        api.get("/completions/today"),
        api.get("/stats"),
      ]);
      setHabits(habitsData);
      setStats(statsData);
    } catch (err) {
      console.error("Ошибка загрузки:", err);
    } finally {
      setLoading(false);
    }
  }

  async function toggleHabit(habitId, isCompleted) {
    try {
      if (isCompleted) {
        await api.delete(`/completions/${habitId}`);
      } else {
        await api.post(`/completions/${habitId}`);
      }
      await loadData();
    } catch (err) {
      console.error("Ошибка:", err);
    }
  }

  if (loading) return <p>Загрузка...</p>;

  const completedCount = habits.filter((h) => h.is_completed_today).length;

  return (
    <div>
      <LevelBar stats={stats} />

      <div className="today-layout">
        <section className="today-habits">
          <h2>Today's Habits</h2>
          {habits.length === 0 ? (
            <p className="empty-state">
              У тебя пока что нет привычек. Перейди в Manage Habits чтобы
              добавить!
            </p>
          ) : (
            habits.map((habit) => (
              <div
                key={habit.id}
                className={`habit-card ${habit.is_completed_today ? "completed" : ""}`}
                onClick={() => toggleHabit(habit.id, habit.is_completed_today)}
              >
                <div
                  className={`habit-checkbox ${habit.is_completed_today ? "checked" : ""} `}
                >
                  {habit.is_completed_today && "✓"}
                </div>

                <div className="habit-info">
                  <div className="habit-name">
                    {habit.icon} {habit.name}
                  </div>
                  <div className="habit-meta">
                    <span className="habit-xp">
                      +
                      {habit.is_completed_today
                        ? habit.xp_today
                        : habit.base_xp}{" "}
                      XP
                    </span>
                    <span className="habit-streak">
                      🔥 {habit.current_streak}d
                    </span>
                    {habit.multiplier > 1 && (
                      <span className="habit-multiplier">
                        ×{habit.multiplier}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </section>

        {stats && (
          <aside className="quick-stats">
            <h3>Quick Stats</h3>
            <div className="quick-stats-grid">
              <div className="quick-stat-card">
                <span className="quick-stat-icon">🎯</span>
                <div className="quick-stat-value">{stats.completed_today}</div>
                <div className="quick-stat-label">Completed Today</div>
              </div>
              <div className="quick-stat-card">
                <span className="quick-stat-icon">🔥</span>
                <div className="quick-stat-value">{stats.longest_streak}d</div>
                <div className="quick-stat-label">Longest Streak</div>
              </div>
              <div className="quick-stat-card">
                <span className="quick-stat-icon">⚡</span>
                <div className="quick-stat-value">{stats.total_xp}</div>
                <div className="quick-stat-label">Total XP</div>
              </div>
              <div className="quick-stat-card">
                <span className="quick-stat-icon">🔁</span>
                <div className="quick-stat-value">
                  {stats.total_streak_days}d
                </div>
                <div className="quick-stat-label">Total Streaks</div>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
