import os
import json
import requests
import argparse
from datetime import datetime
from html import escape

class ConfigManager:
    """配置管理器，用于处理配置文件的读写"""
    
    def __init__(self, config_file='.hoj_config.json'):
        """初始化配置管理器"""
        self.config_file = os.path.expanduser(config_file)
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return {}
            
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            
    def get_token(self):
        """获取存储的 Token"""
        return self.config.get('token')
        
    def save_token(self, token):
        """保存 Token 到配置文件"""
        self.config['token'] = token
        self.save_config()
        
    def clear_token(self):
        """清除存储的 Token"""
        if 'token' in self.config:
            del self.config['token']
            self.save_config()

class HOJAssistantCLI:
    def __init__(self):
        self.version = "1.0.1" 
        self.last_update = "20250718"
        self.author = "longStone"
        self.is_admin = False
        self.session = requests.Session()
        self.debug_mode = False
        self.auth_token = None
        self.oj_base_url = "https://deeplearning.org.cn"
        self.username = None
        self.config_manager = ConfigManager()
        
        # 尝试从配置文件加载 Token
        saved_token = self.config_manager.get_token()
        if saved_token:
            self.auth_token = saved_token
            print("已从配置文件加载 Token")

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

    def login(self, username=None, password=None, token=None, oj_url="https://deeplearning.org.cn"):
        """处理登录请求"""
        oj_url = oj_url.rstrip('/')
        self.oj_base_url = oj_url

        if token:
            self.username = "Token 用户"
            self.auth_token = token
            self.config_manager.save_token(token)  # 保存 Token 到配置文件
            print("Token 登录成功")
            return

        if not username or not password:
            print("错误: 请填写完整的登录信息")
            return

        login_url = f"{oj_url}/api/login"
        payload = {
            "username": username,
            "password": password
        }

        headers = self.get_common_headers(oj_url)
        headers["Content-Type"] = "application/json"

        try:
            response = self.session.post(login_url, json=payload, headers=headers)
            response.raise_for_status()  # 检查HTTP错误

            data = response.json()

            if 'Authorization' in response.headers:
                self.auth_token = response.headers['Authorization']
                self.config_manager.save_token(self.auth_token)  # 保存 Token 到配置文件
            else:
                self.auth_token = None

            if response.status_code == 200 and data.get("status") == 200:
                if data['data']['roleList'][0] in ['root', 'problem_admin', 'admin']:
                    print(f"成功: 欢迎回来，尊敬的管理员 {username}")
                    self.is_admin = True
                self.username = username
                print("登录成功")
            else:
                error_msg = data.get("msg", "登录失败，未知错误")
                print(f"登录失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def logout(self):
        """登出并清除 Token"""
        self.auth_token = None
        self.username = None
        self.config_manager.clear_token()
        print("已登出，Token 已清除")

    def crawl_code(self, submit_id):
        """处理代码爬取请求"""
        if not submit_id.isdigit():
            print("错误: 提交ID必须是数字")
            return

        crawl_url = f"{self.oj_base_url}/api/resubmit?submitId={submit_id}"
        headers = self.get_common_headers(f"{self.oj_base_url}/status")

        try:
            response = self.session.get(crawl_url, headers=headers)
            response.raise_for_status()  # 检查HTTP错误

            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                self.display_code(data.get("data", {}))
                print(f"成功获取提交ID为 {submit_id} 的代码")
            else:
                error_msg = data.get("msg", "爬取失败，未知错误")
                print(f"爬取失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def display_code(self, code_data):
        """显示代码信息和内容"""
        if not code_data:
            print("未获取到代码数据")
            return

        print("评测记录")
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

        for label, value in info_items:
            print(f"{label} {value}")

        print("警告：本工具仅用于学习研究用途，请于下载后 24 小时删除")

        code = code_data.get('code', '')
        if code:
            code = code.replace(r'\u003C', '<')
            code = code.replace(r'\u003E', '>')
            code = code.replace(r'\\n', '\n')
            code = code.replace(r'\\t', '\t')
            print(code)
        else:
            print("代码内容: 无")

    def format_time(self, time_str):
        """格式化时间字符串"""
        if not time_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return time_str

    def submit_code(self, file_path):
        """提交代码到API"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
        except FileNotFoundError:
            print("错误: 文件未找到")
            return

        pid = input("请输入题目ID: ")
        language = input("请输入代码语言: ")
        is_remote = input("是否远程测评 (y/n): ").lower() == 'y'

        if not pid or not language or not code:
            print("错误: 请输入完整的信息")
            return

        html_escaped_code = escape(code)

        payload = {
            "pid": pid,
            "language": language,
            "code": html_escaped_code,
            "cid": 0,
            "tid": None,
            "gid": None,
            "isRemote": is_remote
        }

        submit_url = f"{self.oj_base_url}/api/submit-problem-judge"
        headers = self.get_common_headers(submit_url)
        headers["Content-Type"] = "application/json"

        try:
            response = self.session.post(submit_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            if response.status_code == 200 and result.get("status") == 200:
                print("代码提交成功")
            else:
                error_msg = result.get("msg", "提交失败，未知错误")
                print(f"提交失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def get_discussion_info(self, discussion_id):
        """获取讨论信息"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        if not discussion_id.isdigit():
            print("错误: 讨论ID必须是数字")
            return

        get_url = f"{self.oj_base_url}/api/get-discussion-detail?did={discussion_id}"
        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")
        try:
            response = self.session.get(get_url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                self.display_discussion_info(data.get("data", {}))
                print(f"成功获取讨论ID为 {discussion_id} 的信息")
            else:
                error_msg = data.get("msg", "获取失败，未知错误")
                print(f"获取失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def display_discussion_info(self, discussion_data):
        """显示讨论信息"""
        if not discussion_data:
            print("未获取到讨论数据")
            return

        print(f"讨论标题: {discussion_data.get('title', 'N/A')}")
        print(f"讨论内容: {discussion_data.get('content', 'N/A')}")
        print(f"作者: {discussion_data.get('author', 'N/A')}")
    def to_discussion_like(self, is_like, discussion_id):
        """点赞或取消点赞讨论"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        if not discussion_id.isdigit():
            print("错误: 讨论ID必须是数字")
            return

        action = "true" if is_like else "false"
        like_url = f"{self.oj_base_url}/api/discussion-like?did={discussion_id}&toLike={action}"
        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")

        try:
            response = self.session.get(like_url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                print(f"成功 {'点赞' if is_like else '取消点赞'} 讨论ID为 {discussion_id} 的讨论")
            else:
                error_msg = data.get("msg", f"{action} 失败，未知错误")
                print(f"{action} 失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def report_discussion(self, discussion_id, report_reason):
        """举报讨论"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        if not discussion_id.isdigit():
            print("错误: 讨论ID必须是数字")
            return

        report_url = f"{self.oj_base_url}/api/discussion-report"
        headers = self.get_common_headers(f"{self.oj_base_url}/discussion")
        payload = {
            "discussionId": discussion_id,
            "reportReason": report_reason
        }
        headers["Content-Type"] = "application/json"

        try:
            response = self.session.post(report_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                print(f"成功举报讨论ID为 {discussion_id} 的讨论")
            else:
                error_msg = data.get("msg", "举报失败，未知错误")
                print(f"举报失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def send_session(self, cf_session):
        """发送CFSession更新请求"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        update_url = f"{self.oj_base_url}/api/update-cfSession"
        headers = self.get_common_headers(f"{self.oj_base_url}/status")
        data = {"cfSession": cf_session}

        try:
            response = self.session.post(update_url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()

            if response.status_code == 200 and result.get("status") == 200:
                print("CFSession更新成功")
            else:
                error_msg = result.get("msg", "更新失败，未知错误")
                print(f"更新失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def remove_session(self):
        """删除CFSession"""
        if not self.oj_base_url or not self.auth_token:
            print("错误: 请先登录")
            return

        update_url = f"{self.oj_base_url}/api/delete-cfSession"
        headers = self.get_common_headers(f"{self.oj_base_url}/status")

        try:
            response = self.session.delete(update_url, headers=headers)
            response.raise_for_status()

            result = response.json()

            if response.status_code == 200 and result.get("status") == 200:
                print("CFSession删除成功")
            else:
                error_msg = result.get("msg", "删除失败，未知错误")
                print(f"删除失败: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"网络错误: 无法连接到服务器: {str(e)}")
        except json.JSONDecodeError:
            print("错误: 服务器返回非JSON格式数据")
        except Exception as e:
            print(f"未知错误: {str(e)}")
def main():
    parser = argparse.ArgumentParser(description="HOJ Tool CLI")
    subparsers = parser.add_subparsers(dest='command')

    # 登录命令
    login_parser = subparsers.add_parser('login', help='登录到 OJ')
    logout_parser = subparsers.add_parser('logout', help='登出 OJ')
    login_group = login_parser.add_mutually_exclusive_group(required=True)
    login_group.add_argument('-u', '--username', help='用户名')
    login_group.add_argument('-t', '--token', help='用户的Token')
    login_parser.add_argument('-p', '--password', help='密码')
    login_parser.add_argument('-url','--oj-url', default="https://deeplearning.org.cn", help='OJ地址')

    # 代码爬取命令
    submitcraw_parser = subparsers.add_parser('submitcraw', help='爬取代码')
    submitcraw_parser.add_argument('-i', '--submit-id', required=True, help='代码ID')

    # 代码提交命令
    submit_parser = subparsers.add_parser('submit', help='提交代码')
    submit_parser.add_argument('-f', '--file', required=True, help='代码文件路径')

    # 讨论爬取命令
    discusscraw_parser = subparsers.add_parser('discusscraw', help='爬取讨论信息')
    discusscraw_parser.add_argument('-i', '--discussion-id', required=True, help='讨论ID')

    # 点赞命令
    like_parser = subparsers.add_parser('like', help='点赞讨论')
    like_parser.add_argument('-i', '--discussion-id', required=True, help='讨论ID')

    # 取消点赞命令
    dislike_parser = subparsers.add_parser('dislike', help='取消点赞讨论')
    dislike_parser.add_argument('-i', '--discussion-id', required=True, help='讨论ID')

    # 举报命令
    report_parser = subparsers.add_parser('report', help='举报讨论')
    report_parser.add_argument('-i', '--discussion-id', required=True, help='讨论ID')
    report_parser.add_argument('-t', '--report-reason', required=True, help='举报原因')

    # 更新 Session 命令
    updsession_parser = subparsers.add_parser('updsession', help='更新 CFSession')
    updsession_parser.add_argument('-t', '--session', required=True, help='新的session')

    # 删除 Session 命令
    remsession_parser = subparsers.add_parser('remsession', help='删除 CFSession')

    args = parser.parse_args()

    cli = HOJAssistantCLI()
    if args.command == 'login':
        if args.username:
            cli.login(username=args.username, password=args.password, oj_url=args.oj_url)
        else:
            cli.login(token=args.token, oj_url=args.oj_url)
    elif args.command == 'logout':
        cli.logout()
    elif args.command == 'submitcraw':
        cli.crawl_code(args.submit_id)
    elif args.command == 'submit':
        cli.submit_code(args.file)
    elif args.command == 'discusscraw':
        cli.get_discussion_info(args.discussion_id)
    elif args.command == 'like':
        cli.to_discussion_like(True, args.discussion_id)
    elif args.command == 'dislike':
        cli.to_discussion_like(False, args.discussion_id)
    elif args.command == 'report':
        cli.report_discussion(args.discussion_id, args.report_reason)
    elif args.command == 'updsession':
        cli.send_session(args.session)
    elif args.command == 'remsession':
        cli.remove_session()

if __name__ == "__main__":
    main()