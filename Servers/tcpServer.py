# tcp_message_server.py
import base64
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
        buffer = ""
        try:
            while True:
                data = self.request.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data

                lines = buffer.split('\n')
                buffer = lines[-1]
                for line in lines[:-1]:
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                        self.processMessage(msg)
                    except json.JSONDecodeError as e:
                        print(f"[JSON ERROR] {e} // line: {line[:80]}")


        except ConnectionResetError:
            pass
        finally:
            if self.user_id in connected_clients:
                del connected_clients[self.user_id]
                print(f"[TCP] {self.user_id} disconnected.")

    def processMessage(self, msg):
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

            attachment_data = msg.get('attachment')
            attachment_name = msg.get('attachment_name')
            attachment_blob = None

            print(f"[TCP] primljena poruka je {ID}, {content}, {sender}, {receiver}, {timestamp}")

            if attachment_data:
                try:
                    attachment_blob = base64.b64decode(attachment_data)
                    print(f"[DEBUG] Attachment type: {type(attachment_blob)} // size: {len(attachment_blob)}")
                except Exception as e:
                    print(f"[TCP ERROR] Neuspjelo dekodiranje attachmenta: {e}")
                    attachment_blob = None
                    attachment_name = None

            def after_insert(_):
                print("[TCP] dobro upisano u bazu, pošalji natrag obavijest")
                if receiver in connected_clients:
                    try:
                        connected_clients[receiver].sendall(json.dumps({
                            'type': 'new_message',
                            'from': sender
                        }).encode('utf-8'))
                        print(f"[TCP] Obavijest poslana {receiver}")
                    except Exception as e:
                        print(f"[TCP ERROR] Slanje nije uspjelo: {e}")

            DatabaseManager.instance().insertNewChatMessage(
                ID, content, sender, receiver, timestamp,
                attachment_blob, attachment_name,
                callback=after_insert
            )


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9010
    with socketserver.ThreadingTCPServer((HOST, PORT), MessageHandler) as server:
        print(f"[TCP] server pokrenut na portu {PORT}")
        server.serve_forever()
