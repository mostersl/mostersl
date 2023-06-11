import base64
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def rsa_encrypt(message):
    message = bytes(message, encoding='utf-8')
    with open('./cache/op.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = PKCS1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(message))
        return cipher_text

