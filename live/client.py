"""
Live 92PKR Win Go API Client.
Communicates directly with the 92PKR real-time game gateway to fetch live countdowns,
active period numbers, and historical draws with automated MD5 signature generation.
"""
import requests
import json
import time
import uuid
import hashlib
import urllib3
from typing import Dict, Any, List, Optional

urllib3.disable_warnings()

GAME_TYPES = {
    "1m": {"typeId": 1, "name": "Win Go 1 Min", "interval": 60},
    "30s": {"typeId": 30, "name": "Win Go 30 Sec", "interval": 30},
    "3m": {"typeId": 2, "name": "Win Go 3 Min", "interval": 180},
    "5m": {"typeId": 3, "name": "Win Go 5 Min", "interval": 300}
}


class PKR92LiveClient:
    def __init__(self, base_url: str = "https://92pkrapi.com/api/webapi"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://www.92pkr1.com',
            'Referer': 'https://www.92pkr1.com/'
        }

    def _sign_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        t = dict(data)
        t.pop("signature", None)
        t.pop("timestamp", None)
        t["language"] = 0
        t["random"] = uuid.uuid4().hex

        # Exclude internal non-signed keys
        kce = ["signature", "track", "xosoBettingData"]
        sorted_dict = {
            k: t[k] for k in sorted(t.keys())
            if t[k] is not None and t[k] != "" and k not in kce
        }
        json_str = json.dumps(sorted_dict, separators=(',', ':'))
        t["signature"] = hashlib.md5(json_str.encode('utf-8')).hexdigest().upper()
        t["timestamp"] = int(time.time())
        return t

    def get_game_issue(self, game_key: str = "1m") -> Optional[Dict[str, Any]]:
        """
        Fetches the current active issue number and countdown remaining.
        """
        cfg = GAME_TYPES.get(game_key, GAME_TYPES["1m"])
        payload = self._sign_payload({"typeId": cfg["typeId"]})
        try:
            r = requests.post(f"{self.base_url}/GetGameIssue", json=payload, headers=self.headers, timeout=6, verify=False)
            if r.status_code == 200:
                res = r.json()
                if res.get("code") == 0 and "data" in res:
                    data = res["data"]
                    # Calculate remaining seconds
                    return {
                        "success": True,
                        "game_key": game_key,
                        "game_name": cfg["name"],
                        "issueNumber": data.get("issueNumber"),
                        "startTime": data.get("startTime"),
                        "endTime": data.get("endTime"),
                        "serviceTime": data.get("serviceTime"),
                        "intervalM": data.get("intervalM")
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": "Invalid response"}

    def get_history_draws(self, game_key: str = "1m", page_size: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches the latest completed rounds (period, winning number, color, big/small).
        Returns clean records sorted chronologically: oldest first, newest last.
        """
        cfg = GAME_TYPES.get(game_key, GAME_TYPES["1m"])
        payload = self._sign_payload({
            "typeId": cfg["typeId"],
            "pageSize": page_size,
            "pageNo": 1
        })

        try:
            r = requests.post(f"{self.base_url}/GetNoaverageEmerdList", json=payload, headers=self.headers, timeout=8, verify=False)
            if r.status_code == 200:
                res = r.json()
                if res.get("code") == 0 and "data" in res:
                    raw_list = res["data"].get("list", [])
                    records = []
                    for item in raw_list:
                        period = str(item.get("issueNumber", "")).strip()
                        num_str = str(item.get("number", "")).strip()
                        if not period or not num_str.isdigit():
                            continue
                        number = int(num_str)
                        size = "Big" if number >= 5 else "Small"
                        raw_color = str(item.get("colour", "")).lower()
                        if "violet" in raw_color or number in [0, 5]:
                            color = "Violet"
                        elif "green" in raw_color or number in [1, 3, 7, 9]:
                            color = "Green"
                        else:
                            color = "Red"

                        records.append({
                            "period": period,
                            "number": number,
                            "size": size,
                            "color": color
                        })

                    # The API returns newest first. Reverse so oldest is at index 0 and newest at index -1
                    records.reverse()
                    return records
        except Exception as e:
            print(f"Error fetching live draws: {e}")
        return []
