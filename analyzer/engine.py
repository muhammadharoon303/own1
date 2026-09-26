"""
Ensemble Prediction Engine for 92pkr Big/Small.
Aggregates Markov transitions, pattern matching, streak momentum, and frequency distributions
to generate a weighted consensus forecast, target numbers, colors, and risk sizing.
Features real-time online training and adaptive weight optimization.
"""
import os
import re
from typing import List, Dict, Any
from .markov import MarkovAnalyzer
from .patterns import PatternAnalyzer
from .statistics import StatisticsAnalyzer
from .adaptive_trainer import AdaptiveTrainer
from .confidence_calibrator import ConfidenceCalibrator
from .digit_predictor import DynamicDigitPredictor


class PredictionEngine:
    def __init__(self, data_dir: str = None):
        self.markov = MarkovAnalyzer()
        self.patterns = PatternAnalyzer()
        self.stats = StatisticsAnalyzer()
        self.digit_predictor = DynamicDigitPredictor()
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.trainer = AdaptiveTrainer(data_dir=data_dir)
        self.calibrator = ConfidenceCalibrator(data_dir=data_dir)

    def get_next_period_string(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return "20240908001"
        last_p = str(history[-1].get("period", "0")).strip()
        match = re.search(r'(\d+)$', last_p)
        if match:
            digits = match.group(1)
            prefix = last_p[:match.start()]
            next_val = int(digits) + 1
            return f"{prefix}{str(next_val).zfill(len(digits))}"
        return str(len(history) + 1)

    def predict(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not history:
            return {
                "status": "empty",
                "message": "No historical records found. Please upload a ZIP/screenshot or sync live data.",
                "prediction": None,
                "training_info": None
            }

        # 1. Run Online Adaptive Trainer: backtests recent rounds & optimizes model weights dynamically
        training_info = self.trainer.evaluate_and_train(
            history, self.markov, self.patterns, self.stats, self.digit_predictor
        )
        weights = training_info.get("weights", {"markov": 0.40, "patterns": 0.40, "statistics": 0.20})
        w_markov = weights.get("markov", 0.40)
        w_patterns = weights.get("patterns", 0.40)
        w_stats = weights.get("statistics", 0.20)

        # 2. Run individual strategy analyzers on the full history
        markov_res = self.markov.analyze(history)
        patterns_res = self.patterns.analyze(history)
        stats_res = self.stats.analyze(history)

        def to_score(res):
            sig = res.get("signal", "Neutral")
            conf = res.get("confidence", 50.0) / 100.0
            if sig == "Big":
                return conf
            elif sig == "Small":
                return 1.0 - conf
            return 0.50

        s_markov = to_score(markov_res)
        s_patterns = to_score(patterns_res)
        s_stats = to_score(stats_res)

        total_big_score = (s_markov * w_markov) + (s_patterns * w_patterns) + (s_stats * w_stats)
        total_small_score = 1.0 - total_big_score

        # Determine Consensus Signal & Confidence
        diff = total_big_score - 0.5
        # Broaden neutral margin (48.0% - 52.0%) to prevent forcing coin-flips
        if abs(diff) < 0.020:
            outcome = "NEUTRAL / SKIP"
            confidence = 50.0
        elif total_big_score > 0.5:
            outcome = "BIG"
            confidence = min(94.0, max(52.0, round(total_big_score * 100, 1)))
        else:
            outcome = "SMALL"
            confidence = min(94.0, max(52.0, round(total_small_score * 100, 1)))

        # 3. Apply Empirical Calibration from User Tested Notes
        calibration = self.calibrator.calibrate(confidence, outcome)

        # Target Numbers & Color inference using DynamicDigitPredictor (updates on every draw)
        digit_res = self.digit_predictor.predict_target_numbers(history, outcome, top_k=3)
        top_numbers = digit_res["top_numbers"]
        primary_number = digit_res["primary_number"]
        secondary_number = digit_res.get("secondary_number")
        cover_number = digit_res.get("cover_number")
        digit_probabilities = digit_res.get("probabilities", {})
        predicted_color = digit_res["predicted_color"]
        digit_explanation = digit_res["explanation"]

        cold_avoid_numbers = digit_res.get("cold_avoid_numbers", [])

        # Risk & Staking advice based on empirical calibration + online hit rate
        zone = calibration.get("zone", "")
        calib_wr = calibration.get("calibrated_win_rate", 50.0)

        if zone == "REVERSAL_TRAP":
            stake_level = "🚨 Reversal Trap (>60%)"
            stake_badge = "danger"
            stake_action = f"TRAP ALERT: User tests show >60% signals have a 75% failure rate! Naive streak is overextended. Level 1 only or SKIP."
        elif zone == "NEUTRAL_SKIP":
            stake_level = "⏸️ Neutral / Skip (N)"
            stake_badge = "secondary"
            stake_action = "DO NOT BET: Real data proves N (disagreement) leads to losses (N/L). Wait for aligned signal."
        elif zone == "PRIME_WINDOW":
            stake_level = f"🏆 Prime Sweet-Spot ({calib_wr}% Win Rate)"
            stake_badge = "success"
            stake_action = f"TOP ACCURACY TIER: {calib_wr}% verified win rate in user tracked notes! Genuine trend momentum without exhaustion."
        elif zone == "EXHAUSTION_TRAP":
            stake_level = "⚠️ Exhaustion Warning (58-60%)"
            stake_badge = "warning"
            stake_action = f"Exhaustion Zone: Accuracy drops to {calib_wr}%. Long streaks often reverse here. Do not increase stake."
        else:
            stake_level = f"Low Edge / Coin-Flip ({calib_wr}%)"
            stake_badge = "warning"
            stake_action = f"Minimal edge ({calib_wr}% historical accuracy). Bet lowest base unit or observe."

        last_record = history[-1] if history else {}
        last_period = str(last_record.get("period", "0"))
        next_period = self.get_next_period_string(history)

        return {
            "status": "success",
            "last_period": last_period,
            "next_period": next_period,
            "prediction": {
                "outcome": outcome,
                "confidence": confidence,
                "calibrated_win_rate": calib_wr,
                "calibration_zone": zone,
                "calibration_status": calibration.get("status", "NORMAL"),
                "calibration_alert": calibration.get("alert", ""),
                "calibration": calibration,
                "tier_stats": self.calibrator.get_tier_stats(),
                "p_big": round(total_big_score * 100, 1),
                "p_small": round(total_small_score * 100, 1),
                "top_numbers": top_numbers,
                "primary_number": primary_number,
                "secondary_number": secondary_number,
                "cover_number": cover_number,
                "cold_avoid_numbers": cold_avoid_numbers,
                "digit_probabilities": digit_probabilities,
                "all_group_probabilities": digit_res.get("all_group_probabilities", {}),
                "digit_explanation": digit_explanation,
                "predicted_color": predicted_color,
                "risk_advice": {
                    "level": stake_level,
                    "badge": stake_badge,
                    "action": stake_action
                }
            },
            "training_info": training_info,
            "models_breakdown": {
                "markov": {
                    "name": "Markov Transition",
                    "weight": f"{int(w_markov*100)}%",
                    "signal": markov_res["signal"],
                    "confidence": markov_res["confidence"],
                    "accuracy": f"{training_info.get('accuracy', {}).get('markov', 50)}%",
                    "explanation": markov_res["explanation"]
                },
                "patterns": {
                    "name": "Streak & N-Gram Pattern",
                    "weight": f"{int(w_patterns*100)}%",
                    "signal": patterns_res["signal"],
                    "confidence": patterns_res["confidence"],
                    "accuracy": f"{training_info.get('accuracy', {}).get('patterns', 50)}%",
                    "pattern_name": patterns_res["pattern_name"],
                    "current_streak": patterns_res.get("current_streak", {}),
                    "explanation": patterns_res["explanation"]
                },
                "statistics": {
                    "name": "Frequency & Ratio",
                    "weight": f"{int(w_stats*100)}%",
                    "signal": stats_res["signal"],
                    "confidence": stats_res["confidence"],
                    "accuracy": f"{training_info.get('accuracy', {}).get('statistics', 50)}%",
                    "big_percent": stats_res["big_percent"],
                    "small_percent": stats_res["small_percent"],
                    "explanation": stats_res["explanation"]
                }
            },
            "stats_summary": stats_res
        }
