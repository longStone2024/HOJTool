import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import re
from datetime import datetime
from html import escape
from ttkbootstrap import Style
import pyperclip
import pywinstyles
from windows_toasts import WindowsToaster, Toast


class HOJAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("HOJ Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.win_toasts = WindowsToaster('HOJ Tool')
        self.version = "1.0.2" 
        self.last_update = "20250719"
        self.author = "longStone"

        self.is_admin = False
        
        pywinstyles.apply_style(self.root, "dark")
        self.style = Style(theme="darkly")
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 创建会话对象，用于保持登录状态
        self.session = requests.Session()
        
        # 调试模式
        self.debug_mode = False
        self.auth_token = None
        # 初始化界面
        self.create_login_frame()

    def create_login_frame(self):
        """创建登录界面"""
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(self.login_frame, text="HOJ Tool", font=("SimHei", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # OJ地址
        ttk.Label(self.login_frame, text="OJ地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.oj_url_var = tk.StringVar(value="https://deeplearning.org.cn")
        ttk.Entry(self.login_frame, textvariable=self.oj_url_var, width=40).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # 用户名
        ttk.Label(self.login_frame, text="用户名:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.username_var, width=40).grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # 密码
        ttk.Label(self.login_frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.password_var, show="*", width=40).grid(row=3, column=1, pady=5, sticky=tk.W)
        # 调试模式按钮
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(self.login_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug_mode)
        debug_check.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 登录按钮
        login_btn = ttk.Button(self.login_frame, text="登录", style="Win11.TButton", command=self.login)
        login_btn.grid(row=4, column=1, pady=20, sticky=tk.W)
        
        ttk.Label(self.login_frame, text="Token:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.token_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.token_var, width=80).grid(row=5, column=1, pady=5, sticky=tk.W)
        
        login_btn = ttk.Button(self.login_frame, text="Token 登录", command=self.token_login)
        login_btn.grid(row=5, column=2, pady=10, sticky=tk.W)

        # 状态标签
        self.status_var = tk.StringVar(value="请输入登录信息")
        ttk.Label(self.login_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.login_frame, text="警告：本工具仅用于学习研究用途，请于下载后 24 小时删除", font=("SimHei", 10, "bold"), foreground="orange").grid(
            row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2
        )
        
        # 调试信息文本框 - 初始隐藏
        self.debug_text = scrolledtext.ScrolledText(self.login_frame, width=70, height=10, wrap=tk.WORD)
        self.debug_text.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        self.debug_text.config(state=tk.DISABLED)
        self.debug_text.grid_remove()  # 初始隐藏
        
        # 设置列和行的权重
        self.login_frame.columnconfigure(1, weight=1)
        self.login_frame.rowconfigure(6, weight=1)  # 为调试框保留空间
    
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = self.debug_var.get()
        
        if self.debug_mode:
            self.debug_text.grid()  # 显示调试框
            self.log_debug("调试模式已启用")
        else:
            self.debug_text.grid_remove()  # 隐藏调试框
            self.clear_debug_log()
        
    
    def log_debug(self, message):
        """记录调试信息"""
        if not self.debug_mode:
            return
            
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.insert(tk.END, f"{message}\n")
        self.debug_text.see(tk.END)
        self.debug_text.config(state=tk.DISABLED)
    
    def clear_debug_log(self):
        """清除调试日志"""
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.config(state=tk.DISABLED)
    
    def get_common_headers(self, referer):
        """获取通用请求头"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Referer": referer,
            "URL-Type": "general"
        }
        if self.auth_token:
            headers['Authorization'] = self.auth_token
        return headers

    def login(self):
        """处理登录请求"""
        self.clear_debug_log()
        
        oj_url = self.oj_url_var.get().rstrip('/')  # 移除尾部斜杠
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not oj_url or not username or not password:
            messagebox.showerror("错误", "请填写完整的登录信息")
            return
        
        self.status_var.set("正在登录...")
        self.root.update()
        
        login_url = f"{oj_url}/api/login"
        payload = {
            "username": username,
            "password": password
        }
        
        headers = self.get_common_headers(oj_url)
        headers["Content-Type"] = "application/json"
        
        self.log_debug(f"登录URL: {login_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"请求体: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(login_url, json=payload, headers=headers)
            response.raise_for_status()  # 检查HTTP错误
            
            # 记录详细的响应信息
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            self.log_debug(f"Cookie: {json.dumps(self.session.cookies.get_dict(), indent=2)}")
            
            try:
                data = response.json()
                self.log_debug(f"响应JSON: {json.dumps(data, indent=2)}")
                
                # 检查响应头中是否有Authorization字段
                if 'Authorization' in response.headers:
                    self.auth_token = response.headers['Authorization']
                    self.log_debug(f"获取到Authorization令牌: {self.auth_token[:30]}...")
                else:
                    self.auth_token = None
                    self.log_debug("未找到Authorization令牌")
                #  + data['data']['username']
                if response.status_code == 200 and data.get("status") == 200:
                    if data['data']['roleList'][0] == 'root' or data['data']['roleList'][0] == 'problem_admin' or data['data']['roleList'][0] == 'admin':
                        newToast = Toast()
                        newToast.text_fields = ["登录成功" , "欢迎回来，尊敬的管理员 " + username]
                        self.win_toasts.show_toast(newToast)
                        is_admin = True
                    else:
                        newToast = Toast()
                        newToast.text_fields = ["登录成功","欢迎回来，" + username]
                        self.win_toasts.show_toast(newToast)
                    self.oj_base_url = oj_url  # 保存OJ基础URL
                    self.login_frame.destroy()
                    self.create_crawler_frame()
                else:
                    error_msg = data.get("msg", "登录失败，未知错误")
                    messagebox.showerror("登录失败", error_msg)
                    self.status_var.set("登录失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise
        
        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")
            
            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查OJ地址")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")
    def token_login(self):
        """处理登录请求"""
        self.clear_debug_log()
        token = self.token_var.get()
        oj_url = self.oj_url_var.get().rstrip('/')
        if not oj_url or not token:
            messagebox.showerror("错误", "请填写完整的登录信息")
            return
        self.status_var.set("正在登录...")
        self.root.update()
        # 不检查登录可行性，将用户名设为 token
        self.username_var.set("Token 用户") 
        self.oj_base_url = oj_url  # 保存OJ基础URL
        self.auth_token = token
        self.login_frame.destroy()
        self.create_crawler_frame()

    def create_crawler_frame(self):
        """创建爬取界面"""
        self.crawler_frame = ttk.Frame(self.root, padding="20")
        self.crawler_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(self.crawler_frame, text="HOJ Tool", font=("SimHei", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # 当前登录信息
        login_info = f"已登录到: {self.oj_base_url}  |  用户: {self.username_var.get()}"
        self.login_info_label = ttk.Label(self.crawler_frame, text=login_info, font=("SimHei", 10))
        self.login_info_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.crawler_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)
        
        self.code_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.code_tab, text="代码爬取")
        
        self.submit_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.submit_tab, text="代码提交")

        self.discussion_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.discussion_tab, text="讨论信息")
        
        self.other_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.other_tab, text="其他")

        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text="关于")
        
        # 设置选项卡控件的权重
        self.crawler_frame.rowconfigure(2, weight=1)
        self.crawler_frame.columnconfigure(0, weight=1)
        
        # Setup all tabs
        self.setup_code_tab()
        self.setup_submit_tab()
        self.setup_discussion_tab()
        self.setup_other_tab()
        self.setup_about_tab()
        
        # 调试信息区域 - 初始隐藏
        self.debug_text = scrolledtext.ScrolledText(self.crawler_frame, width=70, height=10, wrap=tk.WORD)
        self.debug_text.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        self.debug_text.config(state=tk.DISABLED)
        self.debug_text.grid_remove()  # 初始隐藏
        
        # 状态栏
        self.status_var = tk.StringVar(value="HOJ Tool " + self.version)
        ttk.Label(self.crawler_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        if self.debug_mode:
            self.debug_text.grid()  # 显示调试框
            self.log_debug("调试模式已启用")
        else:
            self.debug_text.grid_remove()  # 隐藏调试框
            self.clear_debug_log()
    
    def setup_code_tab(self):
        """设置代码爬取选项卡"""
        # 控制区域
        control_frame = ttk.Frame(self.code_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        # 调试模式按钮
        debug_check = ttk.Checkbutton(control_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug_mode)
        debug_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # SubmitID输入
        ttk.Label(control_frame, text="提交ID:").grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.submit_id_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.submit_id_var, width=40).grid(row=0, column=2, pady=5, sticky=tk.W)
        # 爬取按钮
        crawl_btn = ttk.Button(control_frame, text="爬取代码", command=lambda: self.crawl_code("default"))
        crawl_btn.grid(row=0, column=3, pady=5, padx=10)
        # 范围
        ttk.Label(control_frame, text="范围:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.start_id = tk.StringVar()
        self.end_id = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.start_id, width=30).grid(row=1, column=1)
        ttk.Entry(control_frame, textvariable=self.end_id, width=30).grid(row=1, column=2)
        resubmit_btn = ttk.Button(control_frame, text="批量重测", command=self.resubmit_some_code)
        resubmit_btn.grid(row=1, column=3, pady=5, padx=10)
        # 代码信息区域
        self.code_info_frame = ttk.Frame(self.code_tab)
        self.code_info_frame.pack(fill=tk.X, padx=5, pady=5)
        # 代码内容区域
        code_frame = ttk.Frame(self.code_tab)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 代码标题
        code_header_frame = ttk.Frame(code_frame)
        code_header_frame.pack(fill=tk.X)
        
        ttk.Label(code_header_frame, text="代码内容:", font=("SimHei", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 复制按钮
        copy_btn = ttk.Button(code_header_frame, text="复制代码", command=self.copy_code)
        copy_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 代码文本框
        self.code_text = scrolledtext.ScrolledText(code_frame, width=70, height=15, wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_submit_tab(self):
        """设置代码提交选项卡"""
        # 控制区域
        control_frame = ttk.Frame(self.submit_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 调试模式按钮
        debug_check = ttk.Checkbutton(control_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug_mode)
        debug_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # ProblemID输入
        ttk.Label(control_frame, text="问题ID:").grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.problem_id_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.problem_id_var, width=40).grid(row=0, column=2, pady=5, sticky=tk.W)

        # 代码语言选择(输入框)
        ttk.Label(control_frame, text="代码语言:").grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        self.language_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.language_var, width=10).grid(row=1, column=2, pady=5, sticky=tk.W)
        # 是否远程测评
        self.is_remote_var = tk.BooleanVar(value=False)
        remote_check = ttk.Checkbutton(control_frame, text="远程测评", variable=self.is_remote_var)
        remote_check.grid(row=1, column=5, sticky=tk.W, pady=5)

        # 按钮
        crawl_btn = ttk.Button(control_frame, text="提交", command=self.submit_code)  # 修改为提交代码函数
        crawl_btn.grid(row=0, column=3, pady=5, padx=10)
        
        # 代码信息区域
        self.submit_info_frame = ttk.Frame(self.submit_tab)
        self.submit_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 代码内容区域
        submit_frame = ttk.Frame(self.submit_tab)
        submit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 代码标题
        submit_header_frame = ttk.Frame(submit_frame)
        submit_header_frame.pack(fill=tk.X)
        
        ttk.Label(submit_header_frame, text="代码内容:", font=("SimHei", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        # 代码文本框
        self.submit_text = scrolledtext.ScrolledText(submit_frame, width=70, height=15, wrap=tk.WORD)
        self.submit_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    def setup_discussion_tab(self):
        """设置讨论信息选项卡"""
        # 控制区域
        control_frame = ttk.Frame(self.discussion_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 调试模式按钮
        debug_check = ttk.Checkbutton(control_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug_mode)
        debug_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 讨论ID输入
        ttk.Label(control_frame, text="讨论ID:").grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.discussion_id_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.discussion_id_var, width=30).grid(row=0, column=2, pady=5, sticky=tk.W)
        
        # 获取按钮
        get_discussion_btn = ttk.Button(control_frame, text="获取讨论信息", command=self.get_discussion_info)
        get_discussion_btn.grid(row=0, column=3, pady=5, padx=10)
        
        # 点赞按钮 - 使用lambda表达式正确绑定参数
        add_like_btn = ttk.Button(control_frame, text="点赞", command=lambda: self.to_discussion_like(True))
        add_like_btn.grid(row=0, column=4, pady=4, padx=5)

        remove_like_btn = ttk.Button(control_frame, text="取消点赞", command=lambda: self.to_discussion_like(False))
        remove_like_btn.grid(row=0, column=5, pady=4, padx=5)

        # 举报者名字输入
        ttk.Label(control_frame, text="举报者名字:").grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        self.reporter_name_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.reporter_name_var, width=30).grid(row=1, column=2, pady=5, sticky=tk.W)

        # 举报标签输入
        ttk.Label(control_frame, text="举报标签:格式:\n#标签# 内容").grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        self.report_tags_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.report_tags_var, width=30).grid(row=2, column=2, pady=5, sticky=tk.W)
    
        # 举报按钮
        report_btn = ttk.Button(control_frame, text="举报讨论", command=self.report_discussion)
        report_btn.grid(row=2, column=3, pady=5, padx=10)
        
        # 讨论详情框架
        detail_frame = ttk.LabelFrame(self.discussion_tab, text="讨论详情")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 讨论标题
        self.discussion_title_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.discussion_title_var, font=("SimHei", 12, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        # 讨论信息
        self.discussion_info_frame = ttk.Frame(detail_frame)
        self.discussion_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 讨论内容
        self.discussion_content_text = scrolledtext.ScrolledText(detail_frame, width=70, height=10, wrap=tk.WORD)
        self.discussion_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.discussion_content_text.config(state=tk.DISABLED)
    def setup_other_tab(self):
        """设置其他选项卡"""
        # 控制区域
        control_frame = ttk.Frame(self.other_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 调试模式按钮
        debug_check = ttk.Checkbutton(control_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug_mode)
        debug_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # CFSession 输入
        ttk.Label(control_frame, text="刷新 CFSession:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.seassion = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.seassion, width=40).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # 提交Session按钮
        session_btn = ttk.Button(control_frame, text="提交", command=self.send_session)
        session_btn.grid(row=1, column=5, pady=5, padx=10)
        
        rem_session_btn = ttk.Button(control_frame, text="删除", command=self.remove_session)
        rem_session_btn.grid(row=1, column=6, pady=5, padx=10)
    def setup_about_tab(self):
        """设置关于选项卡"""
        # 关于信息
        control_frame = ttk.Frame(self.about_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        about_text = f"HOJ Tool {self.version}\n" \
                     f"作者: {self.author}\n" \
                     f"最后更新: {self.last_update}\n"
        # 居中显示 About
        about_label = ttk.Label(control_frame, text=about_text, justify=tk.CENTER, font=("SimHei", 10))
        about_label.pack(anchor=tk.CENTER, padx=5, pady=5)
        # 版权信息
        copyright_text = "© 2025 longStone. All rights reserved."
        copyright_label = ttk.Label(control_frame, text=copyright_text, justify=tk.CENTER, font=("SimHei", 10))
        copyright_label.pack(anchor=tk.CENTER, padx=5, pady=5)
    def remove_session(self):
        """删除CFSession"""
        self.status_var.set("正在删除CFSession...")
        self.root.update()
        # 采用 DELETE 方法
        update_url = f"{self.oj_base_url}/api/delete-cfSession"
        headers = self.get_common_headers(f"{self.oj_base_url}/status")
        
        try:
            response = self.session.delete(update_url, headers=headers)
            response.raise_for_status()
            
            self.log_debug(f"更新URL: {update_url}")
            self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            try:
                result = response.json()
                self.log_debug(f"响应JSON: {json.dumps(result, indent=2)}")
                
                if response.status_code == 200 and result.get("status") == 200:
                    self.status_var.set("CFSession删除成功")
                else:
                    error_msg = result.get("msg", "更新失败，未知错误")
                    self.status_var.set("更新失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise
            
        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            self.status_var.set("服务器返回非JSON格式数据")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")   
    def send_session(self):
        """发送CFSession更新请求"""
        cf_session = self.seassion.get().strip()
        
        self.status_var.set("正在更新CFSession...")
        self.root.update()
        
        update_url = f"{self.oj_base_url}/api/update-cfSession"
        headers = self.get_common_headers(f"{self.oj_base_url}/status")
        data = {"cfSession": cf_session}
        
        try:
            response = self.session.post(update_url, json=data, headers=headers)
            response.raise_for_status()
            
            self.log_debug(f"更新URL: {update_url}")
            self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
            self.log_debug(f"请求数据: {json.dumps(data, indent=2)}")
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            try:
                result = response.json()
                self.log_debug(f"响应JSON: {json.dumps(result, indent=2)}")
                
                if response.status_code == 200 and result.get("status") == 200:
                    self.status_var.set("CFSession更新成功")
                else:
                    error_msg = result.get("msg", "更新失败，未知错误")
                    self.status_var.set("更新失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise
            
        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")
            
            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            self.status_var.set("服务器返回非JSON格式数据")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")      
    def resubmit_some_code(self):
        """批量重测代码"""
        self.clear_debug_log()
        start_id = self.start_id.get().strip()
        end_id = self.end_id.get().strip()
        if not start_id or not end_id:
            messagebox.showerror("错误", "请输入完整的范围")
            return
        if not start_id.isdigit() or not end_id.isdigit():
            messagebox.showerror("错误", "范围必须是数字")
            return
        start_id = int(start_id)
        end_id = int(end_id)
        if start_id > end_id:
            messagebox.showerror("错误", "起始ID不能大于结束ID")
            return
        self.status_var.set("正在批量重测代码...")
        self.root.update()
        for i in range(start_id, end_id + 1):
            self.submit_id_var.set(str(i))
            self.crawl_code("noerr")
            self.root.update()
            self.status_var.set("正在重测代码，编号：" + str(i))
        newToast = Toast()
        newToast.text_fields = ["批量重测已经完成", "范围从" + str(start_id) + "到" + str(end_id) + "的代码"]  
        self.win_toasts.show_toast(newToast)
    def crawl_code(self, status):
        """处理代码爬取请求"""
        self.clear_debug_log()
        
        submit_id = self.submit_id_var.get().strip()
        
        if not submit_id:
            messagebox.showerror("错误", "请输入提交ID")
            return
        
        if not submit_id.isdigit():
            messagebox.showerror("错误", "提交ID必须是数字")
            return
        
        self.status_var.set("正在爬取代码...")
        self.root.update()
        
        crawl_url = f"{self.oj_base_url}/api/resubmit?submitId={submit_id}"
        
        headers = self.get_common_headers(f"{self.oj_base_url}/status")
        
        self.log_debug(f"爬取URL: {crawl_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"当前Cookie: {json.dumps(self.session.cookies.get_dict(), indent=2)}")
        
        try:
            response = self.session.get(crawl_url, headers=headers)
            response.raise_for_status()  # 检查HTTP错误
            
            # 记录详细的响应信息
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            try:
                data = response.json()
                self.log_debug(f"响应JSON: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200 and data.get("status") == 200:
                    self.status_var.set(f"成功获取提交ID为 {submit_id} 的代码")
                    if status == "default":
                        self.display_code(data.get("data", {}))
                else:
                    error_msg = data.get("msg", "爬取失败，未知错误")
                    self.status_var.set("爬取失败，请重试" + error_msg)
                    if status == "default":
                        messagebox.showerror("错误", error_msg)
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise
        
        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")
            if status == "default":
                messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            if status == "default":
                messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            if status == "default":
                messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.log_debug(f"未知错误: {str(e)}")
            self.status_var.set("发生未知错误")
    
    def display_code(self, code_data):
        """显示代码信息和内容"""
        # 清空之前的信息
        for widget in self.code_info_frame.winfo_children():
            widget.destroy()
        
        self.code_text.delete(1.0, tk.END)
        
        if not code_data:
            self.code_text.insert(tk.END, "未获取到代码数据")
            return
        
        ttk.Label(self.code_info_frame, text="评测记录", font=("SimHei", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5
        )
            
        info_items = [
            ("题目ID:", code_data.get('displayPid', 'N/A')),
            ("内部题目ID:", code_data.get('pid', 'N/A')),
            ("用户名:", code_data.get('username', 'N/A')),
            ("RMJ用户名:", code_data.get('vjudgeUsername', 'N/A')),
            ("RMJ远程测评ID:", code_data.get('vjudgeSubmitId', 'N/A')),
            ("提交时间:", self.format_time(code_data.get('submitTime'))),
            ("语言:", code_data.get('language', 'N/A')),
            ("代码长度:", f"{code_data.get('length', 'N/A')} 字节")
        ]
            
        # 从第1行开始显示信息
        start_row = 1

        for i, (label, value) in enumerate(info_items):
            ttk.Label(self.code_info_frame, text=f"{label} {value}", font=("SimHei", 10)).grid(
                row=start_row + i//2, column=i%2, sticky=tk.W, padx=5, pady=2
            )
        #黄字显示不要抄袭警告
        ttk.Label(self.code_info_frame, text="警告：本工具仅用于学习研究用途，请于下载后 24 小时删除", font=("SimHei", 10, "bold"), foreground="orange").grid(
            row=start_row + len(info_items)//2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2
        )

        # 处理代码内容
        code = code_data.get('code', '')
        if code:
            # 解码HTML实体
            code = re.sub(r'\\u003C', '<', code)
            code = re.sub(r'\\u003E', '>', code)
            code = re.sub(r'\\n', '\n', code)
            code = re.sub(r'\\t', '\t', code)
            self.code_text.insert(tk.END, code)
        else:
            self.code_text.insert(tk.END, "代码内容: 无")
        
        # 自动调整滚动条到顶部
        self.code_text.see(1.0)
    
    def format_time(self, time_str):
        """格式化时间字符串"""
        if not time_str:
            return "N/A"
        try:
            # 转换ISO格式时间
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return time_str
    
    def copy_code(self):
        """复制代码到剪贴板"""
        code = self.code_text.get(1.0, tk.END).strip()
        if code:
            pyperclip.copy(code)
            messagebox.showinfo("成功", "代码已复制到剪贴板")
        else:
            messagebox.showerror("错误", "没有可复制的代码")
    def submit_code(self):
        """提交代码到API"""
        self.clear_debug_log()
        
        # 获取UI输入值
        pid = self.problem_id_var.get().strip()
        language = self.language_var.get().strip()
        code = self.submit_text.get(1.0, tk.END).strip()
        is_remote = self.is_remote_var.get()
        
        # 验证输入
        if not pid:
            messagebox.showerror("错误", "请输入题目ID")
            return
        if not language:
            messagebox.showerror("错误", "请输入代码语言")
            return
        if not code:
            messagebox.showerror("错误", "代码内容不能为空")
            return
        
        self.status_var.set("正在提交代码...")
        self.root.update()
        
        # 将代码转换为HTML格式（转义特殊字符）
        html_escaped_code = escape(code)
        
        # 构建请求数据
        payload = {
            "pid": pid,
            "language": language,
            "code": html_escaped_code,
            "cid": 0,
            "tid": None,
            "gid": None,
            "isRemote": is_remote
        }
        
        # 提交API地址（请替换为实际API地址）
        submit_url = f"{self.oj_base_url}/api/submit-problem-judge"
        headers = self.get_common_headers(submit_url)

        headers["Content-Type"] = "application/json"
        
        self.log_debug(f"提交URL: {submit_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"提交数据: {json.dumps(payload, indent=2)}")
        
        try:
            # 发送POST请求
            response = self.session.post(
                submit_url,
                json=payload,  # 直接使用json参数而非data
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            self.log_debug(f"提交响应: {json.dumps(result, indent=2)}")
            
            if result.get("status") == 200:
                messagebox.showinfo("成功", f"代码提交成功！提交ID: {result.get('data', {}).get('submitId', '未知')}")
                self.status_var.set("代码提交成功")
            else:
                error_msg = result.get("msg", "提交失败，未知错误")
                messagebox.showerror("提交失败", error_msg)
                self.status_var.set("提交失败，请重试")
                
        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")
    def get_discussion_info(self):
        """处理获取讨论信息的请求"""
        self.clear_debug_log()

        discussion_id = self.discussion_id_var.get().strip()

        if not discussion_id:
            messagebox.showerror("错误", "请输入讨论ID")
            return

        if not discussion_id.isdigit():
            messagebox.showerror("错误", "讨论ID必须是数字")
            return

        self.status_var.set("正在获取讨论信息...")
        self.root.update()

        discussion_url = f"{self.oj_base_url}/api/get-discussion-detail?did={discussion_id}"

        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")

        self.log_debug(f"讨论信息URL: {discussion_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"当前Cookie: {json.dumps(self.session.cookies.get_dict(), indent=2)}")

        try:
            response = self.session.get(discussion_url, headers=headers)
            response.raise_for_status()  # 检查HTTP错误

            # 记录详细的响应信息
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")

            try:
                data = response.json()
                self.log_debug(f"响应JSON: {json.dumps(data, indent=2)}")

                if response.status_code == 200 and data.get("status") == 200:
                    self.display_discussion_detail(data.get("data", {}))
                    self.status_var.set(f"成功获取讨论ID为 {discussion_id} 的信息")
                else:
                    error_msg = data.get("msg", "获取讨论信息失败，未知错误")
                    messagebox.showerror("获取讨论信息失败", error_msg)
                    self.status_var.set("获取讨论信息失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise

        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")

            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")
    
    def to_discussion_like(self, to_like):
        """处理讨论点赞/取消点赞请求"""
        self.clear_debug_log()

        discussion_id = self.discussion_id_var.get().strip()

        if not discussion_id:
            messagebox.showerror("错误", "请输入讨论ID")
            return

        if not discussion_id.isdigit():
            messagebox.showerror("错误", "讨论ID必须是数字")
            return

        self.status_var.set("正在处理点赞请求...")
        self.root.update()

        discussion_url = f"{self.oj_base_url}/api/discussion-like?did={discussion_id}&toLike={str(to_like).lower()}"

        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")

        self.log_debug(f"点赞请求URL: {discussion_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"当前Cookie: {json.dumps(self.session.cookies.get_dict(), indent=2)}")

        try:
            response = self.session.get(discussion_url, headers=headers)
            response.raise_for_status()  # 检查HTTP错误

            # 记录详细的响应信息
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")

            try:
                data = response.json()
                self.log_debug(f"响应JSON: {json.dumps(data, indent=2)}")

                if response.status_code == 200 and data.get("status") == 200:
                    # 刷新讨论详情
                    action = "点赞" if to_like else "取消点赞"
                    self.status_var.set(f"成功{action}讨论ID为 {discussion_id}")
                else:
                    error_msg = data.get("msg", f"{action}失败，未知错误")
                    messagebox.showerror(f"{action}失败", error_msg)
                    self.status_var.set(f"{action}失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise

        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")

            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")

    def report_discussion(self):
        """处理讨论举报请求"""
        self.clear_debug_log()

        discussion_id = self.discussion_id_var.get().strip()
        reporter_name = self.reporter_name_var.get().strip()
        report_tags = self.report_tags_var.get().strip()

        if not discussion_id:
            messagebox.showerror("错误", "请输入讨论ID")
            return

        if not discussion_id.isdigit():
            messagebox.showerror("错误", "讨论ID必须是数字")
            return

        if not reporter_name:
            messagebox.showerror("错误", "请输入举报者名字")
            return

        if not report_tags:
            messagebox.showerror("错误", "请输入举报标签")
            return

        self.status_var.set("正在处理举报请求...")
        self.root.update()

        report_url = f"{self.oj_base_url}/api/discussion-report"
        payload = {
            "reporter": reporter_name,
            "content": report_tags,
            "did": int(discussion_id)
        }

        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")
        headers["Content-Type"] = "application/json"

        self.log_debug(f"举报请求URL: {report_url}")
        self.log_debug(f"请求头: {json.dumps(headers, indent=2)}")
        self.log_debug(f"请求体: {json.dumps(payload, indent=2)}")
        self.log_debug(f"当前Cookie: {json.dumps(self.session.cookies.get_dict(), indent=2)}")

        try:
            response = self.session.post(report_url, json=payload, headers=headers)
            response.raise_for_status()  # 检查HTTP错误

            # 记录详细的响应信息
            self.log_debug(f"响应状态码: {response.status_code}")
            self.log_debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")

            try:
                data = response.json()
                self.log_debug(f"响应JSON: {json.dumps(data, indent=2)}")

                if response.status_code == 200 and data.get("msg") == "success":
                    messagebox.showinfo("成功", "举报成功！")
                    self.status_var.set(f"成功举报讨论ID为 {discussion_id}")
                else:
                    error_msg = data.get("msg", "举报失败，未知错误")
                    messagebox.showerror("举报失败", error_msg)
                    self.status_var.set("举报失败，请重试")
            except json.JSONDecodeError:
                self.log_debug(f"响应文本: {response.text[:500]}...")
                raise

        except requests.exceptions.RequestException as e:
            self.log_debug(f"请求异常: {str(e)}")
            if hasattr(response, 'status_code'):
                self.log_debug(f"响应状态码: {response.status_code}")
            if hasattr(response, 'text'):
                self.log_debug(f"响应内容: {response.text[:500]}...")

            messagebox.showerror("网络错误", f"无法连接到服务器: {str(e)}")
            self.status_var.set("网络错误，请检查连接")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "服务器返回非JSON格式数据")
            self.status_var.set("服务器响应异常")
        except Exception as e:
            self.log_debug(f"未知错误: {str(e)}")
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
            self.status_var.set("发生未知错误")

    def display_discussion_detail(self, discussion_data):
        """显示讨论详情"""
        # 清空之前的信息
        for widget in self.discussion_info_frame.winfo_children():
            widget.destroy()
        
        self.discussion_content_text.config(state=tk.NORMAL)
        self.discussion_content_text.delete(1.0, tk.END)
        
        if not discussion_data:
            self.discussion_title_var.set("未获取到讨论信息")
            self.discussion_content_text.insert(tk.END, "未获取到讨论内容")
            self.discussion_content_text.config(state=tk.DISABLED)
            return
        
        # 设置讨论标题
        self.discussion_title_var.set(discussion_data.get('title', '无标题'))
        
        # 显示讨论基本信息
        info_items = [
            ("讨论ID:", discussion_data.get('id', 'N/A')),
            ("分类:", discussion_data.get('categoryName', 'N/A')),
            ("作者:", discussion_data.get('author', 'N/A')),
            ("题目:", discussion_data.get('title', 'N/A')),
            ("介绍:", discussion_data.get('description', 'N/A')),
            ("浏览次数:", discussion_data.get('viewNum', 'N/A')),
            ("点赞次数:", discussion_data.get('likeNum', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(info_items):
            ttk.Label(self.discussion_info_frame, text=f"{label} {value}", font=("SimHei", 10)).grid(
                row=i//3, column=i%3, sticky=tk.W, padx=5, pady=2
            )
        
        # 显示讨论内容
        content = discussion_data.get('content', '')
        if content:            
            self.discussion_content_text.insert(tk.END, content)
        
        self.discussion_content_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = HOJAssistant(root)
    root.mainloop()
