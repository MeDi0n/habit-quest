import "./LevelBar.css";
export default function LevelBar({ stats }) {
  if (!stats) return null;

  const progress =
    stats.xp_for_next_level > 0
      ? (stats.xp_in_current_level / stats.xp_for_next_level) * 100
      : 0;

  const completed = stats.completed_today || 0;
  const total = stats.total_habits || 0;
  const circleProgress = total > 0 ? completed / total : 0;

  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - circleProgress);

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
      <div className="level-circle-wrapper">
        <svg width="56" height="56" viewBox="0 0 56 56">
          <circle cx="28" cy="28" r={radius} className="circle-bg" />
          <circle
            cx="28"
            cy="28"
            r={radius}
            className="circle-progress"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 28 28)"
          />
        </svg>
        <span
          className={`level-circle-text ${completed === total && total > 0 ? "complete" : ""}`}
        >
          {completed}/{total}
        </span>
      </div>
    </div>
  );
}
