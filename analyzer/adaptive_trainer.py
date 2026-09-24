"""
Self-Training & Online Adaptive Learning Engine for 92PKR Big/Small.
Continuously evaluates previous model forecasts against real drawn outcomes,
tracks model win-rates, dynamically optimizes strategy weights, and updates
pattern memory trees.
"""
import os
import json
from typing import List, Dict, Any, Tuple


class AdaptiveTrainer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.stats_file = os.path.join(data_dir, "training_stats.json")
        self.weights_file = os.path.join(data_dir, "model_weights.json")
        self.default_weights = {"markov": 0.40, "patterns": 0.40, "statistics": 0.20}

    def load_weights(self) -> Dict[str, float]:
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    w = json.load(f)
                    if isinstance(w, dict) and "markov" in w and "patterns" in w:
                        return w
            except Exception:
                pass
        return dict(self.default_weights)

    def save_weights(self, weights: Dict[str, float]):
        try:
            with open(self.weights_file, "w", encoding="utf-8") as f:
                json.dump(weights, f, indent=2)
        except Exception as e:
            print(f"Error saving weights: {e}")

    def evaluate_and_train(self, history: List[Dict[str, Any]],
                           markov_analyzer, pattern_analyzer, stats_analyzer) -> Dict[str, Any]:
        """
        Performs walk-forward training across historical draws:
        1. Tests each sub-model on previous rounds.
        2. Calculates hit-rate (accuracy) of Markov, Pattern, and Stats over recent 30 rounds.
        3. Dynamically re-weights the models proportional to their actual recent success!
        """
        n = len(history)
        if n < 5:
            return {
                "trained_samples": n,
                "weights": self.load_weights(),
                "accuracy": {"overall": 50.0, "markov": 50.0, "patterns": 50.0, "statistics": 50.0},
                "last_verification": None,
                "recent_history_eval": []
            }

        # Walk-forward backtest window (evaluate up to last 35 rounds)
        eval_window = min(35, n - 2)
        start_idx = n - eval_window

        model_hits = {"markov": 0, "patterns": 0, "statistics": 0, "consensus": 0}
        model_valid = {"markov": 0, "patterns": 0, "statistics": 0, "consensus": 0}
        eval_details = []

        current_weights = self.load_weights()

        for i in range(start_idx, n):
            sub_hist = history[:i]
            actual_next = history[i]
            actual_outcome = actual_next.get("size", "").upper()  # BIG or SMALL

            if not actual_outcome:
                continue

            # Run models on past sub_hist
            m_res = markov_analyzer.analyze(sub_hist)
            p_res = pattern_analyzer.analyze(sub_hist)
            s_res = stats_analyzer.analyze(sub_hist)

            m_sig = m_res.get("signal", "Neutral").upper()
            p_sig = p_res.get("signal", "Neutral").upper()
            s_sig = s_res.get("signal", "Neutral").upper()

            # Track sub-model accuracy
            for key, sig in [("markov", m_sig), ("patterns", p_sig), ("statistics", s_sig)]:
                if sig in ["BIG", "SMALL"]:
                    model_valid[key] += 1
                    if sig == actual_outcome:
                        model_hits[key] += 1

            # Check consensus prediction with Sniper Quality Filter
            def to_score(sig, conf):
                if sig == "BIG": return conf / 100.0
                if sig == "SMALL": return 1.0 - (conf / 100.0)
                return 0.5

            s_m = to_score(m_sig, m_res.get("confidence", 50.0))
            s_p = to_score(p_sig, p_res.get("confidence", 50.0))
            s_s = to_score(s_sig, s_res.get("confidence", 50.0))

            total_big = (s_m * current_weights["markov"]) + (s_p * current_weights["patterns"]) + (s_s * current_weights["statistics"])
            raw_conf = round(max(total_big, 1.0 - total_big) * 100.0, 1)

            # Conflict & Quality Filter check
            is_conflict = (m_sig in ["BIG", "SMALL"] and p_sig in ["BIG", "SMALL"] and m_sig != p_sig)
            streak_len = p_res.get("current_streak", {}).get("count", 1)

            if is_conflict or raw_conf < 57.5 or streak_len >= 4 or (streak_len == 2 and p_sig == "NEUTRAL"):
                cons_pred = "NEUTRAL"
            else:
                cons_pred = "BIG" if total_big > 0.5 else ("SMALL" if total_big < 0.5 else "NEUTRAL")

            if cons_pred != "NEUTRAL":
                model_valid["consensus"] += 1
                hit = (cons_pred == actual_outcome)
                if hit:
                    model_hits["consensus"] += 1
            else:
                hit = None

            eval_details.append({
                "period": actual_next.get("period"),
                "number": actual_next.get("number"),
                "actual": actual_outcome,
                "predicted": cons_pred,
                "hit": hit
            })

        # Calculate accuracy percentages
        def get_acc(k):
            val = model_valid[k]
            if val == 0: return 50.0
            return round((model_hits[k] / val) * 100, 1)

        acc_markov = get_acc("markov")
        acc_patterns = get_acc("patterns")
        acc_stats = get_acc("statistics")
        acc_consensus = get_acc("consensus")

        # ADAPTIVE WEIGHT OPTIMIZATION:
        # Give higher weight to models with higher recent hit-rate using Softmax / Normalized power
        raw_scores = {
            "markov": max(0.2, (acc_markov / 100.0) ** 2),
            "patterns": max(0.2, (acc_patterns / 100.0) ** 2),
            "statistics": max(0.15, (acc_stats / 100.0) ** 2)
        }
        total_raw = sum(raw_scores.values())
        new_weights = {
            k: round(v / total_raw, 3) for k, v in raw_scores.items()
        }

        # Smooth update with previous weights (EMA 70% new, 30% old to prevent sudden jitter)
        smoothed_weights = {
            k: round((new_weights[k] * 0.70) + (current_weights.get(k, 0.33) * 0.30), 3)
            for k in new_weights
        }
        # Normalize to exactly 1.0
        w_sum = sum(smoothed_weights.values())
        final_weights = {k: round(v / w_sum, 3) for k, v in smoothed_weights.items()}

        self.save_weights(final_weights)

        # Last verification result
        last_eval = eval_details[-1] if eval_details else None

        # Rolling 10 active verification score (Target: 7/10 Wins = 70%)
        active_evals = [e for e in eval_details if e.get("hit") is not None]
        last_10_active = active_evals[-10:] if active_evals else []
        last_10_wins = sum(1 for e in last_10_active if e.get("hit") is True)
        last_10_count = len(last_10_active)
        rolling_10_rate = round((last_10_wins / last_10_count * 100), 1) if last_10_count > 0 else 0.0

        training_summary = {
            "trained_samples": n,
            "evaluation_window": len(eval_details),
            "weights": final_weights,
            "accuracy": {
                "consensus": acc_consensus,
                "markov": acc_markov,
                "patterns": acc_patterns,
                "statistics": acc_stats
            },
            "rolling_10": {
                "wins": last_10_wins,
                "total": last_10_count,
                "win_rate": rolling_10_rate,
                "target_wins": 7,
                "target_met": (last_10_wins >= 7) if last_10_count >= 10 else None,
                "display": f"{last_10_wins}/{last_10_count} Wins" if last_10_count > 0 else "0/10 Wins"
            },
            "last_verification": last_eval,
            "recent_verifications": eval_details[-12:] if eval_details else [],
            "active_verifications": last_10_active
        }


        # Save stats
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(training_summary, f, indent=2)
        except Exception:
            pass

        return training_summary
