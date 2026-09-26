"""
Pattern Recognition and Streak Analyzer for 92pkr / Big-Small game.
Evaluates current run length, alternating chop tendencies, and historical pattern matching.
"""
from typing import List, Dict, Any


class PatternAnalyzer:
    def __init__(self):
        pass

    def analyze(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(history) < 2:
            return {
                "signal": "Neutral",
                "confidence": 50.0,
                "current_streak": {"type": "None", "count": 0},
                "pattern_name": "Insufficient Data",
                "explanation": "Need at least 2 records for pattern analysis."
            }

        sizes = [h["size"].capitalize() for h in history if h.get("size")]
        total = len(sizes)
        current_type = sizes[-1]

        # 1. Current Streak calculation
        streak_count = 0
        for s in reversed(sizes):
            if s == current_type:
                streak_count += 1
            else:
                break

        # Check for alternating / chop in the last 4-6 draws
        chop_count = 0
        for i in range(len(sizes) - 1, 0, -1):
            if sizes[i] != sizes[i - 1]:
                chop_count += 1
            else:
                break

        streak_signal = "Neutral"
        streak_conf = 50.0
        pattern_name = "Normal Run"
        pattern_detail = ""

        if chop_count >= 2:
            # Alternating Chop mode (e.g. B-S-B or S-B-S)
            pattern_name = f"Alternating Chop ({chop_count}x flips)"
            streak_signal = "Small" if current_type == "Big" else "Big"
            streak_conf = min(85.0, 56.0 + chop_count * 5.0)
            pattern_detail = f"Alternating chop detected ({chop_count} switches). Continuation favors flip to {streak_signal}."
        elif streak_count >= 3:
            # Dragon streak
            pattern_name = f"Dragon Streak ({streak_count}x {current_type})"
            if streak_count >= 6:
                # Strong exhaustion zone: mean-reversion favored
                streak_signal = "Small" if current_type == "Big" else "Big"
                streak_conf = min(82.0, 62.0 + (streak_count - 5) * 3.0)
                pattern_detail = f"Extended dragon ({streak_count}x {current_type}) near resistance. Reversal to {streak_signal} favored."
            else:
                # Ride the dragon trend
                streak_signal = current_type
                streak_conf = min(80.0, 58.0 + streak_count * 4.0)
                pattern_detail = f"Dragon trend active ({streak_count}x {current_type}). Momentum favors {streak_signal}."
        elif streak_count == 2:
            pattern_name = f"Double {current_type} Pair"
            # In casino patterns, double often tests either 3rd continuation or 2-2 switch
            # Look at historical what happened after 2x current_type
            two_type_followed_same = 0
            two_type_followed_flip = 0
            for i in range(len(sizes) - 2):
                if sizes[i] == current_type and sizes[i + 1] == current_type:
                    if sizes[i + 2] == current_type:
                        two_type_followed_same += 1
                    else:
                        two_type_followed_flip += 1
            
            if two_type_followed_same > two_type_followed_flip:
                streak_signal = current_type
                streak_conf = 62.0
                pattern_detail = f"Double {current_type} historically continued to 3rd draw ({two_type_followed_same} vs {two_type_followed_flip})."
            elif two_type_followed_flip > two_type_followed_same:
                streak_signal = "Small" if current_type == "Big" else "Big"
                streak_conf = 62.0
                pattern_detail = f"Double {current_type} historically flipped to 2-2 pair ({two_type_followed_flip} vs {two_type_followed_same})."
            else:
                streak_signal = current_type
                streak_conf = 55.0
                pattern_detail = f"Double {current_type} balanced. Slight momentum to {streak_signal}."
        else:
            # streak_count == 1 (first appearance after switch)
            pattern_name = f"Single {current_type} Switch"
            streak_signal = current_type
            streak_conf = 54.0
            pattern_detail = f"Fresh switch to {current_type}."

        # 2. Historical N-Gram Matching (last 2 and 3 draws)
        ngram_signal = "Neutral"
        ngram_conf = 50.0
        ngram_text = ""

        for n in [3, 2]:
            if total > n + 1:
                target_ngram = sizes[-n:]
                matches_big = 0
                matches_small = 0

                for i in range(total - n):
                    window = sizes[i : i + n]
                    if window == target_ngram:
                        next_res = sizes[i + n]
                        if next_res == "Big":
                            matches_big += 1
                        elif next_res == "Small":
                            matches_small += 1

                total_matches = matches_big + matches_small
                if total_matches >= 2:
                    if matches_big > matches_small:
                        ngram_signal = "Big"
                        ngram_conf = round(matches_big / total_matches * 100, 1)
                    elif matches_small > matches_big:
                        ngram_signal = "Small"
                        ngram_conf = round(matches_small / total_matches * 100, 1)
                    ngram_text = f"Pattern [{'->'.join(target_ngram)}] appeared {total_matches}x in history: {matches_big} Big, {matches_small} Small."
                    break

        # Blend
        if ngram_signal != "Neutral" and streak_signal != "Neutral":
            if ngram_signal == streak_signal:
                final_sig = streak_signal
                final_conf = min(88.0, max(streak_conf, ngram_conf) + 3.0)
                final_exp = f"{pattern_detail} Confirmed by history: {ngram_text}"
            else:
                final_sig = streak_signal
                final_conf = max(52.0, (streak_conf + (100.0 - ngram_conf)) / 2)
                final_exp = f"{pattern_detail} (History sequence shows {ngram_signal} {ngram_conf}%)."
        elif streak_signal != "Neutral":
            final_sig = streak_signal
            final_conf = streak_conf
            final_exp = pattern_detail
        elif ngram_signal != "Neutral":
            final_sig = ngram_signal
            final_conf = ngram_conf
            final_exp = ngram_text
        else:
            final_sig = "Neutral"
            final_conf = 50.0
            final_exp = "Normal balanced flow."

        return {
            "signal": final_sig,
            "confidence": round(final_conf, 1),
            "current_streak": {
                "type": current_type,
                "count": streak_count
            },
            "pattern_name": pattern_name,
            "explanation": final_exp
        }
