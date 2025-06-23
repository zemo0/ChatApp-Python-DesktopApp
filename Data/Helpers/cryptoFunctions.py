import hashlib
import os
import random
import sys
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
import base64
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from config import AES_KEY, AES_IV
from Crypto.Util.Padding import unpad, pad
possible_peppers = ["Kotanyi", "Franck", "Sallant", "Sana", "Crni"]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# OVO NE KORISTIT VIŠE, SAMO JEDAN PUT JE POTREBNO
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#def generate_rsa_keys():
#    key = RSA.generate(2048)
#    with open("Files/private_key.pem", "wb") as private_file:
#        private_file.write(key.export_key())
#    with open("Files/public_key.pem", "wb") as public_file:
#        public_file.write(key.publickey().export_key())

#RSA za ideve
def encryptRSA(plain_text: str):
    with open("files/public_key.pem", "rb") as pub_file:
        public_key = RSA.import_key(pub_file.read())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted = cipher_rsa.encrypt(plain_text.encode())

    return base64.b64encode(encrypted).decode()

def hashSHA256(id:str):
    primary_key = hashlib.sha256(id.encode()).hexdigest()
    return primary_key

def prepId(var:str):
    encryptedId = encryptRSA(var)
    hashedId = hashSHA256(encryptedId)
    return hashedId

# AES za lozinke
def encryptAES(plain_text: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode()

def decryptAES(encrypted_b64: str) -> str:
    encrypted_bytes = base64.b64decode(encrypted_b64)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted.decode()

def encryptThenHash(password: str, username: str) -> str:
    salt = username[::-1]
    pepper = random.choice(possible_peppers)
    combined = pepper + password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def verifyPassword(input_password, username, stored_hash):
    salt = username[::-1]
    for pepper in possible_peppers:
        combined = pepper + input_password + salt
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        if hashed == stored_hash:
            return True
    return False