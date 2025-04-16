import hashlib
import os
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# OVO NE KORISTIT VIŠE, SAMO JEDAN PUT JE POTREBNO
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#def generate_rsa_keys():
#    key = RSA.generate(2048)
#    with open("Files/private_key.pem", "wb") as private_file:
#        private_file.write(key.export_key())
#    with open("Files/public_key.pem", "wb") as public_file:
#        public_file.write(key.publickey().export_key())

def encrypt_rsa(plain_text: str):
    with open("files/public_key.pem", "rb") as pub_file:
        public_key = RSA.import_key(pub_file.read())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted = cipher_rsa.encrypt(plain_text.encode())

    return base64.b64encode(encrypted).decode()

def decrypt_rsa(encrypted_text: str):
    with open("files/private_key.pem", "rb") as priv_file:
        private_key = RSA.import_key(priv_file.read())

    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted = cipher_rsa.decrypt(base64.b64decode(encrypted_text))

    return decrypted.decode()

def hashTheId(id:str):
    primary_key = hashlib.sha256(id.encode()).hexdigest()
    return primary_key

def prepId(id:str):
    encryptedId = encrypt_rsa(id)
    hashedId = hashTheId(encryptedId)
    return hashedId