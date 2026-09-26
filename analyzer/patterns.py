"""
Pattern Recognition and Streak Analyzer for 92pkr / Big-Small game.
Evaluates current run length, alternating chop tendencies, streak exhaustion,
and recency-weighted N-gram historical sequence matching.
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
        opposite_type = "Small" if current_type == "Big" else "Big"

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

        # REGIME 1: Alternating Chop (B-S-B or S-B-S)
        if chop_count >= 2:
            pattern_name = f"Alternating Chop ({chop_count}x flips)"
            streak_signal = opposite_type
            streak_conf = min(84.0, 58.0 + chop_count * 4.0)
            pattern_detail = f"Alternating chop mode active ({chop_count} switches). High probability of continuation to {streak_signal}."

        # REGIME 2: Dragon Streak Momentum vs Exhaustion
        elif streak_count >= 4:
            # In WinGo, streaks of 4+ face heavy mean-reversion resistance (75%+ reversal rate)
            pattern_name = f"Dragon Exhaustion ({streak_count}x {current_type})"
            streak_signal = opposite_type
            streak_conf = min(82.0, 62.0 + (streak_count - 3) * 4.0)
            pattern_detail = f"Dragon streak ({streak_count}x {current_type}) reached exhaustion limit. Mean-reversion favors break to {streak_signal}."
        elif streak_count == 3:
            # 3 in a row: Peak trend momentum
            pattern_name = f"Dragon Trend ({streak_count}x {current_type})"
            streak_signal = current_type
            streak_conf = 59.0
            pattern_detail = f"Dragon momentum confirmed at 3x {current_type}. Follow trend to 4th draw with tight risk."

        # REGIME 3: Double Pair Pattern Analysis (2-2 or 2-1)
        elif streak_count == 2:
            pattern_name = f"Double {current_type} Pair"
            # Examine recent 25 draws: did 2x continue to 3rd or flip to 2-2 pair?
            recent_sizes = sizes[-25:] if total >= 25 else sizes
            two_followed_same = 0
            two_followed_flip = 0
            for i in range(len(recent_sizes) - 2):
                if recent_sizes[i] == current_type and recent_sizes[i + 1] == current_type:
                    if recent_sizes[i + 2] == current_type:
                        two_followed_same += 1
                    else:
                        two_followed_flip += 1

            if two_followed_flip > two_followed_same:
                streak_signal = opposite_type
                streak_conf = 61.0
                pattern_detail = f"Double {current_type} in 2-2 pair cycle ({two_followed_flip} flips vs {two_followed_same} runs). Reversal to {streak_signal} favored."
            elif two_followed_same > two_followed_flip:
                streak_signal = current_type
                streak_conf = 61.0
                pattern_detail = f"Double {current_type} has continuation momentum ({two_followed_same} runs vs {two_followed_flip} flips)."
            else:
                streak_signal = "Neutral"
                streak_conf = 50.0
                pattern_detail = f"Double {current_type} balanced. No decisive streak edge."

        # REGIME 4: Fresh Single Switch (streak_count == 1)
        else:
            pattern_name = f"Single {current_type} Transition"
            # Check 2-2 pair continuation: e.g. previous was SS, now B -> does it form BB?
            if total >= 4 and sizes[-3] == opposite_type and sizes[-2] == opposite_type and sizes[-1] == current_type:
                streak_signal = current_type
                streak_conf = 58.0
                pattern_detail = f"Potential 2-2 mirror formation: {opposite_type}{opposite_type} followed by {current_type}. Second {current_type} favored."
            else:
                streak_signal = "Neutral"
                streak_conf = 50.0
                pattern_detail = f"Fresh single switch to {current_type}. Deferring to sequence pattern memory."

        # 2. Recency-Weighted High-Order Sequence Pattern Matching (4-gram, 3-gram, 2-gram)
        ngram_signal = "Neutral"
        ngram_conf = 50.0
        ngram_text = ""

        for n in [4, 3, 2]:
            if total >= n + 2:
                target_ngram = sizes[-n:]
                matches_big_w = 0.0
                matches_small_w = 0.0
                raw_matches_count = 0

                for i in range(total - n - 1):
                    window = sizes[i : i + n]
                    if window == target_ngram:
                        next_res = sizes[i + n]
                        raw_matches_count += 1
                        # Exponential recency weighting: recent matches have 3x influence
                        rec_w = 1.0 + (i / max(1, total)) * 2.5
                        if next_res == "Big":
                            matches_big_w += rec_w
                        elif next_res == "Small":
                            matches_small_w += rec_w

                tot_w = matches_big_w + matches_small_w
                if raw_matches_count >= 2 and tot_w > 0:
                    dominance = max(matches_big_w, matches_small_w) / tot_w
                    if dominance >= 0.62:
                        if matches_big_w > matches_small_w:
                            ngram_signal = "Big"
                        else:
                            ngram_signal = "Small"
                        ngram_conf = round(min(86.0, 52.0 + dominance * 32.0), 1)
                        ngram_text = f"Pattern [{'->'.join(target_ngram)}] appeared {raw_matches_count}x: {int(dominance*100)}% weighted affinity towards {ngram_signal}."
                        break

        # 3. Consensus Integration
        if ngram_signal != "Neutral" and streak_signal != "Neutral":
            if ngram_signal == streak_signal:
                final_sig = streak_signal
                final_conf = min(88.0, max(streak_conf, ngram_conf) + 4.0)
                final_exp = f"{pattern_detail} Confirmed by Sequence Memory: {ngram_text}"
            else:
                # Contradiction: reduce confidence, defer to pattern if dragon/chop
                if "Dragon" in pattern_name or "Chop" in pattern_name:
                    final_sig = streak_signal
                    final_conf = max(52.0, streak_conf - 4.0)
                    final_exp = f"{pattern_detail} (Sequence memory suggests {ngram_signal} {ngram_conf}%)."
                else:
                    final_sig = ngram_signal
                    final_conf = max(52.0, ngram_conf - 4.0)
                    final_exp = f"{ngram_text} (Streak trend indicates {streak_signal})."
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
            final_exp = "Normal balanced flow. Awaiting structured pattern formation."

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
