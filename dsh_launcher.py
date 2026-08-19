# -*- coding: utf-8 -*-
"""
DeepSeek Harness 一键启动器 v3.0 — 标签页 + 插件管理
基于官网 https://www.deepseek.com/harness/ 开发
核心命令: npx @deepseek-ai/dsh web --port 3080
"""

import tkinter as tk
from tkinter import ttk, font, messagebox
import subprocess
import threading
import webbrowser
import os
import sys
import json
import re
import socket
import time
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw

# ============================================================
# 冻结环境 (PyInstaller) 下设置 TCL/TK 库路径
# ============================================================
if getattr(sys, 'frozen', False):
    _base = os.path.dirname(sys.executable)
    _meipass = getattr(sys, '_MEIPASS', _base)
    for _libname in ['tcl8.6', 'tk8.6']:
        _libpath = os.path.join(_meipass, _libname)
        if os.path.exists(_libpath):
            if _libname.startswith('tcl'):
                os.environ['TCL_LIBRARY'] = _libpath
            else:
                os.environ['TK_LIBRARY'] = _libpath

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

# ============================================================
# 配置
# ============================================================
APP_TITLE = "DeepSeek Harness — 一键启动器"
APP_VERSION = "v3.0"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dsh_launcher_config.json")

# 配色
C_BG="#edf1f7"; C_CARD="#ffffff"; C_HEADER="#1a1f36"; C_HEADER_SUB="#2d3561"
C_PRIMARY="#4f6df5"; C_PRIMARY_H="#3b5de7"; C_PRIMARY_L="#e8ecfe"
C_GREEN="#22c55e"; C_RED="#ef4444"; C_AMBER="#f59e0b"
C_TEXT="#1e293b"; C_TEXT2="#64748b"; C_TEXT3="#94a3b8"
C_BORDER="#e2e8f0"; C_LOG_BG="#0f172a"; C_LOG_FG="#e2e8f0"
C_LOG_TIME="#64748b"; C_LOG_OK="#4ade80"; C_LOG_ERR="#f87171"; C_LOG_INFO="#60a5fa"
C_BOTTOM="#f1f5f9"; C_TAB_ACTIVE=C_PRIMARY; C_TAB_IDLE=C_TEXT3

# 字体
F_H1=("Microsoft YaHei",14,"bold"); F_H2=("Microsoft YaHei",11,"bold")
F_BODY=("Microsoft YaHei",10); F_BODY_B=("Microsoft YaHei",10,"bold")
F_SMALL=("Microsoft YaHei",9); F_TINY=("Microsoft YaHei",8)
F_LOG=("Cascadia Code",9)

# ============================================================
# 插件数据库 — 按类别分类的热门插件
# ============================================================
PLUGIN_CATEGORIES = {
    "主题外观": "🎨",
    "记忆增强": "🧠",
    "界面优化": "🖥",
    "工具增强": "🔧",
    "安全认证": "🔒",
    "中文增强": "🀄",
    "模型接入": "🤖",
    "已安装": "✅",
}

PLUGIN_DB = [
    # 主题外观
    {"name":"dsh-dream-skin","cat":"主题外观","desc":"Dream Skin 换肤插件：精选 --dsw-alias-* 主题色系","ver":"latest"},
    {"name":"dsh-theme-plugin","cat":"主题外观","desc":"中国传统色主题包，国风配色一键切换","ver":"latest"},
    {"name":"dsh-catppuccin","cat":"主题外观","desc":"Catppuccin 柔和pastel主题，4种风味","ver":"latest"},
    {"name":"dsh-skin","cat":"主题外观","desc":"15种预设皮肤 + 13项可调颜色参数","ver":"latest"},
    {"name":"dsh-themes","cat":"主题外观","desc":"内置调色板、Open VSX 搜索导入、颜色编辑器","ver":"latest"},
    {"name":"dsh-dracula-theme","cat":"主题外观","desc":"Dracula 经典暗色主题 + Soft 变体","ver":"latest"},
    {"name":"dsh-oh-my-theme","cat":"主题外观","desc":"精选主题 + 文件工作区管理","ver":"latest"},
    {"name":"dsh-opencode-palette","cat":"主题外观","desc":"34款经典皮肤：东京霓虹、德古拉暗红等","ver":"latest"},
    {"name":"dsh-icon-theme","cat":"主题外观","desc":"自动检测 + 自定义图标主题","ver":"latest"},
    {"name":"dsh-theme-machine","cat":"主题外观","desc":"Person-of-Interest 监控HUD风格主题","ver":"latest"},
    # 记忆增强
    {"name":"dsh-mnemon","cat":"记忆增强","desc":"三层记忆控制：持久运行时上下文","ver":"latest"},
    {"name":"dsh-persona-memory","cat":"记忆增强","desc":"持久长期人设记忆 MEMORY.md/USER.md","ver":"latest"},
    {"name":"dsh-memory-gate","cat":"记忆增强","desc":"CBDC门控记忆：决定记忆注入策略","ver":"latest"},
    {"name":"dsh-layered-memory","cat":"记忆增强","desc":"L0~L3 分层蒸馏：对话→原子→场景→画像","ver":"latest"},
    {"name":"dsh-memory-vault","cat":"记忆增强","desc":"跨会话记忆库：remember/recall/forget","ver":"latest"},
    {"name":"dsh-agent-memory","cat":"记忆增强","desc":"跨会话长期记忆，schema验证","ver":"latest"},
    {"name":"dsh-memento","cat":"记忆增强","desc":"有界分层审批制跨会话记忆","ver":"latest"},
    {"name":"dsh-engramory","cat":"记忆增强","desc":"人类可读markdown长期记忆","ver":"latest"},
    {"name":"dsh-plugin-long-term-memory","cat":"记忆增强","desc":"长期记忆与自学习：观察→提取→回顾","ver":"latest"},
    {"name":"dsh-nocturne-memory","cat":"记忆增强","desc":"Nocturne Memory：自动长期记忆","ver":"latest"},
    # 界面优化
    {"name":"dshmarket","cat":"界面优化","desc":"可视化插件市场：浏览/搜索/一键安装","ver":"latest"},
    {"name":"dsh-web-plugin-manager","cat":"界面优化","desc":"Web UI 管理插件：列表/启用/禁用/安装","ver":"latest"},
    {"name":"dsh-context","cat":"界面优化","desc":"上下文洞察与管理仪表盘","ver":"latest"},
    {"name":"deepseek-harness-tui","cat":"界面优化","desc":"交互式终端 UI，dsh profile bundle","ver":"latest"},
    {"name":"deepseek-flow","cat":"界面优化","desc":"Markdown优先的可视化工作流插件","ver":"latest"},
    {"name":"dsh-gui-customization","cat":"界面优化","desc":"Nous Blue调色板 + 环境光效","ver":"latest"},
    {"name":"dsh-skin-switcher","cat":"界面优化","desc":"皮肤切换器：设置页一键切换已装皮肤","ver":"latest"},
    # 工具增强
    {"name":"dsh-vision-router","cat":"工具增强","desc":"文本Agent的视觉能力：免费视觉链(无需Key)","ver":"latest"},
    {"name":"dsh-plugin-deepeye","cat":"工具增强","desc":"原生视觉插件：为纯文本LLM添加图像理解","ver":"latest"},
    {"name":"dsh-find-plugin","cat":"工具增强","desc":"Agent内搜索插件：实时GitHub dsh-plugin topic","ver":"latest"},
    {"name":"dsh-harmony","cat":"工具增强","desc":"插件补丁库：运行时替换/装饰DSH插件","ver":"latest"},
    {"name":"dsh-plugin-wallpaper-engine","cat":"工具增强","desc":"Wallpaper Engine背景：渲染本地动态壁纸","ver":"latest"},
    # 安全认证
    {"name":"deepseek-harness-auth","cat":"安全认证","desc":"密码认证代理：Fail-closed安全网关","ver":"latest"},
    {"name":"dsh-lan-access","cat":"安全认证","desc":"LAN访问：绑定0.0.0.0 + crypto polyfill","ver":"latest"},
    # 中文增强
    {"name":"deepseek-harness-zh_pro","cat":"中文增强","desc":"中文增强：修正残留英文+中文优先提示","ver":"latest"},
    # 模型接入
    {"name":"@memtensor/memos-local-plugin","cat":"模型接入","desc":"Reflect2Evolve：L1/L2/L3分层记忆+反思","ver":"latest"},
]


