# InsightMe 命令行结构化日记系统

## 项目简介

InsightMe 是一个极简、结构化的命令行日记系统，支持多用户数据隔离、结构化提问、历史记录回顾。每个用户的数据独立存储，所有记录不可修改/删除，保证数据安全和简洁。

---

## 主要功能
- 用户名登录（无需密码，自动数据隔离）
- 新建每日结构化日记（自动填入日期，结构化提问）
- 支持多行输入（如“做了什么”、“想法”、“明日计划”等）
- 查看历史记录（美观缩进展示）
- 不支持修改/删除，极简安全

---

## 目录结构
```
project_root/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md               # 项目说明
├── users/                  # 各用户独立数据库（自动生成）
├── utils/
│   └── db_helper.py        # 数据库操作
├── ui/
│   └── console.py          # 命令行交互（UI层）
└── service/
    └── diary_service.py    # 业务逻辑（Service层）
```

---

## 安装依赖

建议使用 Python 3.7 及以上版本。

```bash
pip install -r requirements.txt
```

---

## 使用方法

1. 运行主程序：
   ```bash
   python main.py
   ```
2. 按提示输入用户名（如 `xiaoming`），进入主菜单。
3. 选择“新建每日记录”，依次回答结构化问题。
   - **多行输入说明**：如“做了什么”、“想法”、“明日计划”等问题，支持多行输入。每输入一行按回车，最后输入空行结束。
4. 选择“查看历史记录”可回顾所有历史日记。
5. 选择“退出程序”即可安全退出。

---

## 打包为 Windows 可执行文件（exe）

推荐使用 PyInstaller，生成单文件夹模式，便于数据管理。

1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 打包：
   ```bash
   pyinstaller main.py
   ```
3. 打包后在 `dist/main/` 文件夹下找到 `main.exe`，双击即可运行。
   - **注意**：分发时请将整个 `dist/main/` 文件夹一起分发。

---

## 贡献与维护

- 欢迎提交 Issue 或 PR 反馈问题和建议。
- 代码结构清晰，便于二次开发和扩展。

---

## License

MIT
