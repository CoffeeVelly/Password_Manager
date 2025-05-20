from cryptography.fernet import Fernet

def generate_key():
    """生成一个新的加密密钥"""
    return Fernet.generate_key()

def load_key():
    """从文件加载加密密钥"""
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("密钥文件未找到，创建一个新的密钥")
        key = generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key