class ToggleSwitch:
    """自定义开关组件"""
    def __init__(self, parent, text, variable, bg=C_CARD):
        self.variable = variable
        self.bg = bg
        self.frame = tk.Frame(parent, bg=bg)
        self.canvas = tk.Canvas(self.frame, width=44, height=24, bg=bg, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.label = tk.Label(self.frame, text=text, font=F_BODY, bg=bg, fg=C_TEXT)
        self.label.pack(side=tk.LEFT)
        self._draw()
        self.canvas.bind("<Button-1>", self._toggle)
        self.label.bind("<Button-1>", self._toggle)
        self.variable.trace_add('write', lambda *_: self._draw())

    def _draw(self):
        self.canvas.delete("all")
        if self.variable.get():
            self._rr(2, 3, 42, 21, 10, fill=C_PRIMARY)
            self.canvas.create_oval(26, 5, 38, 17, fill="white", outline="")
        else:
            self._rr(2, 3, 42, 21, 10, fill="#cbd5e1")
            self.canvas.create_oval(6, 5, 18, 17, fill="white", outline="")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2,
               x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        self.canvas.create_polygon(pts, smooth=True, **kw)

    def _toggle(self, e=None):
        self.variable.set(not self.variable.get())

    def pack(self, **kw):
        self.frame.pack(**kw)


class DSHLauncher:
    def __init__(self, root):
        self.root = root
        self.process = None
        self.is_running = False
        self.tray_icon = None
        self._browser_opened = False
        self._pulse_id = None
        self.installed_plugins = set()
        self.installing_plugins = set()  # 正在安装中的插件
        self.current_category = "主题外观"
        self.plugin_cards = {}

        self.load_config()
        self.setup_window()
        self.create_ui()
        self.update_status(False)
        self.log("就绪", "info")
        self.log("点击「一键启动」开始运行 DeepSeek Harness", "dim")

    # ============================================================
    # 配置
    # ============================================================
    def load_config(self):
        defaults = {'port': '3080', 'auto_open_browser': True, 'hide_to_tray': True, 'installed_plugins': []}
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        self.port_var = tk.StringVar(value=defaults['port'])
        self.auto_browser_var = tk.BooleanVar(value=defaults['auto_open_browser'])
        self.hide_tray_var = tk.BooleanVar(value=defaults['hide_to_tray'])
        self.installed_plugins = set(defaults.get('installed_plugins', []))

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'port': self.port_var.get(),
                    'auto_open_browser': self.auto_browser_var.get(),
                    'hide_to_tray': self.hide_tray_var.get(),
                    'installed_plugins': list(self.installed_plugins)
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ============================================================
    # 窗口
    # ============================================================
    def setup_window(self):
        self.root.title(APP_TITLE)
        self.root.geometry("720x680")
        self.root.minsize(720, 680)
        self.root.configure(bg=C_BG)
        try:
            icon_img = self._make_icon(32)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, self.icon_photo)
        except Exception:
            pass
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _make_icon(self, size):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
        if getattr(sys, 'frozen', False):
            meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            icon_path = os.path.join(meipass, "app_icon.png")
        try:
            img = Image.open(icon_path).convert("RGBA")
            return img.resize((size, size), Image.LANCZOS)
        except Exception:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([2, 2, size-2, size-2], radius=size//6, fill=(79, 109, 245, 255))
            return img

    # ============================================================
    # UI 主框架
    # ============================================================
    def create_ui(self):
        self._create_header()
        self._create_tab_bar()
        # 内容容器
        self.content_frame = tk.Frame(self.root, bg=C_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 12))
        # 两个标签页
        self.tab_general = tk.Frame(self.content_frame, bg=C_BG)
        self.tab_plugin = tk.Frame(self.content_frame, bg=C_BG)
        self._build_general_tab()
        self._build_plugin_tab()
        self._show_tab("general")
        self._create_footer()

    def _create_header(self):
        header = tk.Frame(self.root, bg=C_HEADER, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        inner = tk.Frame(header, bg=C_HEADER)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        left = tk.Frame(inner, bg=C_HEADER)
        left.pack(side=tk.LEFT)
        try:
            logo_img = self._make_icon(28)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(left, image=self.logo_photo, bg=C_HEADER).pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            pass
        tk.Label(left, text="DeepSeek Harness", font=F_H1, bg=C_HEADER, fg="white").pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(left, text="一键启动器", font=F_H2, bg=C_HEADER, fg="#94a3b8").pack(side=tk.LEFT)
        tk.Label(inner, text=f"  {APP_VERSION}  ", font=F_TINY, bg=C_HEADER_SUB, fg="#cbd5e1").pack(side=tk.RIGHT)

    def _create_tab_bar(self):
        """标签栏"""
        bar = tk.Frame(self.root, bg=C_CARD, height=42)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        bar.configure(highlightbackground=C_BORDER, highlightthickness=1)

        self.tab_buttons = {}
        for tab_id, label in [("general", "常规"), ("plugin", "插件")]:
            btn = tk.Label(
                bar, text=f"  {label}  ", font=F_BODY_B, bg=C_CARD, fg=C_TEXT3,
                cursor="hand2", padx=20, pady=10
            )
            btn.pack(side=tk.LEFT, padx=(8, 0))
            btn.bind("<Button-1>", lambda e, tid=tab_id: self._show_tab(tid))
            self.tab_buttons[tab_id] = btn

    def _show_tab(self, tab_id):
        """切换标签页"""
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(bg=C_PRIMARY_L, fg=C_PRIMARY)
            else:
                btn.configure(bg=C_CARD, fg=C_TEXT3)
        if tab_id == "general":
            self.tab_plugin.pack_forget()
            self.tab_general.pack(fill=tk.BOTH, expand=True)
        else:
            self.tab_general.pack_forget()
            self.tab_plugin.pack(fill=tk.BOTH, expand=True)

    # ============================================================
    # 常规标签页
    # ============================================================
    def _build_general_tab(self):
        body = self.tab_general
        self._create_status_card(body)
        tk.Frame(body, bg=C_BG, height=10).pack(fill=tk.X)
        self._create_settings_card(body)
        tk.Frame(body, bg=C_BG, height=10).pack(fill=tk.X)
        self._create_log_card(body)

    def _create_status_card(self, parent):
        card = tk.Frame(parent, bg=C_CARD, relief=tk.FLAT)
        card.pack(fill=tk.X)
        card.configure(highlightbackground=C_BORDER, highlightthickness=1)
        content = tk.Frame(card, bg=C_CARD)
        content.pack(fill=tk.X, padx=20, pady=16)

        left = tk.Frame(content, bg=C_CARD)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        row1 = tk.Frame(left, bg=C_CARD)
        row1.pack(anchor=tk.W)
        self.status_canvas = tk.Canvas(row1, width=16, height=16, bg=C_CARD, highlightthickness=0)
        self.status_circle = self.status_canvas.create_oval(3, 3, 13, 13, fill=C_RED, outline="")
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self.status_label = tk.Label(row1, text="已停止", font=F_H2, bg=C_CARD, fg=C_TEXT)
        self.status_label.pack(side=tk.LEFT)

        row2 = tk.Frame(left, bg=C_CARD)
        row2.pack(anchor=tk.W, pady=(8, 0))
        tk.Label(row2, text="访问地址", font=F_SMALL, bg=C_CARD, fg=C_TEXT3).pack(side=tk.LEFT, padx=(0, 8))
        self.addr_label = tk.Label(row2, text="—", font=F_BODY_B, bg=C_CARD, fg=C_TEXT3, cursor="hand2")
        self.addr_label.pack(side=tk.LEFT)
        self.addr_label.bind("<Button-1>", self._on_addr_click)
        self.copy_btn = tk.Button(row2, text=" 复制 ", font=F_TINY, bg=C_BG, fg=C_TEXT2,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2", state=tk.DISABLED,
            command=self._copy_addr, activebackground=C_BG)
        self.copy_btn.pack(side=tk.LEFT, padx=(10, 0))

        right = tk.Frame(content, bg=C_CARD)
        right.pack(side=tk.RIGHT)
        self.stop_btn = tk.Button(right, text="  停止  ", font=F_BODY, bg=C_CARD, fg=C_TEXT2,
            relief=tk.SOLID, bd=1, padx=14, pady=7, cursor="hand2",
            command=self.stop_service, state=tk.DISABLED, activebackground=C_BG)
        self.stop_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self.start_btn = tk.Button(right, text="  ⚡ 一键启动  ", font=F_BODY_B, bg=C_PRIMARY, fg="white",
            relief=tk.FLAT, bd=0, padx=18, pady=7, cursor="hand2",
            command=self.start_service, activebackground=C_PRIMARY_H)
        self.start_btn.pack(side=tk.RIGHT)
        self._btn_hover(self.start_btn, C_PRIMARY, C_PRIMARY_H, "white", "white")
        self._btn_hover(self.stop_btn, C_CARD, C_BG, C_TEXT2, C_TEXT)

    def _create_settings_card(self, parent):
        card = tk.Frame(parent, bg=C_CARD, relief=tk.FLAT)
        card.pack(fill=tk.X)
        card.configure(highlightbackground=C_BORDER, highlightthickness=1)
        content = tk.Frame(card, bg=C_CARD)
        content.pack(fill=tk.X, padx=20, pady=16)
        tk.Label(content, text="设置", font=F_H2, bg=C_CARD, fg=C_TEXT).pack(anchor=tk.W)

        port_row = tk.Frame(content, bg=C_CARD)
        port_row.pack(fill=tk.X, pady=(12, 0))
        tk.Label(port_row, text="端口", font=F_BODY, bg=C_CARD, fg=C_TEXT2).pack(side=tk.LEFT)
        tk.Entry(port_row, textvariable=self.port_var, font=F_BODY_B, width=6,
            relief=tk.SOLID, bd=1, justify=tk.CENTER,
            highlightthickness=1, highlightcolor=C_PRIMARY, highlightbackground=C_BORDER
        ).pack(side=tk.LEFT, padx=(10, 6))
        tk.Label(port_row, text="默认 3080，被占用时可修改", font=F_SMALL, bg=C_CARD, fg=C_TEXT3).pack(side=tk.LEFT)

        toggle_row = tk.Frame(content, bg=C_CARD)
        toggle_row.pack(fill=tk.X, pady=(14, 0))
        ToggleSwitch(toggle_row, "启动后自动打开浏览器", self.auto_browser_var, bg=C_CARD).pack(side=tk.LEFT)
        ToggleSwitch(toggle_row, "最小化时隐藏到托盘", self.hide_tray_var, bg=C_CARD).pack(side=tk.LEFT, padx=(28, 0))

        self.auto_browser_var.trace_add('write', lambda *_: self.save_config())
        self.hide_tray_var.trace_add('write', lambda *_: self.save_config())
        self.port_var.trace_add('write', lambda *_: self.save_config())

    def _create_log_card(self, parent):
        card = tk.Frame(parent, bg=C_CARD, relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True)
        card.configure(highlightbackground=C_BORDER, highlightthickness=1)
        content = tk.Frame(card, bg=C_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        header = tk.Frame(content, bg=C_CARD)
        header.pack(fill=tk.X)
        tk.Label(header, text="运行日志", font=F_H2, bg=C_CARD, fg=C_TEXT).pack(side=tk.LEFT)
        self.log_count_label = tk.Label(header, text="0 条", font=F_TINY, bg=C_CARD, fg=C_TEXT3)
        self.log_count_label.pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(header, text="清空", font=F_TINY, bg=C_BG, fg=C_TEXT2,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._clear_log, activebackground=C_BORDER).pack(side=tk.RIGHT)

        log_wrap = tk.Frame(content, bg=C_LOG_BG)
        log_wrap.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        log_wrap.configure(highlightbackground=C_LOG_BG, highlightthickness=1)
        self.log_text = tk.Text(log_wrap, font=F_LOG, bg=C_LOG_BG, fg=C_LOG_FG,
            relief=tk.FLAT, bd=0, padx=12, pady=10, wrap=tk.WORD, state=tk.DISABLED,
            highlightthickness=0, insertbackground=C_LOG_FG)
        scroll = ttk.Scrollbar(log_wrap, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for tag, fg in [('time',C_LOG_TIME),('info',C_LOG_INFO),('ok',C_LOG_OK),('err',C_LOG_ERR),('dim',C_TEXT3),('normal',C_LOG_FG)]:
            self.log_text.tag_configure(tag, foreground=fg)
        self._log_count = 0

    # ============================================================
    # 插件标签页
    # ============================================================
    def _build_plugin_tab(self):
        parent = self.tab_plugin

        # 顶部工具栏
        toolbar = tk.Frame(parent, bg=C_CARD)
        toolbar.pack(fill=tk.X)
        toolbar.configure(highlightbackground=C_BORDER, highlightthickness=1)

        toolbar_inner = tk.Frame(toolbar, bg=C_CARD)
        toolbar_inner.pack(fill=tk.X, padx=16, pady=12)

        # 搜索框
        tk.Label(toolbar_inner, text="🔍", font=F_BODY, bg=C_CARD, fg=C_TEXT3).pack(side=tk.LEFT, padx=(0, 6))
        self.plugin_search_var = tk.StringVar()
        self.plugin_search_var.trace_add('write', lambda *_: self._filter_plugins())
        search_entry = tk.Entry(toolbar_inner, textvariable=self.plugin_search_var, font=F_BODY,
            width=20, relief=tk.SOLID, bd=1,
            highlightthickness=1, highlightcolor=C_PRIMARY, highlightbackground=C_BORDER)
        search_entry.pack(side=tk.LEFT)
        search_entry.insert(0, "搜索插件...")
        search_entry.configure(fg=C_TEXT3)
        search_entry.bind("<FocusIn>", lambda e: self._search_focus_in(search_entry))
        search_entry.bind("<FocusOut>", lambda e: self._search_focus_out(search_entry))

        # 刷新按钮
        self.refresh_btn = tk.Button(toolbar_inner, text="🔄 刷新插件列表", font=F_SMALL,
            bg=C_PRIMARY_L, fg=C_PRIMARY, relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=self._refresh_plugins, activebackground=C_PRIMARY)
        self.refresh_btn.pack(side=tk.RIGHT)

        # 已安装数量
        self.installed_count_label = tk.Label(toolbar_inner, text="已安装: 0", font=F_SMALL, bg=C_CARD, fg=C_TEXT3)
        self.installed_count_label.pack(side=tk.RIGHT, padx=(12, 12))

        # 主体：左侧分类 + 右侧插件列表
        main = tk.Frame(parent, bg=C_BG)
        main.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        # 左侧分类栏
        cat_frame = tk.Frame(main, bg=C_CARD, width=140)
        cat_frame.pack(side=tk.LEFT, fill=tk.Y)
        cat_frame.pack_propagate(False)
        cat_frame.configure(highlightbackground=C_BORDER, highlightthickness=1)

        tk.Label(cat_frame, text=" 分类", font=F_BODY_B, bg=C_CARD, fg=C_TEXT).pack(anchor=tk.W, padx=12, pady=(12, 8))

        self.cat_buttons = {}
        for cat, icon in PLUGIN_CATEGORIES.items():
            btn = tk.Label(cat_frame, text=f" {icon} {cat}", font=F_SMALL, bg=C_CARD, fg=C_TEXT2,
                cursor="hand2", padx=12, pady=6, anchor=tk.W)
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
            self.cat_buttons[cat] = btn

        # 右侧插件列表（可滚动）
        list_frame = tk.Frame(main, bg=C_BG)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # 滚动容器
        canvas_frame = tk.Frame(list_frame, bg=C_BG)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.plugin_canvas = tk.Canvas(canvas_frame, bg=C_BG, highlightthickness=0)
        plugin_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.plugin_canvas.yview)
        self.plugin_scroll_inner = tk.Frame(self.plugin_canvas, bg=C_BG)
        self.plugin_scroll_inner.bind("<Configure>",
            lambda e: self.plugin_canvas.configure(scrollregion=self.plugin_canvas.bbox("all")))
        self.canvas_window = self.plugin_canvas.create_window((0, 0), window=self.plugin_scroll_inner, anchor=tk.NW)
        self.plugin_canvas.bind("<Configure>",
            lambda e: self.plugin_canvas.itemconfig(self.canvas_window, width=e.width))
        plugin_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.plugin_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.plugin_canvas.configure(yscrollcommand=plugin_scroll.set)

        # 鼠标滚轮绑定
        self.plugin_canvas.bind_all("<MouseWheel>",
            lambda e: self.plugin_canvas.yview_scroll(int(-e.delta/120), "units"))

        # 初始渲染插件列表
        self._render_plugins()

        # 后台检测已安装插件
        threading.Thread(target=self._detect_installed, daemon=True).start()

    def _search_focus_in(self, entry):
        if entry.get() == "搜索插件...":
            entry.delete(0, tk.END)
            entry.configure(fg=C_TEXT)

    def _search_focus_out(self, entry):
        if not entry.get():
            entry.insert(0, "搜索插件...")
            entry.configure(fg=C_TEXT3)

    def _select_category(self, cat):
        self.current_category = cat
        for c, btn in self.cat_buttons.items():
            if c == cat:
                btn.configure(bg=C_PRIMARY_L, fg=C_PRIMARY)
            else:
                btn.configure(bg=C_CARD, fg=C_TEXT2)
        self._render_plugins()

    def _filter_plugins(self):
        self._render_plugins()

    def _get_filtered_plugins(self):
        search = self.plugin_search_var.get().strip().lower()
        if search == "搜索插件...":
            search = ""
        result = []

        if self.current_category == "已安装":
            # 已安装类目：只显示已安装的插件
            for p in PLUGIN_DB:
                if p["name"] not in self.installed_plugins:
                    continue
                if search and search not in p["name"].lower() and search not in p["desc"].lower():
                    continue
                result.append(p)
            # 也包含不在 PLUGIN_DB 中但已安装的插件
            db_names = {p["name"] for p in PLUGIN_DB}
            for name in self.installed_plugins:
                if name in db_names:
                    continue
                if search and search not in name.lower():
                    continue
                result.append({"name": name, "cat": "已安装", "desc": "已安装插件", "ver": "latest"})
            return result

        # 其他分类：显示该分类下所有插件，不受已安装状态影响
        for p in PLUGIN_DB:
            if p["cat"] != self.current_category:
                continue
            if search and search not in p["name"].lower() and search not in p["desc"].lower():
                continue
            result.append(p)
        return result

    def _render_plugins(self):
        """渲染插件卡片列表"""
        # 清空旧卡片
        for child in self.plugin_scroll_inner.winfo_children():
            child.destroy()
        self.plugin_cards.clear()

        plugins = self._get_filtered_plugins()

        if not plugins:
            msg = "暂无已安装插件，去其他类目安装吧~" if self.current_category == "已安装" else "暂无匹配插件"
            tk.Label(self.plugin_scroll_inner, text=msg, font=F_BODY,
                bg=C_BG, fg=C_TEXT3).pack(pady=40)
            return

        for p in plugins:
            self._create_plugin_card(self.plugin_scroll_inner, p)

        # 调试日志
        installed_in_view = sum(1 for p in plugins if p["name"] in self.installed_plugins)
        self.log(f"渲染 {self.current_category}: {len(plugins)} 个插件, 其中 {installed_in_view} 个已安装", "dim")

    def _create_plugin_card(self, parent, plugin):
        """创建单个插件卡片"""
        name = plugin["name"]
        is_installed = name in self.installed_plugins
        is_installing = name in self.installing_plugins

        card = tk.Frame(parent, bg=C_CARD, relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 6))
        card.configure(highlightbackground=C_BORDER, highlightthickness=1)

        content = tk.Frame(card, bg=C_CARD)
        content.pack(fill=tk.X, padx=14, pady=10)

        # 右侧：操作按钮（先创建右侧，确保按钮始终可见）
        btn_frame = tk.Frame(content, bg=C_CARD)
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        if is_installing:
            btn = tk.Button(btn_frame, text="安装中...", font=F_SMALL, bg=C_TEXT3, fg="white",
                relief=tk.FLAT, padx=14, pady=5, state=tk.DISABLED)
        elif is_installed:
            btn = tk.Button(btn_frame, text="卸载", font=F_BODY_B, bg=C_RED, fg="white",
                relief=tk.FLAT, padx=16, pady=5, cursor="hand2",
                command=lambda n=name: self._uninstall_plugin(n),
                activebackground="#dc2626")
        else:
            btn = tk.Button(btn_frame, text="安装", font=F_SMALL, bg=C_PRIMARY, fg="white",
                relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
                command=lambda n=name: self._install_plugin(n),
                activebackground=C_PRIMARY_H)
        btn.pack()

        # 左侧：名称 + 描述
        left = tk.Frame(content, bg=C_CARD)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 名称行
        name_row = tk.Frame(left, bg=C_CARD)
        name_row.pack(anchor=tk.W)

        tk.Label(name_row, text=name, font=F_BODY_B, bg=C_CARD, fg=C_TEXT).pack(side=tk.LEFT)

        # 类别标签
        tk.Label(name_row, text=f" {plugin['cat']} ", font=F_TINY,
            bg=C_PRIMARY_L, fg=C_PRIMARY, padx=4).pack(side=tk.LEFT, padx=(8, 0))

        # 状态标签
        if is_installing:
            tk.Label(name_row, text=" 安装中... ", font=F_TINY, bg=C_AMBER, fg="white", padx=4).pack(side=tk.LEFT, padx=(6, 0))
        elif is_installed:
            tk.Label(name_row, text=" ✓ 已安装 ", font=F_TINY, bg=C_GREEN, fg="white", padx=4).pack(side=tk.LEFT, padx=(6, 0))

        # 描述
        tk.Label(left, text=plugin["desc"], font=F_SMALL, bg=C_CARD, fg=C_TEXT2).pack(anchor=tk.W, pady=(4, 0))

        self.plugin_cards[name] = {"card": card, "btn": btn, "plugin": plugin}

    # ============================================================
    # 插件管理逻辑
    # ============================================================
    def _install_plugin(self, name):
        """安装插件"""
        if name in self.installing_plugins:
            return  # 已在安装中
        self.installing_plugins.add(name)
        self.log(f"正在安装插件: {name}", "info")
        # 更新按钮状态
        if name in self.plugin_cards:
            self.plugin_cards[name]["btn"].configure(text="安装中...", state=tk.DISABLED, bg=C_TEXT3)

        threading.Thread(target=self._do_install, args=(name,), daemon=True).start()

    def _get_enhanced_env(self):
        """获取增强的 PATH 环境变量，确保 pnpm 可被找到"""
        env = os.environ.copy()
        extra_paths = []

        # 1. 检查常见 npm 全局目录
        candidates = [
            os.path.expanduser('~/.npm-global'),
            os.path.expanduser('~/AppData/Roaming/npm'),
            os.path.join(os.environ.get('APPDATA', ''), 'npm'),
        ]
        # 2. 尝试 npm prefix -g
        try:
            result = subprocess.run('npm prefix -g', shell=True, capture_output=True,
                text=True, encoding='utf-8', errors='replace', timeout=5)
            if result.returncode == 0:
                p = result.stdout.strip()
                if p:
                    candidates.append(p)
        except Exception:
            pass

        # 3. 验证哪些目录确实包含 pnpm
        for c in candidates:
            if c and os.path.exists(os.path.join(c, 'pnpm.cmd')):
                extra_paths.append(c)

        # 4. 也检查 pnpm 自身安装路径
        pnpm_home = os.path.expanduser('~/AppData/Local/pnpm')
        if os.path.exists(pnpm_home):
            extra_paths.append(pnpm_home)

        if extra_paths:
            env['PATH'] = os.pathsep.join(extra_paths) + os.pathsep + env.get('PATH', '')

        return env

    def _do_install(self, name):
        try:
            env = self._get_enhanced_env()
            dsh_dir = os.path.expanduser('~/.dsh/profiles/web')

            # 方法1: dsh plugin add
            cmd = f'npx @deepseek-ai/dsh plugin --profile web add {name}'
            self.root.after(0, self.log, f"执行: {cmd}", "dim")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=120, env=env)
            output = (result.stdout + result.stderr).strip()

            if result.returncode == 0:
                self.installed_plugins.add(name)
                self.installing_plugins.discard(name)
                self.save_config()
                self.root.after(0, self.log, f"✓ 插件安装成功: {name}", "ok")
                self.root.after(0, self._render_plugins)
                self.root.after(0, self._update_installed_count)
                return

            # 方法2: pnpm add 直接在 profile 目录执行
            self.root.after(0, self.log, "dsh 命令失败，尝试 pnpm 直接安装...", "dim")
            pnpm_cmd = f'pnpm add {name}'
            self.root.after(0, self.log, f"执行: {pnpm_cmd} (cwd={dsh_dir})", "dim")
            result2 = subprocess.run(pnpm_cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=120, env=env, cwd=dsh_dir)
            output2 = (result2.stdout + result2.stderr).strip()

            if result2.returncode == 0:
                self.installed_plugins.add(name)
                self.installing_plugins.discard(name)
                self.save_config()
                self.root.after(0, self.log, f"✓ 插件安装成功: {name}", "ok")
                self.root.after(0, self._render_plugins)
                self.root.after(0, self._update_installed_count)
                return

            # 两种方法都失败
            self.installing_plugins.discard(name)
            self.root.after(0, self.log, f"✗ 插件安装失败: {name}", "err")
            for line in (output + '\n' + output2).split('\n')[:5]:
                line = line.strip()
                if line:
                    self.root.after(0, self.log, f"  {line}", "dim")
            if 'pnpm' in (output + output2).lower():
                self.root.after(0, self.log, "提示: 缺少 pnpm，正在自动安装...", "info")
                self._auto_install_pnpm(name, is_install=True)
                return
            self.root.after(0, self._render_plugins)
        except subprocess.TimeoutExpired:
            self.installing_plugins.discard(name)
            self.root.after(0, self.log, f"✗ 安装超时(120s): {name}", "err")
            self.root.after(0, self._render_plugins)
        except Exception as e:
            self.installing_plugins.discard(name)
            self.root.after(0, self.log, f"✗ 安装出错: {e}", "err")
            self.root.after(0, self._render_plugins)

    def _auto_install_pnpm(self, plugin_name, is_install=True):
        """自动安装 pnpm 后重试插件操作"""
        def _do():
            try:
                env = self._get_enhanced_env()
                self.root.after(0, self.log, "正在安装 pnpm: npm install -g pnpm", "info")
                result = subprocess.run('npm install -g pnpm', shell=True, capture_output=True,
                    text=True, encoding='utf-8', errors='replace', timeout=60, env=env)
                if result.returncode == 0:
                    self.root.after(0, self.log, "✓ pnpm 安装成功，重试插件操作", "ok")
                    # 重试
                    if is_install:
                        self._do_install(plugin_name)
                    else:
                        self._do_uninstall(plugin_name)
                else:
                    out = (result.stdout + result.stderr).strip()
                    self.installing_plugins.discard(plugin_name)
                    self.root.after(0, self.log, f"✗ pnpm 安装失败: {out[:100]}", "err")
                    self.root.after(0, self._render_plugins)
            except Exception as e:
                self.installing_plugins.discard(plugin_name)
                self.root.after(0, self.log, f"✗ pnpm 自动安装出错: {e}", "err")
                self.root.after(0, self._render_plugins)
        threading.Thread(target=_do, daemon=True).start()

    def _uninstall_plugin(self, name):
        """卸载插件"""
        if name in self.installing_plugins:
            return
        self.installing_plugins.add(name)  # 复用作为“操作中”标记
        self.log(f"正在卸载插件: {name}", "info")
        if name in self.plugin_cards:
            self.plugin_cards[name]["btn"].configure(text="卸载中...", state=tk.DISABLED, bg=C_TEXT3)

        threading.Thread(target=self._do_uninstall, args=(name,), daemon=True).start()

    def _do_uninstall(self, name):
        try:
            env = self._get_enhanced_env()
            dsh_dir = os.path.expanduser('~/.dsh/profiles/web')

            # 方法1: dsh plugin remove
            cmd = f'npx @deepseek-ai/dsh plugin --profile web remove {name}'
            self.root.after(0, self.log, f"执行: {cmd}", "dim")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=60, env=env)
            output = (result.stdout + result.stderr).strip()

            if result.returncode == 0:
                self.installed_plugins.discard(name)
                self.installing_plugins.discard(name)
                self.save_config()
                self.root.after(0, self.log, f"✓ 插件已卸载: {name}", "ok")
                self.root.after(0, self._render_plugins)
                self.root.after(0, self._update_installed_count)
                return

            # 方法2: pnpm remove 直接在 profile 目录执行
            self.root.after(0, self.log, "dsh 命令失败，尝试 pnpm 直接卸载...", "dim")
            pnpm_cmd = f'pnpm remove {name}'
            self.root.after(0, self.log, f"执行: {pnpm_cmd} (cwd={dsh_dir})", "dim")
            result2 = subprocess.run(pnpm_cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=60, env=env, cwd=dsh_dir)
            output2 = (result2.stdout + result2.stderr).strip()

            if result2.returncode == 0:
                self.installed_plugins.discard(name)
                self.installing_plugins.discard(name)
                self.save_config()
                self.root.after(0, self.log, f"✓ 插件已卸载: {name}", "ok")
                self.root.after(0, self._render_plugins)
                self.root.after(0, self._update_installed_count)
                return

            # 两种方法都失败
            self.installing_plugins.discard(name)
            self.root.after(0, self.log, f"✗ 插件卸载失败: {name}", "err")
            for line in (output + '\n' + output2).split('\n')[:5]:
                line = line.strip()
                if line:
                    self.root.after(0, self.log, f"  {line}", "dim")
            if 'pnpm' in (output + output2).lower():
                self.root.after(0, self.log, "提示: 缺少 pnpm，正在自动安装...", "info")
                self._auto_install_pnpm(name, is_install=False)
                return
            self.root.after(0, self._render_plugins)
        except Exception as e:
            self.installing_plugins.discard(name)
            self.root.after(0, self.log, f"✗ 卸载出错: {e}", "err")
            self.root.after(0, self._render_plugins)

    def _reset_plugin_btn(self, name, is_installed):
        """恢复插件按钮状态"""
        if name not in self.plugin_cards:
            return
        btn = self.plugin_cards[name]["btn"]
        btn.configure(state=tk.NORMAL)
        if is_installed:
            btn.configure(text="卸载", bg=C_RED_L, fg=C_RED)
        else:
            btn.configure(text="安装", bg=C_PRIMARY, fg="white")

    def _update_installed_count(self):
        self.installed_count_label.configure(text=f"已安装: {len(self.installed_plugins)}")

    def _detect_installed(self):
        """检测已安装的插件 — 从 cordis.patch.yml + pnpm list + 配置文件综合检测"""
        try:
            # 方法1: 解析 cordis.patch.yml（dsh 插件安装的真正位置）
            patch_file = os.path.expanduser('~/.dsh/profiles/web/cordis.patch.yml')
            if os.path.exists(patch_file):
                with open(patch_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content and content != '[]':
                    # 尝试提取插件名（YAML 格式，查找 insert/add 条目中的包名）
                    for line in content.split('\n'):
                        line = line.strip()
                        # 匹配 npm 包名格式
                        m = re.search(r'(@?[\w][\w.-]*/[\w][\w.-]*|@?[\w][\w.-]*)', line)
                        if m:
                            pkg = m.group(1)
                            if not pkg.startswith('@deepseek-ai/') and not pkg.startswith('#'):
                                self.installed_plugins.add(pkg)

            # 方法2: 用 pnpm list 检测（需要完整路径）
            try:
                pnpm_path = os.path.join(os.path.expanduser('~/.npm-global'), 'pnpm.cmd')
                if not os.path.exists(pnpm_path):
                    # 尝试 npm prefix -g 获取路径
                    r = subprocess.run('npm prefix -g', shell=True, capture_output=True,
                        text=True, encoding='utf-8', errors='replace', timeout=5)
                    if r.returncode == 0:
                        pnpm_path = os.path.join(r.stdout.strip(), 'pnpm.cmd')

                if os.path.exists(pnpm_path):
                    dsh_dir = os.path.expanduser('~/.dsh/profiles/web')
                    result = subprocess.run(
                        [pnpm_path, 'list', '--depth', '0', '--json'],
                        cwd=dsh_dir, capture_output=True, text=True,
                        encoding='utf-8', errors='replace', timeout=15)
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        if data and isinstance(data, list):
                            deps = data[0].get('dependencies', {})
                            for dep_name in deps:
                                if not dep_name.startswith('@deepseek-ai/'):
                                    self.installed_plugins.add(dep_name)
            except Exception:
                pass

            # 方法3: 配置文件中已记录的（由本启动器安装的）
            # installed_plugins 已在 load_config 中加载

            # 保存并更新 UI
            self.save_config()
            if self.installed_plugins:
                self.root.after(0, self.log, f"检测到 {len(self.installed_plugins)} 个已安装插件", "info")
            self.root.after(0, self._update_installed_count)
            self.root.after(0, self._render_plugins)
        except Exception:
            pass

    def _refresh_plugins(self):
        """刷新插件列表 — 从 npm 搜索最新插件"""
        self.refresh_btn.configure(text="刷新中...", state=tk.DISABLED)
        self.log("正在从 npm 获取最新插件列表...", "info")
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        """后台执行 npm search 获取最新插件"""
        env = self._get_enhanced_env()
        search_terms = [
            ("dsh-plugin", "工具增强"),
            ("dsh theme", "主题外观"),
            ("dsh memory", "记忆增强"),
            ("deepseek harness plugin", "界面优化"),
        ]
        new_plugins = []
        seen_names = set()

        for term, default_cat in search_terms:
            try:
                cmd = f'npm search "{term}" --json'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=30, env=env)
                if result.returncode == 0:
                    import json as j
                    data = j.loads(result.stdout)
                    for p in data:
                        name = p.get("name", "")
                        if name.startswith("@deepseek-ai/") or name in seen_names:
                            continue
                        desc = (p.get("description") or "")[:80]
                        ver = p.get("version", "latest")
                        if not desc:
                            continue
                        # 简单分类推断
                        cat = default_cat
                        nl = name.lower()
                        dl = desc.lower()
                        if "theme" in nl or "skin" in nl or "palette" in nl or "color" in dl:
                            cat = "主题外观"
                        elif "memory" in nl or "mem" in nl:
                            cat = "记忆增强"
                        elif "auth" in nl or "security" in nl or "safe" in dl:
                            cat = "安全认证"
                        elif "zh" in nl or "中文" in dl or "chinese" in dl:
                            cat = "中文增强"
                        elif "vision" in nl or "tool" in nl or "find" in nl:
                            cat = "工具增强"
                        elif "ui" in nl or "manager" in nl or "market" in nl:
                            cat = "界面优化"

                        new_plugins.append({"name": name, "cat": cat, "desc": desc, "ver": ver})
                        seen_names.add(name)
            except Exception:
                continue

        if new_plugins:
            # 合并到 PLUGIN_DB
            global PLUGIN_DB
            existing_names = {p["name"] for p in PLUGIN_DB}
            for p in new_plugins:
                if p["name"] not in existing_names:
                    PLUGIN_DB.append(p)

            self.root.after(0, self.log, f"✓ 获取到 {len(new_plugins)} 个插件，新增 {len(new_plugins) - len(existing_names & seen_names)} 个", "ok")
            self.root.after(0, self._render_plugins)
        else:
            self.root.after(0, self.log, "未获取到新插件，使用内置列表", "dim")

        self.root.after(0, self._reset_refresh_btn)

    def _reset_refresh_btn(self):
        self.refresh_btn.configure(text="🔄 刷新插件列表", state=tk.NORMAL)

    # ============================================================
    # 底栏
    # ============================================================
    def _create_footer(self):
        footer = tk.Frame(self.root, bg=C_BOTTOM, height=28)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        footer.pack_propagate(False)
        tk.Label(footer, text=f"  DeepSeek Harness 一键启动器  ·  关闭窗口后常驻系统托盘  ·  {APP_VERSION}",
            font=F_TINY, bg=C_BOTTOM, fg=C_TEXT3).pack(side=tk.LEFT, pady=5)


    # ============================================================
    # 辅助
    # ============================================================
    def _btn_hover(self, btn, bg_n, bg_h, fg_n, fg_h):
        btn.bind("<Enter>", lambda e: btn.configure(bg=bg_h, fg=fg_h))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg_n, fg=fg_n))

    # ============================================================
    # 日志
    # ============================================================
    def log(self, message, level="normal"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] ", 'time')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self._log_count += 1
        self.log_count_label.configure(text=f"{self._log_count} 条")

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self._log_count = 0
        self.log_count_label.configure(text="0 条")

    # ============================================================
    # 启动/停止
    # ============================================================
    def start_service(self):
        if self.is_running:
            return
        port = self.port_var.get().strip()
        if not port.isdigit() or int(port) < 1 or int(port) > 65535:
            messagebox.showwarning("端口错误", "请输入有效的端口号 (1-65535)")
            return
        self.save_config()
        self.start_btn.configure(state=tk.DISABLED, bg=C_TEXT3)
        self.log(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}", "dim")
        self.log(f"正在启动: npx @deepseek-ai/dsh web --port {port}", "info")
        threading.Thread(target=self._run_process, args=(port,), daemon=True).start()

    def _run_process(self, port):
        try:
            cmd = f'npx @deepseek-ai/dsh web --port {port}'
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE, text=True, bufsize=1, encoding='utf-8', errors='replace', shell=True)
            self.is_running = True
            self.root.after(0, self.update_status, True)
            for line in self.process.stdout:
                line = line.rstrip()
                if line:
                    self.root.after(0, self._process_output, line, port)
            ret = self.process.wait()
            self.is_running = False
            self.root.after(0, self.update_status, False)
            if ret != 0:
                self.root.after(0, self.log, f"进程退出，返回码: {ret}", "err")
        except FileNotFoundError:
            self.root.after(0, self.log, "未找到 npx，请先安装 Node.js", "err")
            self.root.after(0, self.log, "下载地址: https://nodejs.org/", "dim")
            self.root.after(0, self.update_status, False)
        except Exception as e:
            self.root.after(0, self.log, f"启动失败: {e}", "err")
            self.root.after(0, self.update_status, False)

    def _process_output(self, line, port):
        self.log(line, "normal")
        if re.search(r'localhost|127\.0\.0\.1|ready|started|listening|dsh web', line, re.IGNORECASE):
            if not self._browser_opened:
                self._browser_opened = True
                addr = f"http://127.0.0.1:{port}"
                self.log(f"服务输出就绪信号，正在确认端口 {port} 可访问...", "info")
                threading.Thread(target=self._wait_and_open_browser, args=(addr, port), daemon=True).start()

    def _wait_and_open_browser(self, addr, port):
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1", int(port)), timeout=1):
                    import urllib.request
                    try:
                        urllib.request.urlopen(urllib.request.Request(addr, method='HEAD'), timeout=2)
                    except Exception:
                        pass
                    self.root.after(0, self._on_service_ready, addr)
                    return
            except (ConnectionRefusedError, socket.timeout, OSError):
                pass
            time.sleep(0.5)
        self.root.after(0, self.log, f"端口 {port} 确认超时，请稍后手动访问: {addr}", "err")

    def _on_service_ready(self, addr):
        self.log(f"✓ 服务已就绪，访问地址: {addr}", "ok")
        if self.auto_browser_var.get():
            self.log("正在打开浏览器...", "info")
            webbrowser.open(addr)

    def stop_service(self):
        if not self.is_running or not self.process:
            return
        self.log("正在停止服务...", "info")
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/PID', str(self.process.pid), '/T', '/F'], capture_output=True)
            else:
                self.process.terminate()
        except Exception as e:
            self.log(f"停止出错: {e}", "err")
        self.is_running = False
        self.update_status(False)
        self._browser_opened = False
        self.log("服务已停止", "dim")

    # ============================================================
    # 状态
    # ============================================================
    def update_status(self, running):
        self.is_running = running
        if running:
            self.status_canvas.itemconfig(self.status_circle, fill=C_GREEN)
            self.status_label.configure(text="运行中", fg=C_GREEN)
            self.addr_label.configure(text=f"http://127.0.0.1:{self.port_var.get()}", fg=C_PRIMARY)
            self.copy_btn.configure(state=tk.NORMAL, fg=C_TEXT2)
            self.start_btn.configure(state=tk.DISABLED, bg=C_TEXT3)
            self.stop_btn.configure(state=tk.NORMAL)
            self._start_pulse()
        else:
            self.status_canvas.itemconfig(self.status_circle, fill=C_RED)
            self.status_label.configure(text="已停止", fg=C_TEXT2)
            self.addr_label.configure(text="—", fg=C_TEXT3)
            self.copy_btn.configure(state=tk.DISABLED, fg=C_TEXT3)
            self.start_btn.configure(state=tk.NORMAL, bg=C_PRIMARY)
            self.stop_btn.configure(state=tk.DISABLED)
            self._stop_pulse()

    def _start_pulse(self):
        self._stop_pulse()
        colors = [C_GREEN, "#4ade80", C_GREEN, "#16a34a"]
        idx = [0]
        def pulse():
            if not self.is_running:
                return
            self.status_canvas.itemconfig(self.status_circle, fill=colors[idx[0] % len(colors)])
            idx[0] += 1
            self._pulse_id = self.root.after(600, pulse)
        pulse()

    def _stop_pulse(self):
        if self._pulse_id:
            self.root.after_cancel(self._pulse_id)
            self._pulse_id = None

    # ============================================================
    # 地址
    # ============================================================
    def _on_addr_click(self, event):
        addr = self.addr_label.cget("text")
        if addr and addr != "—":
            webbrowser.open(addr)

    def _copy_addr(self):
        addr = self.addr_label.cget("text")
        if addr and addr != "—":
            self.root.clipboard_clear()
            self.root.clipboard_append(addr)
            self.log(f"已复制: {addr}", "ok")

    # ============================================================
    # 托盘
    # ============================================================
    def on_close(self):
        if self.hide_tray_var.get() and HAS_PYSTRAY:
            self.root.withdraw()
            self._create_tray()
        else:
            self._quit()

    def _create_tray(self):
        if self.tray_icon:
            return
        icon_img = self._make_icon(64)
        def show(icon, item): self.root.after(0, self._restore)
        def quit(icon, item): self.root.after(0, self._quit)
        menu = Menu(Item("显示窗口", show, default=True), Item("退出", quit))
        self.tray_icon = pystray.Icon("dsh_launcher", icon_img, APP_TITLE, menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def _quit(self):
        if self.is_running:
            self.stop_service()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.destroy()


def main():
    root = tk.Tk()
    app = DSHLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
