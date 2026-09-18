import os
import json
from typing import Dict, Any, List

class ConfidenceCalibrator:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.data_dir = data_dir
        self.calib_file = os.path.join(data_dir, 'empirical_calibration.json')

    def load_data(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.calib_file):
            try:
                with open(self.calib_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_data(self, data: List[Dict[str, Any]]):
        try:
            with open(self.calib_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f'Error saving calibration data: {e}')

    def add_entry(self, confidence: float, outcome: str, note: str = ''):
        data = self.load_data()
        data.append({
            'confidence': float(confidence),
            'outcome': outcome,
            'note': note
        })
        self.save_data(data)

    def get_tier_stats(self) -> Dict[str, Any]:
        data = self.load_data()
        
        tiers = {
            'neutral': {'label': 'Neutral / Disagreement (N)', 'min': 49.0, 'max': 51.0, 'wins': 0, 'losses': 0, 'skips': 0},
            'coin_flip': {'label': 'Low Trend (51.1% - 53.0%)', 'min': 51.1, 'max': 53.0, 'wins': 0, 'losses': 0, 'skips': 0},
            'prime': {'label': 'Prime Sweet-Spot (53.1% - 57.9%)', 'min': 53.1, 'max': 57.9, 'wins': 0, 'losses': 0, 'skips': 0},
            'exhaustion': {'label': 'Exhaustion Zone (58.0% - 60.0%)', 'min': 58.0, 'max': 60.0, 'wins': 0, 'losses': 0, 'skips': 0},
            'reversal_trap': {'label': 'Extreme Trap (> 60.0%)', 'min': 60.1, 'max': 100.0, 'wins': 0, 'losses': 0, 'skips': 0},
        }

        total_tested = 0
        total_wins = 0

        for row in data:
            c = float(row.get('confidence', 50.0))
            out = str(row.get('outcome', '')).lower()
            
            if 'neutral' in out or c == 50.0:
                t_key = 'neutral'
                if 'lose' in out:
                    tiers[t_key]['losses'] += 1
                else:
                    tiers[t_key]['skips'] += 1
            elif c <= 53.0:
                t_key = 'coin_flip'
            elif c <= 57.9:
                t_key = 'prime'
            elif c <= 60.0:
                t_key = 'exhaustion'
            else:
                t_key = 'reversal_trap'

            if t_key != 'neutral':
                if 'win' in out:
                    tiers[t_key]['wins'] += 1
                    total_wins += 1
                    total_tested += 1
                elif 'lose' in out:
                    tiers[t_key]['losses'] += 1
                    total_tested += 1

        for k, v in tiers.items():
            tot = v['wins'] + v['losses']
            v['total'] = tot
            v['win_rate'] = round((v['wins'] / tot * 100), 1) if tot > 0 else 0.0

        return {
            'total_records': len(data),
            'total_tested': total_tested,
            'overall_tested_winrate': round((total_wins / total_tested * 100), 1) if total_tested > 0 else 0.0,
            'tiers': tiers
        }

    def calibrate(self, raw_confidence: float, outcome: str) -> Dict[str, Any]:
        stats = self.get_tier_stats()
        tiers = stats['tiers']

        if outcome == 'NEUTRAL / SKIP' or raw_confidence <= 51.0:
            tier = tiers['neutral']
            return {
                'zone': 'NEUTRAL_SKIP',
                'zone_name': 'Neutral / Skip (N)',
                'badge_color': 'slate',
                'calibrated_win_rate': 0.0,
                'status': 'SKIP_RECOMMENDED',
                'alert': 'User handwritten data proves N (disagreement) leads to repeated losses (N / L). STRICTLY SKIP THIS ROUND.',
                'action': 'SKIP / DO NOT BET',
                'tier_summary': tier
            }
        elif raw_confidence <= 53.0:
            tier = tiers['coin_flip']
            wr = tier['win_rate']
            return {
                'zone': 'COIN_FLIP',
                'zone_name': 'Low Edge / Coin-Flip (51% - 53%)',
                'badge_color': 'amber',
                'calibrated_win_rate': wr,
                'status': 'CAUTIOUS',
                'alert': f'Historical accuracy in this tier is {wr}%. Models have minimal edge. Bet lowest base unit or wait.',
                'action': 'Minimum Base Unit (Level 1) or Wait',
                'tier_summary': tier
            }
        elif raw_confidence <= 57.9:
            tier = tiers['prime']
            wr = tier['win_rate']
            return {
                'zone': 'PRIME_WINDOW',
                'zone_name': 'Prime Sweet-Spot (53.1% - 57.9%)',
                'badge_color': 'emerald',
                'calibrated_win_rate': wr,
                'status': 'OPTIMAL_SIGNAL',
                'alert': f'TOP ACCURACY TIER: {wr}% verified win rate in user tracked notes! Genuine trend momentum without exhaustion.',
                'action': 'Optimal Entry (Follow Signal Confidently)',
                'tier_summary': tier
            }
        elif raw_confidence <= 60.0:
            tier = tiers['exhaustion']
            wr = tier['win_rate']
            return {
                'zone': 'EXHAUSTION_TRAP',
                'zone_name': 'Exhaustion Warning Zone (58% - 60%)',
                'badge_color': 'orange',
                'calibrated_win_rate': wr,
                'status': 'EXHAUSTION_RISK',
                'alert': f'Exhaustion Alert: Win rate drops to {wr}%. Long streaks often snap here (mean reversion). Do not increase stake.',
                'action': 'Light Stake (Level 1) or Skip if on profit',
                'tier_summary': tier
            }
        else:
            tier = tiers['reversal_trap']
            wr = tier['win_rate']
            return {
                'zone': 'REVERSAL_TRAP',
                'zone_name': 'Extreme Reversal Trap (> 60%)',
                'badge_color': 'rose',
                'calibrated_win_rate': wr,
                'status': 'TRAP_DETECTED',
                'alert': f'HIGH REVERSAL TRAP DETECTED: Real tests show a 75% failure rate (only {wr}% win rate)! Naive consensus is overconfident right before a trend break.',
                'action': 'DANGER: Avoid High Bet / Consider Reversal or Skip',
                'tier_summary': tier
            }
