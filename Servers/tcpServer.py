# tcp_message_server.py
import json
import os
import socketserver
import sys
from datetime import datetime
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from Data.database import DatabaseManager



connected_clients = {}

class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.user_id = None
        try:
            while True:
                data = self.request.recv(4096).decode('utf-8')
                if not data:
                    break
                msg = json.loads(data)

                if msg['type'] == 'register':
                    self.user_id = msg['user_id']
                    connected_clients[self.user_id] = self.request
                    print(f"[TCP] {self.user_id} connected.")

                elif msg['type'] == 'chat_message':
                    ID = msg['message_id']
                    content = msg['content']
                    sender = msg['from']
                    receiver = msg['to']
                    timestamp = datetime.fromisoformat(msg['timestamp'])
                    def after_insert(_):
                        if receiver in connected_clients:
                            try:
                                connected_clients[receiver].sendall(json.dumps({
                                    'type': 'new_message',
                                    'from': sender
                                }).encode('utf-8'))
                                print(f"[TCP] Obavijest poslana {receiver}")
                            except Exception as e:
                                print(f"[TCP ERROR] Slanje nije uspjelo: {e}")

                    DatabaseManager.instance().insertNewChatMessage(ID, content, sender, receiver, timestamp, callback=after_insert)

        except ConnectionResetError:
            pass
        finally:
            if self.user_id in connected_clients:
                del connected_clients[self.user_id]
                print(f"[TCP] {self.user_id} disconnected.")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9010
    with socketserver.ThreadingTCPServer((HOST, PORT), MessageHandler) as server:
        print(f"[TCP] server pokrenut na portu {PORT}")
        server.serve_forever()
