import { useEffect, useState } from "react";
import api from "../../api/client";
import LevelBar from "../../components/LevelBar/LevelBar";
import "./ProfilePage.css";
const EVOLUTION = [
  { emoji: "🥚", name: "Egg" },
  { emoji: "🐣", name: "Hatchling" },
  { emoji: "🐥", name: "Chick" },
  { emoji: "🐤", name: "Fledgling" },
  { emoji: "💚", name: "Sprout" },
  { emoji: "💛", name: "Bloom" },
  { emoji: "🦋", name: "Butterfly" },
  { emoji: "🐉", name: "Phoenix" },
  { emoji: "👑", name: "Star" },
  { emoji: "⭐", name: "Legend" },
];

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [profileData, statsData] = await Promise.all([
          api.get("/profile"),
          api.get("/stats"),
        ]);
        setProfile(profileData);
        setStats(statsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <p>Загрузка...</p>;
  if (!profile) return <p>Нет данных</p>;

  const stage = Math.min(profile.character_stage, 9);
  const progress =
    profile.xp_for_next_level > 0
      ? (profile.xp_in_current_level / profile.xp_for_next_level) * 100
      : 0;

  return (
    <div>
      <LevelBar stats={stats} />
      <h2>Profile</h2>

      <div className="profile-card">
        <div className="profile-character">{EVOLUTION[stage].emoji}</div>
        <span className="character-level">Lv.{profile.level}</span>

        <h3 className="profile-level-name">Level {profile.level}</h3>
        <p className="profile-xp">{profile.total_xp} total XP earned</p>

        <div className="profile-progress">
          <div className="profile-progress-header">
            <span>Level {profile.level}</span>
            <span>
              {profile.xp_in_current_level} / {profile.xp_for_next_level} XP
            </span>
          </div>
          <div className="profile-progress-track">
            <div
              className="profile-progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          <p className="evolution-label">
            Your character evolves as you level up!
          </p>
          <div className="evolution-stages">
            {EVOLUTION.map((evo, i) => (
              <span
                key={i}
                className={`evolution-item ${i <= stage ? "unlocked" : "locked"}`}
              >
                {evo.emoji}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
