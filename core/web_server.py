import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
from core.characters import get_character_config, CHARACTER_PROFILES

# Global rate limiting dictionary mapping endpoints to timestamps
LAST_REQUEST_TIME = {}

class PetRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                import sys
                import os
                base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                if not getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(base_path)
                with open(os.path.join(base_path, 'ui/dashboard.html'), 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(b"Error loading dashboard.html")
        elif self.path == '/api/info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            char_id = getattr(self.server.pet_window, 'current_character', 'dragon')
            config = get_character_config(char_id)
            
            characters_list = [
                {
                    "id": cid,
                    "name": cid,
                    "display_name": prof.get("name", cid),
                    "type": prof.get("type", "generic"),
                    "supported_actions": prof.get("supported_actions", [])
                }
                for cid, prof in CHARACTER_PROFILES.items()
            ]
            
            response_body = {
                "status": "ok",
                "character": char_id,
                "supported_actions": config.get("supported_actions", []),
                "characters": characters_list,
                "is_stopped": getattr(self.server.pet_window, 'is_stopped', False),
                "sleep_on_video": getattr(self.server.pet_window.mood, 'sleep_on_video', True)
            }
            self.wfile.write(json.dumps(response_body).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}

        # The HTTP server runs on a background thread.
        # We must use QMetaObject.invokeMethod to safely call methods on the pet window (main thread).
        
        if self.path == '/api/force_state':
            state = data.get('state', 'idle')
            QMetaObject.invokeMethod(self.server.pet_window, "trigger_anim_safe", Qt.QueuedConnection, Q_ARG(str, state))
            
        elif self.path == '/api/say':
            msg = data.get('message', '')
            QMetaObject.invokeMethod(self.server.pet_window, "say_safe", Qt.QueuedConnection, Q_ARG(str, msg))
            
        elif self.path == '/api/chat':
            # Rate limiting: 1 second minimum between chat requests
            now = time.time()
            if now - LAST_REQUEST_TIME.get('/api/chat', 0) < 1.0:
                self.send_error(429, "Too Many Requests")
                return
            LAST_REQUEST_TIME['/api/chat'] = now
            
            # Payload validation
            if content_length > 2048:
                self.send_error(413, "Payload Too Large")
                return
                
            msg = data.get('message', '')
            if not isinstance(msg, str) or not msg.strip():
                self.send_error(400, "Bad Request")
                return
                
            QMetaObject.invokeMethod(self.server.pet_window, "process_chat_safe", Qt.QueuedConnection, Q_ARG(str, msg))
            
        elif self.path == '/api/clear_chat':
            # Use QMetaObject since clear_memory touches nothing in UI directly but good for thread safety
            # Wait, clear_memory() is inside ai_companion. But we can invoke a new safe method on pet_window.
            # I will add clear_chat_safe to chibi_window, or just invoke lambda?
            # QMetaObject doesn't allow lambda easily. We'll add clear_chat_safe to chibi_window next.
            QMetaObject.invokeMethod(self.server.pet_window, "clear_chat_safe", Qt.QueuedConnection)
            
        elif self.path == '/api/pomodoro':
            action = data.get('action')
            if action == 'start':
                work = int(data.get('work', 25))
                brk = int(data.get('break', 5))
                QMetaObject.invokeMethod(self.server.pet_window, "start_pomo_safe", Qt.QueuedConnection, Q_ARG(int, work), Q_ARG(int, brk))
            elif action == 'stop':
                QMetaObject.invokeMethod(self.server.pet_window, "stop_pomo_safe", Qt.QueuedConnection)
                
        elif self.path == '/api/mood':
            action = data.get('action')
            if action == 'feed':
                QMetaObject.invokeMethod(self.server.pet_window, "feed_safe", Qt.QueuedConnection)
            elif action == 'annoy':
                QMetaObject.invokeMethod(self.server.pet_window, "annoy_safe", Qt.QueuedConnection)
            elif action == 'sleep':
                QMetaObject.invokeMethod(self.server.pet_window, "sleep_safe", Qt.QueuedConnection)

        elif self.path == '/api/character':
            char = data.get('character', 'dragon')
            QMetaObject.invokeMethod(self.server.pet_window, "switch_character_safe", Qt.QueuedConnection, Q_ARG(str, char))

        elif self.path == '/api/settings':
            wander = float(data.get('wander_chance', 0.02))
            QMetaObject.invokeMethod(self.server.pet_window, "update_wander_safe", Qt.QueuedConnection, Q_ARG(float, wander))
            
        elif self.path == '/api/pet_power':
            action = data.get('action')
            if action == 'start':
                QMetaObject.invokeMethod(self.server.pet_window, "start_pet_safe", Qt.BlockingQueuedConnection)
            elif action == 'stop':
                QMetaObject.invokeMethod(self.server.pet_window, "stop_pet_safe", Qt.BlockingQueuedConnection)

        elif self.path == '/api/video_sleep':
            enabled = bool(data.get('enable', True))
            QMetaObject.invokeMethod(self.server.pet_window, "set_video_sleep_safe", Qt.QueuedConnection, Q_ARG(bool, enabled))

        elif self.path == '/api/autostart':
            from core.autostart import enable_autostart, disable_autostart
            enable = data.get('enable', False)
            if enable:
                enable_autostart()
            else:
                disable_autostart()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Allow CORS if needed
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response_body = {
            "status": "ok",
            "is_stopped": getattr(self.server.pet_window, 'is_stopped', False),
            "sleep_on_video": getattr(self.server.pet_window.mood, 'sleep_on_video', True)
        }
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
        
    def log_message(self, format, *args):
        # Suppress logging to keep console clean
        pass

class PetWebServer:
    def __init__(self, pet_window, port=8080):
        self.pet_window = pet_window
        self.port = port
        self.server = None
        for p in [port, port + 1, port + 2]:
            try:
                self.server = HTTPServer(('127.0.0.1', p), PetRequestHandler)
                self.port = p
                break
            except OSError:
                continue
        if self.server:
            self.server.pet_window = self.pet_window
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            print(f"Web dashboard running at http://localhost:{self.port}")
