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

        # Check for alternating / chop in the last 6 draws
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

        # Check post-break transition: did the last draw just break a streak of >= 2?
        just_broke_streak = False
        if len(sizes) >= 3 and sizes[-1] != sizes[-2] and sizes[-2] == sizes[-3]:
            just_broke_streak = True

        if just_broke_streak and streak_count == 1:
            # Fresh break after a streak: high-entropy transition pivot
            pattern_name = f"Post-Streak Break ({sizes[-2]} -> {current_type})"
            streak_signal = "Neutral"
            streak_conf = 50.0
            pattern_detail = f"Fresh break after {sizes[-2]} streak. Transition pivot: wait 1 draw for regime confirmation."
        elif chop_count >= 2:
            # Alternating Chop regime (e.g. B-S-B or S-B-S)
            # In real PRNG, chop runs break rapidly. Pumping confidence into chop continuation is a fatal gambler's fallacy!
            pattern_name = f"Alternating Chop ({chop_count}x flips)"
            streak_signal = "Neutral"
            streak_conf = 50.0
            pattern_detail = f"Alternating chop ({chop_count} switches) is high-entropy noise. Filtered to protect 7/10 target."
        elif streak_count in [3, 4]:
            # Confirmed momentum dragon streak (3x or 4x) - ride the established trend!
            pattern_name = f"Dragon Streak ({streak_count}x {current_type})"
            streak_signal = current_type
            streak_conf = min(72.0, 62.0 + (streak_count - 3) * 4.0)
            pattern_detail = f"Confirmed {streak_count}x {current_type} dragon. Strong momentum favors {current_type} continuation."
        elif streak_count >= 5:
            # Dragon exhaustion zone: mean-reversion risk is extremely high
            pattern_name = f"Extended Dragon ({streak_count}x {current_type})"
            streak_signal = "Neutral"
            streak_conf = 50.0
            pattern_detail = f"Extended dragon ({streak_count}x {current_type}) reached exhaustion threshold. Do not chase."
        elif streak_count == 2:
            # Double pair: fork in the road (either 3rd continuation or 2-2 flip).
            # Do NOT bet on reversal against the pair!
            pattern_name = f"Double {current_type} Pair"
            streak_signal = "Neutral"
            streak_conf = 50.0
            pattern_detail = f"Double {current_type} pair pivot. 50/50 continuation/flip ratio: wait for 3rd confirmation."
        else:
            # streak_count == 1 (single switch)
            pattern_name = f"Single {current_type}"
            streak_signal = "Neutral"
            streak_conf = 50.0
            pattern_detail = f"Single {current_type} switch: insufficient momentum for entry."

        # 2. Historical N-Gram Matching with Laplace Regularization & Minimum Sample Threshold
        ngram_signal = "Neutral"
        ngram_conf = 50.0
        ngram_text = ""

        # Only evaluate n-grams if there are at least 30 historical records
        if total >= 30:
            for n in [3, 2]:
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
                # Require at least 6 prior occurrences to avoid overfitting on micro-samples
                if total_matches >= 6:
                    # Laplace smoothing: (count + 1) / (total + 2)
                    p_big = (matches_big + 1.0) / (total_matches + 2.0)
                    p_small = 1.0 - p_big
                    diff = p_big - 0.5

                    if abs(diff) >= 0.08:  # Significant skew
                        if p_big > 0.5:
                            ngram_signal = "Big"
                            ngram_conf = min(72.0, round(p_big * 100, 1))
                        else:
                            ngram_signal = "Small"
                            ngram_conf = min(72.0, round(p_small * 100, 1))
                        ngram_text = f"Pattern [{'->'.join(target_ngram)}] appeared {total_matches}x: {matches_big} Big, {matches_small} Small (Laplace {round(max(p_big, p_small)*100, 1)}%)."
                        break

        # Blend Streak + N-Gram:
        # N-Gram should NEVER invent a bet when the streak/regime says Neutral!
        # It is only used to slightly enhance confidence when it agrees with an active streak.
        if streak_signal != "Neutral" and ngram_signal != "Neutral":
            if streak_signal == ngram_signal:
                final_sig = streak_signal
                final_conf = min(75.0, streak_conf + 3.0)
                final_exp = f"{pattern_detail} Confirmed by history pattern: {ngram_text}"
            else:
                # Disagreement between streak momentum and n-gram -> stay cautious!
                final_sig = "Neutral"
                final_conf = 50.0
                final_exp = f"{pattern_detail} Pattern conflict: {ngram_text}"
        elif streak_signal != "Neutral":
            final_sig = streak_signal
            final_conf = streak_conf
            final_exp = pattern_detail
        else:
            final_sig = "Neutral"
            final_conf = 50.0
            final_exp = pattern_detail if pattern_detail else "Market in balanced transition flow."

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
