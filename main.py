import tkinter as tk
from tkinter import ttk, messagebox
from manager import PasswordManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PasswordManagerApp:
    def __init__(self, root):
        self.manager = PasswordManager()
        self.root = root
        self.root.title("密码管理器")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 11))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="网站：").grid(row=0, column=0, sticky="w", pady=5)
        self.website_entry = ttk.Entry(frame, width=33)
        self.website_entry.grid(row=0, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="用户名：").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=33)
        self.username_entry.grid(row=1, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="密码：").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=33, show="●")
        self.password_entry.grid(row=2, column=1, pady=5, sticky="w")

        self.show_pw_btn = ttk.Button(frame, text="👁", width=4, command=self.toggle_password_entry)
        self.show_pw_btn.grid(row=2, column=2, padx=5, sticky="e")

        ttk.Button(frame, text="生成强密码", command=self.generate_password).grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="保存密码", command=self.save_password).grid(row=3, column=1, pady=10)
        ttk.Button(frame, text="查找密码", command=self.search_password).grid(row=3, column=2, pady=10)

        ttk.Button(frame, text="删除密码", command=self.delete_password).grid(row=4, column=0, pady=5)
        ttk.Button(frame, text="显示所有记录", command=self.show_all_passwords).grid(row=4, column=1, pady=5)
        ttk.Button(frame, text="导出密码", command=self.export_passwords).grid(row=4, column=2, pady=5)

        ttk.Button(frame, text="检测密码泄露", command=self.check_leak).grid(row=5, column=0, pady=5)

        ttk.Button(frame, text="密码强度分析", command=self.show_password_strength).grid(row=5, column=1, pady=5)
        ttk.Button(frame, text="密码长度分布", command=self.plot_password_length_distribution).grid(row=5, column=2, pady=5)


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
        window.geometry("600x400")
        window.resizable(True, True)

        tree = ttk.Treeview(window, columns=("Website", "Username", "Password"), show="headings")
        tree.heading("Website", text="网站")
        tree.heading("Username", text="用户名")
        tree.heading("Password", text="密码")

        tree.column("Website", width=150, anchor="w")
        tree.column("Username", width=150, anchor="w")
        tree.column("Password", width=150, anchor="w")

        vsb = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        tree.pack(fill="both", expand=True)

        for i, (website, data) in enumerate(self.manager.passwords.items()):
            password_display = '●' * len(data['password'])
            tree.insert("", "end", iid=website, values=(website, data['username'], password_display))

        show_all_button = ttk.Button(window, text="显示/隐藏所有密码", command=lambda: self.toggle_all_passwords_in_treeview(tree))
        show_all_button.pack(pady=5)
        self.show_all_passwords_state = False

    def toggle_all_passwords_in_treeview(self, tree):
        self.show_all_passwords_state = not self.show_all_passwords_state
        for item_id in tree.get_children():
            website = tree.item(item_id, 'values')[0]
            data = self.manager.passwords.get(website)
            if data:
                current_username = tree.item(item_id, 'values')[1]
                if self.show_all_passwords_state:
                    tree.item(item_id, values=(website, current_username, data['password']))
                else:
                    tree.item(item_id, values=(website, current_username, '●' * len(data['password'])))

    def export_passwords(self):
        self.manager.export_passwords()
        messagebox.showinfo("导出成功", "密码已导出到 passwords.csv 文件。")

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

    def show_password_strength(self):
        min_len, max_len, avg_len, median_len, std_dev = self.manager.analyze_password_strength()

        if min_len is None:
            messagebox.showinfo("提示", "目前没有保存的密码数据可供分析。")
            return

        report = f"""
        **密码强度分析报告**

        - 最短密码长度: **{min_len}**
        - 最长密码长度: **{max_len}**
        - 平均密码长度: **{avg_len:.2f}**
        - 密码长度中位数: **{median_len}**
        - 密码长度标准差: **{std_dev:.2f}**

        标准差越小，表示密码长度越集中；标准差越大，表示密码长度差异越大。
        """
        messagebox.showinfo("密码强度分析", report)


    def plot_password_length_distribution(self):
        df = self.manager.get_passwords_dataframe()

        if df.empty:
            messagebox.showinfo("提示", "没有密码数据可用于绘制图表。")
            return

        plot_window = tk.Toplevel(self.root)
        plot_window.title("密码长度分布图")
        plot_window.geometry("700x500")

        fig, ax = plt.subplots(figsize=(8, 5))

        df['PasswordLength'].plot(kind='hist', ax=ax, bins=range(5, 26, 2),
                                  edgecolor='black', alpha=0.7)

        ax.set_title('Password Length Distribution')
        ax.set_xlabel('Password Length')
        ax.set_ylabel('Frequency')
        ax.set_xticks(range(5, 26, 2))

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()