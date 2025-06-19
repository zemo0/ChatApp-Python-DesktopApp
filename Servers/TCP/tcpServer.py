import socket
import threading

online_users = set()
clients = []

def broadcast_online_status(new_user_id, exclude=None):
    for client in clients:
        if client is not exclude:
            try:
                client.sendall(f"ONLINE:{new_user_id}".encode())
            except Exception as e:
                print(f"[ERROR] Neuspjelo slanje poruke klijentu: {e}")

def handle_client(conn, addr):
    clients.append(conn)
    user_id = None
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("ONLINE:"):
                user_id = data.split(":", 1)[1]
                online_users.add(user_id)
                print(f"[INFO] Korisnik {user_id} je online")
                for client in clients:
                    if client is not conn:
                        try:
                            client.sendall(f"ONLINE:{user_id}".encode())
                        except Exception as e:
                            print(f"[ERROR] Slanje poruke klijentu neuspjelo: {e}")

            elif data.startswith("CHECK:"):
                check_id = data.split(":", 1)[1]
                if check_id in online_users:
                    status = "ONLINE"
                else:
                    status = "OFFLINE"
                conn.sendall(status.encode())

            elif data.startswith("LIST_ONLINE"):
                conn.sendall(",".join(online_users).encode())

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if conn in clients:
            clients.remove(conn)
        if user_id in online_users:
            online_users.remove(user_id)
            print(f"[INFO] Korisnik {user_id} je offline")
            for client in clients:
                try:
                    client.sendall(f"OFFLINE:{user_id}".encode())
                except Exception as e:
                    print(f"[ERROR] Slanje OFFLINE poruke neuspjelo: {e}")
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9010))
    server.listen()
    print("[SERVER] TCP server pokrenut na portu 9010")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
