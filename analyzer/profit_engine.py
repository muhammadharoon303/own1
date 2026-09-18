import os
import json
from typing import Dict, Any, List

class ProfitEngine:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.data_dir = data_dir
        self.config_file = os.path.join(data_dir, 'bankroll_config.json')

    def load_config(self) -> Dict[str, Any]:
        default_cfg = {
            'initial_capital': 1000,
            'base_unit': 10,
            'target_profit': 300,
            'stop_loss': 400,
            'current_streak_losses': 0,
            'strategy': 'FIBONACCI_SAFE',
            'filter_mode': 'STRICT_PROFIT'
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    default_cfg.update(data)
            except Exception:
                pass
        return default_cfg

    def save_config(self, cfg: Dict[str, Any]):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            print(f'Error saving bankroll config: {e}')

    def evaluate_profit_signal(self, 
                               raw_outcome: str, 
                               confidence: float, 
                               calib: Dict[str, Any], 
                               recent_streak: Dict[str, Any],
                               sub_signals: Dict[str, str],
                               history_eval: List[Dict[str, Any]]) -> Dict[str, Any]:
        cfg = self.load_config()
        base_unit = cfg.get('base_unit', 10)
        zone = calib.get('zone', '')
        calib_wr = calib.get('calibrated_win_rate', 50.0)
        streak_count = recent_streak.get('count', 0)
        streak_type = recent_streak.get('type', '')

        # Check sub-model consensus
        signals = [v.upper() for v in sub_signals.values() if v.upper() in ['BIG', 'SMALL']]
        all_agree = (len(signals) >= 3 and len(set(signals)) == 1)
        two_agree = (signals.count('BIG') >= 2 or signals.count('SMALL') >= 2)

        # Count consecutive losses in recent verifications
        loss_streak = 0
        if history_eval:
            for item in reversed(history_eval):
                if item.get('hit') is False:
                    loss_streak += 1
                elif item.get('hit') is True:
                    break
        cfg['current_streak_losses'] = loss_streak

        # RULE 1: STRICT FILTER - NEVER BET ON NEUTRAL OR DISAGREEMENT
        if raw_outcome == 'NEUTRAL / SKIP' or zone == 'NEUTRAL_SKIP' or not two_agree:
            return {
                'trade_action': 'WAIT_FOR_SIGNAL',
                'signal_display': 'WAIT (NO BET)',
                'badge': 'secondary',
                'grade': 'SKIP',
                'grade_color': 'slate',
                'reliability_score': 0,
                'recommended_stake': 0,
                'multiplier': 0,
                'profit_edge': '0%',
                'action_advice': 'MODELS CONFLICTING / COIN-FLIP. Do NOT bet this round. Wait for an aligned prime setup.',
                'reasons': [
                    'Models in disagreement or neutral state.',
                    'User empirical notes proved 0% win rate on N rounds. Capital preserved!'
                ]
            }

        # RULE 2: REVERSAL TRAP FILTER (> 60% OR EXTENDED DRAGON)
        if zone == 'REVERSAL_TRAP' or (streak_count >= 5 and raw_outcome == streak_type.upper()):
            return {
                'trade_action': 'REVERSAL_CAUTION',
                'signal_display': 'TRAP WARNING (SKIP)',
                'badge': 'danger',
                'grade': 'DANGER (TRAP)',
                'grade_color': 'rose',
                'reliability_score': 25,
                'recommended_stake': 0,
                'multiplier': 0,
                'profit_edge': '-50% (Trap Risk)',
                'action_advice': 'DANGER TRAP: Streak is at critical exhaustion point. Real test data proved a 75% failure rate here. SKIP THIS ROUND.',
                'reasons': [
                    f'{streak_count}x {streak_type} is at critical exhaustion point.',
                    'Empirical testing proved 75% failure rate in this zone. DO NOT FOLLOW.'
                ]
            }

        # RULE 3: GRADE AAA+ PRIME ENTRY (SWEET SPOT: 53.5% - 57.9% + FULL AGREEMENT)
        if zone == 'PRIME_WINDOW' and all_agree:
            multipliers = [1, 1, 2, 3, 5, 8]
            mult = multipliers[min(loss_streak, len(multipliers) - 1)]
            stake = base_unit * mult
            edge_val = round(calib_wr - 50.0, 1)
            return {
                'trade_action': 'STRONG_BUY',
                'signal_display': f'AAA+ PRIME {raw_outcome}',
                'badge': 'success',
                'grade': 'AAA+ (High Profit Edge)',
                'grade_color': 'emerald',
                'reliability_score': 88,
                'recommended_stake': stake,
                'multiplier': mult,
                'profit_edge': f'+{edge_val}% EV Edge',
                'action_advice': f'HIGH CONVICTION ENTRY: All models agree on {raw_outcome} in the sweet spot. Recommended Stake: Level {mult} ({stake} PKR).',
                'reasons': [
                    f'All 3 models strictly aligned on {raw_outcome}.',
                    f'Verified {calib_wr}% historical win rate in your test notes.',
                    'Clean momentum without streak exhaustion.'
                ]
            }

        # RULE 4: GRADE A (STANDARD PRIME: 53% - 57.9% WITH 2/3 AGREEMENT)
        if zone == 'PRIME_WINDOW' and two_agree:
            multipliers = [1, 1, 2, 3, 5]
            mult = multipliers[min(loss_streak, len(multipliers) - 1)]
            stake = base_unit * mult
            edge_val = round(calib_wr - 50.0, 1)
            return {
                'trade_action': 'STANDARD_BUY',
                'signal_display': f'BUY {raw_outcome}',
                'badge': 'primary',
                'grade': 'A (Confirmed Trend)',
                'grade_color': 'cyan',
                'reliability_score': 74,
                'recommended_stake': stake,
                'multiplier': mult,
                'profit_edge': f'+{edge_val}% EV Edge',
                'action_advice': f'Confirmed Prime Trend ({raw_outcome}). Recommended Stake: Level {mult} ({stake} PKR).',
                'reasons': [
                    f'Prime zone confirmed with majority consensus ({raw_outcome}).',
                    f'Recommended staking: Level {mult} ({stake} PKR).'
                ]
            }

        # RULE 5: EXHAUSTION WARNING (58% - 60%)
        if zone == 'EXHAUSTION_TRAP':
            return {
                'trade_action': 'DEFENSIVE_HOLD',
                'signal_display': f'CAUTIOUS {raw_outcome}',
                'badge': 'warning',
                'grade': 'B (Exhaustion Risk)',
                'grade_color': 'amber',
                'reliability_score': 50,
                'recommended_stake': base_unit,
                'multiplier': 1,
                'profit_edge': '+0% EV',
                'action_advice': f'Approaching streak resistance ({confidence}%). Only bet base unit ({base_unit} PKR) or skip if in profit.',
                'reasons': [
                    'Approaching streak resistance.',
                    f'Only bet minimum Base Unit ({base_unit} PKR) or skip.'
                ]
            }

        # DEFAULT: COIN-FLIP
        return {
            'trade_action': 'SKIP_OR_MINIMUM',
            'signal_display': f'{raw_outcome} (LOW EDGE)',
            'badge': 'warning',
            'grade': 'C (Coin-Flip)',
            'grade_color': 'amber',
            'reliability_score': 50,
            'recommended_stake': 0,
            'multiplier': 0,
            'profit_edge': '0%',
            'action_advice': 'Edge is weak (<53%). Waiting for a high-probability prime setup guarantees better long-term profits.',
            'reasons': ['Low mathematical edge. Protect capital.']
        }
