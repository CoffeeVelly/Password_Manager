import os
import json
import string
import random
from cryptography.fernet import Fernet
from utils import load_key
import csv
import requests
import hashlib
import numpy as np
import pandas as pd

class PasswordManager:
    def __init__(self):
        self.key = load_key()
        self.cipher = Fernet(self.key)
        self.data_file = "passwords.json"
        self.passwords = self.load_passwords()

    def load_passwords(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "rb") as f:
                encrypted = f.read()
            decrypted = self.cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        else:
            return {}

    def save_passwords(self):
        with open(self.data_file, "wb") as f:
            encrypted = self.cipher.encrypt(json.dumps(self.passwords).encode())
            f.write(encrypted)

    def add_password(self, website, username, password):
        # encrypted_password = self.cipher.encrypt(password.encode()).decode()
        self.passwords[website] = {"username": username, "password": password}
        self.save_passwords()

    def get_password(self, website):
        return self.passwords.get(website)

    def delete_password(self, website):
        if website in self.passwords:
            del self.passwords[website]
            self.save_passwords()
            return True
        return False

    def generate_password(self, length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))

    def export_passwords(self, filename="passwords.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Website", "Username", "Password"])
            for website, data in self.passwords.items():
                writer.writerow([website, data["username"], data["password"]])
        print(f"密码已成功导出为 CSV 到 {filename}")

    def check_password_leak(self, password):
        """检查密码是否被泄露（使用 Have I Been Pwned 的 k-Anonymity 机制）"""
        sha1_pw = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_pw[:5]
        suffix = sha1_pw[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise RuntimeError("无法访问泄露检测服务")

            hashes = (line.split(':') for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
            return 0
        except Exception as e:
            print("检查泄露失败：", e)
            return -1

    def get_password_lengths(self):
        """获取所有保存密码的长度列表"""
        lengths = [len(data["password"]) for data in self.passwords.values()]
        return np.array(lengths)

    def analyze_password_strength(self):
        """分析密码长度的统计信息"""
        lengths = self.get_password_lengths()
        if len(lengths) == 0:
            return None, None, None, None, None

        min_len = np.min(lengths)
        max_len = np.max(lengths)
        avg_len = np.mean(lengths)
        median_len = np.median(lengths)
        std_dev = np.std(lengths)

        return min_len, max_len, avg_len, median_len, std_dev

    def get_passwords_dataframe(self):
        """将密码数据转换为 Pandas DataFrame"""
        if not self.passwords:
            return pd.DataFrame(columns=['Website', 'Username', 'Password', 'PasswordLength'])

        data_list = []
        for website, data in self.passwords.items():
            data_list.append({
                'Website': website,
                'Username': data['username'],
                'Password': data['password'],
                'PasswordLength': len(data['password'])
            })
        return pd.DataFrame(data_list)