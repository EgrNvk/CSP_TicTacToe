from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key)


import hashlib
password=input("Enter your password:")
print(hashlib.sha256(password.encode()).hexdigest())
