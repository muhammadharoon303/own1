"""
Dynamic Digit & Number Predictor for 92PKR Win Go.
Computes conditional transition probabilities P(D_{t+1} | D_t),
exponential recency weighting, rolling velocity, mirror/complement affinity,
and cycle gap analysis to dynamically update target numbers on every round.
"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter


class DynamicDigitPredictor:
    def __init__(self):
        # Mirror affinities in Asian wheel / WinGo: (0<->5, 1<->6, 2<->7, 3<->8, 4<->9)
        self.mirrors = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
        # Complement sum-to-9 pairs: (0<->9, 1<->8, 2<->7, 3<->6, 4<->5)
        self.complements = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}

    def predict_target_numbers(self, history: List[Dict[str, Any]], predicted_size: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Dynamically calculates the highest-probability winning numbers for the upcoming draw
        conditioned on the exact last drawn number, rolling frequency, and conditional transitions.
        """
        if not history:
            default_nums = [5, 7, 8] if predicted_size == "BIG" else [1, 2, 3]
            return {
                "top_numbers": default_nums,
                "primary_number": default_nums[0],
                "predicted_color": "Red" if default_nums[0] in [2, 4, 6, 8] else "Green",
                "scores": {n: 1.0 for n in default_nums},
                "explanation": "Default baseline targets (insufficient history)."
            }

        # Extract chronological digit sequence
        valid_records = [h for h in history if h.get("number") is not None and str(h.get("number")).isdigit()]
        numbers = [int(h["number"]) for h in valid_records]
        n = len(numbers)

        if n == 0:
            default_nums = [5, 7, 8] if predicted_size == "BIG" else [1, 2, 3]
            return {
                "top_numbers": default_nums,
                "primary_number": default_nums[0],
                "predicted_color": "Green",
                "scores": {},
                "explanation": "No valid drawn numbers found."
            }

        last_num = numbers[-1]
        prev_num = numbers[-2] if n >= 2 else None

        # Determine candidate pool
        if predicted_size == "BIG":
            candidate_pool = [5, 6, 7, 8, 9]
        elif predicted_size == "SMALL":
            candidate_pool = [0, 1, 2, 3, 4]
        else:
            candidate_pool = list(range(10))

        # 1. First-Order Conditional Digit Transition Scores P(Next | Last)
        # Weight recent transitions much higher with recency multiplier
        trans1_scores = defaultdict(float)
        for i in range(n - 1):
            if numbers[i] == last_num:
                # Recency weighting: older=1.0x, newest=3.0x
                rec_weight = 1.0 + (i / max(1, n)) * 2.5
                trans1_scores[numbers[i + 1]] += rec_weight

        # 2. Second-Order Conditional Digit Transition Scores P(Next | Prev, Last)
        trans2_scores = defaultdict(float)
        if prev_num is not None:
            for i in range(n - 2):
                if numbers[i] == prev_num and numbers[i + 1] == last_num:
                    rec_weight = 1.5 + (i / max(1, n)) * 3.0
                    trans2_scores[numbers[i + 2]] += rec_weight

        # 3. Rolling Window Frequency (Last 15 draws velocity)
        rolling_window = numbers[-15:] if n >= 15 else numbers
        rolling_counts = Counter(rolling_window)

        # 4. Cycle Gap Analysis (Draws elapsed since each number appeared)
        gaps = {}
        for d in range(10):
            try:
                rev_idx = list(reversed(numbers)).index(d)
                gaps[d] = rev_idx
            except ValueError:
                gaps[d] = 25  # never appeared in recent history

        # 5. Mirror & Complement Affinity
        mirror_target = self.mirrors.get(last_num)
        comp_target = self.complements.get(last_num)

        # 6. Combined Dynamic Scoring for each candidate digit
        candidate_scores = {}
        for d in candidate_pool:
            # Component 1: Historical Transition after last_num (Weight: 3.5)
            s_t1 = trans1_scores.get(d, 0.0)
            # Component 2: Second-order transition pair (Weight: 2.0)
            s_t2 = trans2_scores.get(d, 0.0)
            # Component 3: Hot momentum in last 15 draws (Weight: 1.5)
            s_roll = rolling_counts.get(d, 0)
            # Component 4: Cycle bonus (numbers between 3 and 10 draws overdue have high return rate)
            gap = gaps.get(d, 10)
            if 3 <= gap <= 10:
                s_cycle = 1.8
            elif gap > 15:
                s_cycle = 1.2
            else:
                s_cycle = 0.5  # appeared just 1-2 draws ago, slight cooldown
            # Component 5: Mirror & Complement affinity
            s_affinity = 0.0
            if d == mirror_target:
                s_affinity += 1.8
            if d == comp_target:
                s_affinity += 1.2
            # Component 6: Adjacent proximity to last number (+-1 or +-2)
            dist = abs(d - last_num)
            if dist in [1, 2]:
                s_proximity = 1.0
            else:
                s_proximity = 0.2

            total_score = (s_t1 * 3.5) + (s_t2 * 2.5) + (s_roll * 1.5) + (s_cycle * 1.2) + s_affinity + s_proximity
            candidate_scores[d] = round(total_score, 2)

        # Sort candidate digits by dynamic score
        ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        top_digits = [d for d, s in ranked[:top_k]]
        primary_digit = top_digits[0] if top_digits else (7 if predicted_size == "BIG" else 2)

        # Determine target color based on top digits
        color_vote = {"Red": 0, "Green": 0, "Violet": 0}
        for d in top_digits:
            if d in [2, 4, 6, 8]:
                color_vote["Red"] += 3
            elif d in [1, 3, 7, 9]:
                color_vote["Green"] += 3
            elif d == 0:
                color_vote["Red"] += 1
                color_vote["Violet"] += 3
            elif d == 5:
                color_vote["Green"] += 1
                color_vote["Violet"] += 3

        predicted_color = max(color_vote.items(), key=lambda x: x[1])[0]

        # Explanation
        explanation = f"Conditioned on last drawn {last_num}: Dynamic transitions favor {top_digits}. Primary pick: {primary_digit} ({predicted_color})."

        return {
            "top_numbers": top_digits,
            "primary_number": primary_digit,
            "predicted_color": predicted_color,
            "scores": {str(d): s for d, s in ranked},
            "last_drawn_reference": last_num,
            "explanation": explanation
        }
