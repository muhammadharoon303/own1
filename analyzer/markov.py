"""
Markov Chain Transition Probability Analyzer for 92pkr / Big-Small game.
Calculates 1st order and 2nd order conditional transition probabilities with recency weighting.
"""
from typing import List, Dict, Any


class MarkovAnalyzer:
    def __init__(self):
        pass

    def analyze(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        history is ordered chronologically: oldest first, newest last.
        """
        if len(history) < 2:
            return {
                "signal": "Neutral",
                "confidence": 50.0,
                "p_big": 0.5,
                "p_small": 0.5,
                "order1_transitions": {},
                "order2_transitions": {},
                "explanation": "Insufficient historical data for Markov analysis (minimum 2 periods required)."
            }

        sizes = [h["size"].capitalize() for h in history if h.get("size")]
        n = len(sizes)

        # Global transitions
        trans1: Dict[str, Dict[str, float]] = {
            "Big": {"Big": 0.0, "Small": 0.0},
            "Small": {"Big": 0.0, "Small": 0.0}
        }
        trans2: Dict[str, Dict[str, float]] = {
            "Big-Big": {"Big": 0.0, "Small": 0.0},
            "Big-Small": {"Big": 0.0, "Small": 0.0},
            "Small-Big": {"Big": 0.0, "Small": 0.0},
            "Small-Small": {"Big": 0.0, "Small": 0.0}
        }

        # Weight transitions with recency multiplier (recent 30 draws count more)
        for i in range(n - 1):
            curr, nxt = sizes[i], sizes[i + 1]
            recency_weight = 1.0 + (i / max(1, n)) * 1.5  # older=1.0x, newest=2.5x
            if curr in trans1 and nxt in trans1[curr]:
                trans1[curr][nxt] += recency_weight

        for i in range(n - 2):
            key = f"{sizes[i]}-{sizes[i+1]}"
            nxt = sizes[i + 2]
            recency_weight = 1.0 + (i / max(1, n)) * 1.5
            if key in trans2 and nxt in trans2[key]:
                trans2[key][nxt] += recency_weight

        last_state = sizes[-1]
        total_curr1 = sum(trans1[last_state].values())
        if total_curr1 > 0:
            p_big_1 = trans1[last_state]["Big"] / total_curr1
            p_small_1 = trans1[last_state]["Small"] / total_curr1
        else:
            p_big_1 = 0.5
            p_small_1 = 0.5

        # 2nd Order
        p_big_2 = None
        state2_key = None
        if n >= 2:
            state2_key = f"{sizes[-2]}-{sizes[-1]}"
            if state2_key in trans2:
                total_curr2 = sum(trans2[state2_key].values())
                if total_curr2 > 0:
                    p_big_2 = trans2[state2_key]["Big"] / total_curr2

        if p_big_2 is not None:
            final_p_big = (p_big_2 * 0.65) + (p_big_1 * 0.35)
            final_p_small = 1.0 - final_p_big
            basis = f"From state [{state2_key}]: {final_p_big*100:.1f}% Big vs {final_p_small*100:.1f}% Small"
        else:
            final_p_big = p_big_1
            final_p_small = p_small_1
            basis = f"From state [{last_state}]: {final_p_big*100:.1f}% Big vs {final_p_small*100:.1f}% Small"

        # Signal determination with responsive sensitivity
        diff = final_p_big - 0.5
        if abs(diff) < 0.015:
            signal = "Neutral"
            confidence = 50.0
        elif final_p_big > 0.5:
            signal = "Big"
            confidence = min(92.0, max(52.0, round(final_p_big * 100, 1)))
        else:
            signal = "Small"
            confidence = min(92.0, max(52.0, round(final_p_small * 100, 1)))

        return {
            "signal": signal,
            "confidence": confidence,
            "p_big": round(final_p_big, 3),
            "p_small": round(final_p_small, 3),
            "last_state": last_state,
            "last_2state": state2_key,
            "explanation": basis
        }
