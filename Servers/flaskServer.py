import os
import sys
import threading

from flask import Flask, request, jsonify

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from Data.Helpers import cryptoFunctions
from Data.database import DatabaseManager

app = Flask(__name__)

dbManager = DatabaseManager.instance()
def get_role_by_id(user_id):
    result_holder = {"role": None}
    event = threading.Event()

    def callback(role):
        result_holder["role"] = role
        event.set()

    dbManager.getUserRoleById(user_id, callback)
    event.wait()
    return result_holder["role"]

@app.route("/api/get_role", methods=["GET"])
def get_role():
    user_id = request.args.get("user_id")
    role = get_role_by_id(user_id)

    if role:
        return jsonify({"role": role}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    event = threading.Event()
    login_success = {"ok": False}

    def callback(users):
        for (db_username, db_password) in users:
            if db_username == username and cryptoFunctions.verifyPassword(password, username,  db_password):
                login_success["ok"] = True
                break
        event.set()

    dbManager.getUsersInfo("nameAndPassword", callback)
    event.wait()

    if login_success["ok"]:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    event = threading.Event()
    result = {"affected": None}

    def callback(affected_rows):
        result["affected"] = affected_rows
        event.set()

    dbManager.deleteUserById(user_id, callback)
    event.wait()

    if result["affected"] == 0:
        return jsonify({'error': 'Korisnik nije pronađen.'}), 404
    elif result["affected"] > 0:
        return jsonify({'message': 'Korisnik obrisan.'}), 200
    else:
        return jsonify({'error': 'Greška pri brisanju korisnika.'}), 500

@app.route('/api/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    event = threading.Event()
    result = {"affected": None}

    def callback(affected_rows):
        result["affected"] = affected_rows
        event.set()

    dbManager.updateUserById(user_id, data, callback)
    event.wait()

    if result["affected"] == 0:
        return jsonify({'error': 'Korisnik nije pronađen.'}), 404
    elif result["affected"] > 0:
        return jsonify({'message': 'Korisnik ažuriran.'}), 200
    else:
        return jsonify({'error': 'Greška pri ažuriranju korisnika.'}), 500

if __name__ == "__main__":
    app.run(debug=True)