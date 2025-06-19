import socket
import threading
import time

online_users = set()
user_addresses = {}
lock = threading.Lock()

def handle_message(message, addr, server_socket):
    global online_users, user_addresses

    with lock:
        if message.startswith("ONLINE:"):
            user_id = message.split(":", 1)[1]
            online_users.add(user_id)
            user_addresses[user_id] = addr
            print(f"[UDP] {user_id} @ {addr}")
            for uid, uaddr in user_addresses.items():
                if uid != user_id:
                    server_socket.sendto(f"ONLINE:{user_id}".encode(), uaddr)

        elif message.startswith("OFFLINE:"):
            user_id = message.split(":", 1)[1]
            if user_id in online_users:
                online_users.remove(user_id)
                user_addresses.pop(user_id, None)
                print(f"[UDP] {user_id}")

                for uaddr in user_addresses.values():
                    server_socket.sendto(f"OFFLINE:{user_id}".encode(), uaddr)

        elif message.startswith("LIST_ONLINE"):
            online_list = ",".join(online_users)
            server_socket.sendto(online_list.encode(), addr)

def start_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", 9030))
    print("[UDP] Status server pokrenut na portu 9030")

    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            message = data.decode()
            threading.Thread(
                target=handle_message,
                args=(message, addr, server_socket),
                daemon=True
            ).start()
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    start_udp_server()