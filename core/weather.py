import json
import urllib.request
import threading
from PyQt5.QtCore import QTimer

class WeatherService:
    def __init__(self, window, enabled=False):
        self.window = window
        self.enabled = enabled
        self.condition = "clear"
        self.timer = QTimer(window)
        self.timer.timeout.connect(self.fetch_weather)
        if self.enabled:
            self.fetch_weather()
            self.timer.start(3600 * 1000) # Every hour
            
    def fetch_weather(self):
        if not self.enabled:
            return
            
        def _fetch():
            try:
                # 1. Get location from IP
                req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    ip_data = json.loads(response.read())
                    lat = ip_data.get('lat', 0)
                    lon = ip_data.get('lon', 0)
                    
                # 2. Get weather from Open-Meteo
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                req2 = urllib.request.Request(weather_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=5) as response2:
                    weather_data = json.loads(response2.read())
                    code = weather_data.get('current_weather', {}).get('weathercode', 0)
                    
                    # Map WMO weather codes to simple conditions
                    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                        self.condition = "rain"
                    elif code in [71, 73, 75, 85, 86]:
                        self.condition = "snow"
                    else:
                        self.condition = "clear"
            except Exception as e:
                print(f"Weather fetch failed: {e}")
                
        threading.Thread(target=_fetch, daemon=True).start()
