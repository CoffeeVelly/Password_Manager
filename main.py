import tkinter as tk
from tkinter import ttk, messagebox
from manager import PasswordManager

class PasswordManagerApp:
    def __init__(self, root):
        self.manager = PasswordManager()
        self.root = root
        self.root.title("密码管理器")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 11))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        # 网站
        ttk.Label(frame, text="网站：").grid(row=0, column=0, sticky="w", pady=5)
        self.website_entry = ttk.Entry(frame, width=33)
        self.website_entry.grid(row=0, column=1, pady=5, sticky="w")

        # 用户名
        ttk.Label(frame, text="用户名：").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=33)
        self.username_entry.grid(row=1, column=1, pady=5, sticky="w")

        # 密码
        ttk.Label(frame, text="密码：").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=33, show="●")
        self.password_entry.grid(row=2, column=1, pady=5, sticky="w")

        self.show_pw_btn = ttk.Button(frame, text="👁", width=4, command=self.toggle_password_entry)
        self.show_pw_btn.grid(row=2, column=2, padx=5, sticky="e")



        # 第3行：三个按钮横向排列
        ttk.Button(frame, text="生成强密码", command=self.generate_password).grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="保存密码", command=self.save_password).grid(row=3, column=1, pady=10)
        ttk.Button(frame, text="查找密码", command=self.search_password).grid(row=3, column=2, pady=10)

        # 第4行：删除按钮放在左边，显示所有记录按钮占中间两列
        ttk.Button(frame, text="删除密码", command=self.delete_password).grid(row=4, column=0, pady=5)
        ttk.Button(frame, text="显示所有记录", command=self.show_all_passwords).grid(row=4, column=1, pady=5)
        ttk.Button(frame, text="导出密码", command=self.export_passwords).grid(row=4, column=2, pady=5)

        ttk.Button(frame, text="检测密码泄露", command=self.check_leak).grid(row=5, column=1, pady=5)

    def toggle_password_entry(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.config(show="●")
            self.show_pw_btn.config(text="👁")
        else:
            self.password_entry.config(show="")
            self.show_pw_btn.config(text="🙈")

    def generate_password(self):
        password = self.manager.generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def save_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if website and username and password:
            self.manager.add_password(website, username, password)
            messagebox.showinfo("成功", f"{website} 的密码已保存")
        else:
            messagebox.showwarning("错误", "请填写完整信息")

    def search_password(self):
        website = self.website_entry.get()
        result = self.manager.get_password(website)
        if result:
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.username_entry.insert(0, result["username"])
            self.password_entry.insert(0, result["password"])
        else:
            messagebox.showinfo("提示", "未找到该网站的密码")

    def delete_password(self):
        website = self.website_entry.get()
        if self.manager.delete_password(website):
            messagebox.showinfo("成功", f"{website} 的密码已删除")
            self.website_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("提示", "未找到该网站的密码")

    def show_all_passwords(self):
        window = tk.Toplevel(self.root)
        window.title("所有密码记录")
        window.geometry("500x300")
        window.resizable(False, False)

        canvas = tk.Canvas(window)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, (website, data) in enumerate(self.manager.passwords.items()):
            ttk.Label(scrollable_frame, text=website).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(scrollable_frame, text=data['username']).grid(row=i, column=1, padx=5, pady=5, sticky="w")

            password_var = tk.StringVar(value='●' * len(data['password']))
            password_label = ttk.Label(scrollable_frame, textvariable=password_var)
            password_label.grid(row=i, column=2, padx=5, pady=5)

            def toggle(pwd=data['password'], var=password_var, btn=None):
                if var.get().startswith('●'):
                    var.set(pwd)
                    if btn: btn.config(text="隐藏")
                else:
                    var.set('●' * len(pwd))
                    if btn: btn.config(text="显示")

            btn = ttk.Button(scrollable_frame, text="显示")
            btn.grid(row=i, column=3, padx=5, pady=5)
            btn.config(command=lambda p=data['password'], v=password_var, b=btn: toggle(p, v, b))

    def export_passwords(self):
        self.manager.export_passwords()

    def check_leak(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("提示", "请输入要检查的密码")
            return

        count = self.manager.check_password_leak(password)
        if count == -1:
            messagebox.showerror("错误", "检查失败，请稍后再试")
        elif count == 0:
            messagebox.showinfo("安全", "该密码未出现在已知泄露数据库中")
        else:
            messagebox.showwarning("警告", f"该密码已泄露 {count} 次，建议更换密码")




if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
