# HOJTool

[English](https://github.com/longStone2024/HOJTool/blob/main/README.en.md) | [HOJ](https://github.com/HimitZH/HOJ)

核里利用 HOJ 的 API 制作的小工具。

为什么制作它：问作者似乎得不到任何帮助。

## 已实现功能介绍
事实上，有一部分是 AI 辅助制作的，但是不可否认 AI 的贡献只能占一部分。
1. **代码爬取/重测**：允许对于给定的编号，爬取代码，同时泄露了远程评测账号密码（基于重测未鉴权实现）。
1. **自定义提交**：使用你的好朋友名字或者禁止的语言提交代码！（当然需要开远程评测，然后如果语言不支持会 `System Error`）
2. **讨论爬取**：直接爬取讨论 Markdown。
4. **自定义发布讨论** 事实上，你可以自定义你的点赞数，评论数，浏览数，头衔等……
5. **讨论点赞/去点赞**：允许无限次为讨论更改点赞！（点赞API未鉴权，但作者说他写了）
6. **讨论举报**：允许自定义标签和内容，还可以自己选择举报者总之不是你干的！
7. 快速刷新 CFSession：仅适用于部分 HOJ 分支。
8. **评测爬取**：可以配合代码爬取使用，非常方便。

## 快速使用
分为 CLI 和 GUI 两个版本，GUI 已经编译好了！


如果你要运行 GUI，你需要安装如下库:

```cmd
pip install requests ttkbootstrap pyperclip pywinstyles
```

CLI 则仅需要安装 `requests` 和 `tabulate`：
```cmd
pip install requests tabulate
```
## 使用截图

<img width="499" height="156" alt="Screenshot 2025-07-20 131318" src="https://github.com/user-attachments/assets/41a8dc68-0939-484d-82bb-b1d0bd460a94" />

<img width="1482" height="1150" alt="Screenshot 2025-07-24 222132" src="https://github.com/user-attachments/assets/3f5e64bc-d9cb-4086-88c2-5ceeb1a60b7c" />

<img width="1507" height="1186" alt="Screenshot 2025-07-24 222242" src="https://github.com/user-attachments/assets/a2d04528-7b74-4370-a694-709ce82b9cab" />

<img width="1488" height="1183" alt="Screenshot 2025-07-24 222311" src="https://github.com/user-attachments/assets/eab7c0d4-175a-4b8e-badb-f347b87dfb31" />



