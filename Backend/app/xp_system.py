# ============================================================
# xp_system.py — Система опыта и уровней
# ============================================================
# Здесь вся игровая математика:
#
# 1. STREAK MULTIPLIER (множитель за серию дней подряд):
#    - 1 день: ×1.0 (без бонуса)
#    - 3 дня: ×1.3
#    - 6 дней: ×1.6
#    - 10 дней: ×2.0 (максимум)
#    Формула: 1.0 + (streak - 1) * 0.1, но не больше 2.0
#
# 2. XP ЗА ВЫПОЛНЕНИЕ:
#    earned_xp = base_xp × multiplier (округлённо)
#    Пример: base_xp=30, streak=6 → 30 × 1.5 = 45 XP
#
# 3. УРОВНИ:
#    Каждый следующий уровень требует больше XP.
#    Level 1:   0 XP
#    Level 2:  50 XP  (нужно 50)
#    Level 3: 150 XP  (нужно 100)
#    Level 4: 300 XP  (нужно 150)
#    Level 5: 500 XP  (нужно 200)
#    ...
#    Формула порога: threshold(n) = 25 × n × (n - 1)
# ============================================================


# Названия уровней — для красоты в UI
LEVEL_NAMES = {
    1: "Egg",           # 🥚 Яйцо
    2: "Hatchling",     # 🐣 Птенец
    3: "Chick",         # 🐥 Цыплёнок
    4: "Fledgling",     # 🐤 Оперившийся
    5: "Sprout",        # 💚 Росток
    6: "Bloom",         # 💛 Цветок
    7: "Butterfly",     # 🦋 Бабочка
    8: "Phoenix",       # 🐉 Дракон
    9: "Star",          # 👑 Корона
    10: "Legend",       # ⭐ Легенда
}


def get_streak_multiplier(streak_days: int) -> float:
    """
    Вычисляет множитель XP на основе количества дней подряд.

    Аргументы:
        streak_days: сколько дней подряд выполнялась привычка

    Возвращает:
        float: множитель от 1.0 до 2.0

    Примеры:
        >>> get_streak_multiplier(1)
        1.0
        >>> get_streak_multiplier(4)
        1.3
        >>> get_streak_multiplier(15)
        2.0
    """
    if streak_days <= 1:
        return 1.0
    multiplier = 1.0 + (streak_days - 1) * 0.1
    return min(multiplier, 2.0)  # min() — чтобы не превышать 2.0


def calculate_xp(base_xp: int, streak_days: int) -> tuple[int, float]:
    """
    Считает сколько XP получит пользователь.

    Возвращает кортеж (earned_xp, multiplier).

    Пример:
        >>> calculate_xp(30, 6)
        (45, 1.5)
    """
    multiplier = get_streak_multiplier(streak_days)
    earned_xp = round(base_xp * multiplier)
    return earned_xp, multiplier


def get_level_threshold(level: int) -> int:
    """
    Сколько ВСЕГО XP нужно чтобы достичь этого уровня.

    Level 1: 0, Level 2: 50, Level 3: 150, Level 4: 300, ...
    Формула: 25 * level * (level - 1)
    """
    return 25 * level * (level - 1)


def get_level_from_xp(total_xp: int) -> int:
    """
    Определяет уровень пользователя по его общему XP.

    Идёт от уровня 1 вверх, пока XP хватает.
    """
    level = 1
    while get_level_threshold(level + 1) <= total_xp:
        level += 1
    return level


def get_level_progress(total_xp: int) -> dict:
    """
    Возвращает полную информацию об уровне.

    Пример для total_xp=236:
        {
            "level": 3,
            "level_name": "Chick",
            "xp_in_current_level": 86,    # 236 - 150 = 86
            "xp_for_next_level": 150,     # 300 - 150 = 150
            "total_xp": 236,
            "character_stage": 2          # Индекс для массива эволюций (0-9)
        }
    """
    level = get_level_from_xp(total_xp)
    current_threshold = get_level_threshold(level)
    next_threshold = get_level_threshold(level + 1)

    return {
        "level": level,
        "level_name": LEVEL_NAMES.get(level, f"Level {level}"),
        "xp_in_current_level": total_xp - current_threshold,
        "xp_for_next_level": next_threshold - current_threshold,
        "total_xp": total_xp,
        "character_stage": min(level - 1, 9),  # 0-9 для 10 стадий эволюции
    }
