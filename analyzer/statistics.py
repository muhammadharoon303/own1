"""
Statistical & Frequency Distribution Analyzer for 92pkr / Big-Small game.
Analyzes hot/cold numbers, Big/Small ratios, color distributions, and overdue numbers.
"""
from typing import List, Dict, Any
from collections import Counter


class StatisticsAnalyzer:
    def __init__(self):
        pass

    def analyze(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        history: chronological list of records (oldest -> newest).
        """
        if not history:
            return {
                "signal": "Neutral",
                "confidence": 50.0,
                "big_count": 0,
                "small_count": 0,
                "big_percent": 50.0,
                "small_percent": 50.0,
                "hot_numbers": [],
                "cold_numbers": [],
                "overdue_numbers": [],
                "color_stats": {},
                "explanation": "No records available for statistical analysis."
            }

        total = len(history)
        sizes = [h["size"].capitalize() for h in history if h.get("size")]
        numbers = [int(h["number"]) for h in history if h.get("number") is not None and str(h["number"]).isdigit()]
        colors = [h["color"].capitalize() for h in history if h.get("color")]

        # Big / Small counts
        big_count = sizes.count("Big")
        small_count = sizes.count("Small")
        big_pct = round((big_count / len(sizes) * 100), 1) if sizes else 50.0
        small_pct = round((small_count / len(sizes) * 100), 1) if sizes else 50.0

        # Recent window statistics (last 20 periods)
        recent_window = sizes[-20:] if len(sizes) >= 20 else sizes
        rec_big = recent_window.count("Big")
        rec_small = recent_window.count("Small")
        rec_total = len(recent_window)
        rec_big_pct = round((rec_big / rec_total * 100), 1) if rec_total else 50.0

        # Mean reversion calculation:
        # In a balanced game, Big and Small each tend toward 50%.
        # If in the last 20 periods Big is <= 35%, there is significant mean-reversion pull towards Big.
        stat_signal = "Neutral"
        stat_conf = 50.0
        stat_reason = "Big and Small distribution is well balanced near 50%."

        if rec_big_pct <= 35.0:
            stat_signal = "Big"
            stat_conf = min(78.0, 50.0 + (50.0 - rec_big_pct) * 1.2)
            stat_reason = f"Big is statistically oversold (only {rec_big_pct}% in last {rec_total} draws). Mean reversion favors BIG."
        elif rec_big_pct >= 65.0:
            stat_signal = "Small"
            stat_conf = min(78.0, 50.0 + (rec_big_pct - 50.0) * 1.2)
            stat_reason = f"Small is statistically oversold (Big has dominated at {rec_big_pct}% in last {rec_total} draws). Mean reversion favors SMALL."

        # Number frequencies (0 to 9)
        num_counts = {i: 0 for i in range(10)}
        for n in numbers:
            if 0 <= n <= 9:
                num_counts[n] += 1

        # Hot and Cold numbers
        sorted_by_freq = sorted(num_counts.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [num for num, count in sorted_by_freq[:3]]
        cold_numbers = [num for num, count in sorted_by_freq[-3:]]

        # Overdue numbers (periods since last appearance)
        periods_since = {i: 999 for i in range(10)}
        for idx, h in enumerate(reversed(history)):
            try:
                num = int(h["number"])
                if 0 <= num <= 9 and periods_since[num] == 999:
                    periods_since[num] = idx
            except (ValueError, KeyError, TypeError):
                continue

        overdue_sorted = sorted(periods_since.items(), key=lambda x: x[1], reverse=True)
        overdue_numbers = [num for num, gap in overdue_sorted[:3] if gap != 999]

        # Color stats
        color_counts = Counter(colors)
        color_stats = {
            "Green": color_counts.get("Green", 0),
            "Red": color_counts.get("Red", 0),
            "Violet": color_counts.get("Violet", 0)
        }

        return {
            "signal": stat_signal,
            "confidence": round(stat_conf, 1),
            "total_records": total,
            "big_count": big_count,
            "small_count": small_count,
            "big_percent": big_pct,
            "small_percent": small_pct,
            "recent_big_percent": rec_big_pct,
            "number_frequencies": num_counts,
            "hot_numbers": hot_numbers,
            "cold_numbers": cold_numbers,
            "overdue_numbers": overdue_numbers,
            "color_stats": color_stats,
            "explanation": stat_reason
        }
