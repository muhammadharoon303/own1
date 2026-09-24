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

        # Use recent sliding window (up to 45 draws) to capture active gaming regime
        window_size = min(45, n)
        recent_sizes = sizes[-window_size:]
        local_n = len(recent_sizes)

        # Transition matrices initialized with Laplace prior (+1 pseudocount)
        trans1: Dict[str, Dict[str, float]] = {
            "Big": {"Big": 1.0, "Small": 1.0},
            "Small": {"Big": 1.0, "Small": 1.0}
        }
        trans2: Dict[str, Dict[str, float]] = {
            "Big-Big": {"Big": 1.0, "Small": 1.0},
            "Big-Small": {"Big": 1.0, "Small": 1.0},
            "Small-Big": {"Big": 1.0, "Small": 1.0},
            "Small-Small": {"Big": 1.0, "Small": 1.0}
        }

        # Weight transitions with recency multiplier within local window
        for i in range(local_n - 1):
            curr, nxt = recent_sizes[i], recent_sizes[i + 1]
            recency_weight = 1.0 + (i / max(1, local_n)) * 1.0  # 1.0x to 2.0x
            if curr in trans1 and nxt in trans1[curr]:
                trans1[curr][nxt] += recency_weight

        for i in range(local_n - 2):
            key = f"{recent_sizes[i]}-{recent_sizes[i+1]}"
            nxt = recent_sizes[i + 2]
            recency_weight = 1.0 + (i / max(1, local_n)) * 1.0
            if key in trans2 and nxt in trans2[key]:
                trans2[key][nxt] += recency_weight

        last_state = sizes[-1]
        total_curr1 = sum(trans1[last_state].values())
        p_big_1 = trans1[last_state]["Big"] / total_curr1
        p_small_1 = trans1[last_state]["Small"] / total_curr1

        # 2nd Order
        p_big_2 = None
        state2_key = None
        if n >= 2:
            state2_key = f"{sizes[-2]}-{sizes[-1]}"
            if state2_key in trans2:
                total_curr2 = sum(trans2[state2_key].values())
                p_big_2 = trans2[state2_key]["Big"] / total_curr2

        if p_big_2 is not None:
            final_p_big = (p_big_2 * 0.70) + (p_big_1 * 0.30)
            final_p_small = 1.0 - final_p_big
            basis = f"From state [{state2_key}]: {final_p_big*100:.1f}% Big vs {final_p_small*100:.1f}% Small (Local {local_n} rounds)"
        else:
            final_p_big = p_big_1
            final_p_small = p_small_1
            basis = f"From state [{last_state}]: {final_p_big*100:.1f}% Big vs {final_p_small*100:.1f}% Small (Local {local_n} rounds)"

        # Signal determination: require at least 4% edge (46% - 54% is neutral noise)
        diff = final_p_big - 0.5
        if abs(diff) < 0.040:
            signal = "Neutral"
            confidence = 50.0
        elif final_p_big > 0.5:
            signal = "Big"
            confidence = min(75.0, round(52.0 + (final_p_big - 0.50) * 75.0, 1))
        else:
            signal = "Small"
            confidence = min(75.0, round(52.0 + (final_p_small - 0.50) * 75.0, 1))

        return {
            "signal": signal,
            "confidence": confidence,
            "p_big": round(final_p_big, 3),
            "p_small": round(final_p_small, 3),
            "last_state": last_state,
            "last_2state": state2_key,
            "explanation": basis
        }
