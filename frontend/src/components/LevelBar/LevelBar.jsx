import "./LevelBar.css";
export default function LevelBar({ stats }) {
  if (!stats) return null;

  const progress =
    stats.xp_for_next_level > 0
      ? (stats.xp_in_current_level / stats.xp_for_next_level) * 100
      : 0;

  return (
    <div className="level-bar">
      <div className="level-bar-info">
        <span className="level-label">Level {stats.level}</span>
        <span className="level-xp">
          {stats.xp_in_current_level} / {stats.xp_for_next_level} XP
        </span>
      </div>
      <div className="level-progress-track">
        <div
          className="level-progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div
        className={`level-circle ${stats.completed_today === stats.total_habits && stats.total_habits > 0 ? "complete" : ""}`}
      >
        {stats.completed_today}/{stats.total_habits}
      </div>
    </div>
  );
}
