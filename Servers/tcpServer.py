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
        buffer = b""
        try:
            while True:
                #socket veza koja prima 4096 bajtova
                data = self.request.recv(4096)
                if not data:
                    break
                buffer += data

                while b'\n' in buffer:
                    #podjeli json i attachment
                    line, buffer = buffer.split(b'\n', 1)
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line.decode('utf-8'))
                        if msg.get('has_attachment'):
                            print("Poruka ima attachment")
                            expected = msg['attachment_size']
                            print(f"Ocekivana velicina je {expected}")
                            while len(buffer) < expected:
                                #ako attachment jos nije stigao nastavi citati podatke s klijenta
                                buffer += self.request.recv(4096)
                            #attachment podataka je velicina koja ocekujemo u bufferu 0 -> len(attachment_size
                            attachment_blob = buffer[:expected]
                            buffer = buffer[expected:]
                        else:
                            attachment_blob = None
                        self.processMessage(msg, attachment_blob)
                    except json.JSONDecodeError as e:
                        print(f"Greška s JSONom na serveru, {e}")
        except ConnectionResetError:
            pass
        finally:
            if self.user_id in connected_clients:
                del connected_clients[self.user_id]
                print(f"[TCP] {self.user_id} se odspojio.")

    def processMessage(self, msg, attachment_blob):
        if msg['type'] == 'register':
            self.user_id = msg['user_id']
            connected_clients[self.user_id] = self.request
            print(f"[TCP] {self.user_id} se spojio.")

        elif msg['type'] == 'chat_message':
            ID = msg['message_id']
            content = msg['content']
            sender = msg['from']
            receiver = msg['to']
            timestamp = datetime.fromisoformat(msg['timestamp'])
            attachment_name = msg.get('attachment_name')

            print(f"[TCP] primljena poruka je {ID}, {content}, {sender}, {receiver}, {timestamp}")

            def after_insert(_):
                print("[TCP] Poruka spremljena u bazu.")
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
