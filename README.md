# DeepSeek Harness 一键启动器

> 基于 [DeepSeek Harness](https://www.deepseek.com/harness/) 官网开发的 Windows 桌面一键启动器，让 DeepSeek Agent 的启动、配置和插件管理变得简单。

## 功能特性

### 常规标签页

- **一键启动/停止** — 启动 `npx @deepseek-ai/dsh web --port 3080`，无需命令行操作
- **端口配置** — 自定义端口号，默认 3080
- **自动打开浏览器** — 服务就绪后自动打开访问页面（端口轮询确认，避免连接拒绝）
- **系统托盘常驻** — 关闭窗口后最小化到托盘，右键菜单可显示/退出
- **实时运行日志** — 深色终端风格，彩色分级显示（信息/成功/错误）
- **配置持久化** — 端口和选项自动保存

### 插件标签页

- **分类浏览** — 按主题外观、记忆增强、界面优化、工具增强、安全认证、中文增强、模型接入分类
- **已安装管理** — 独立"已安装"分类，集中管理所有已装插件
- **一键安装/卸载** — 调用 `dsh plugin --profile web add/remove` 命令，支持多插件同时安装
- **动态刷新** — 从 npm 搜索最新插件并自动归类
- **搜索过滤** — 按名称和描述实时搜索
- **自动检测** — 启动时自动扫描已安装插件，支持 pnpm 自动安装

## 截图

### 常规标签页

- 深色顶栏 + 蓝紫主色调
- 状态脉冲动画指示灯
- 自定义 ToggleSwitch 开关组件
- 深色终端风格日志区

### 插件标签页

- 左侧分类导航栏
- 右侧插件卡片列表（可滚动）
- 每个卡片显示：插件名、分类标签、安装状态、描述、操作按钮
- 顶部搜索框 + 刷新按钮 + 已安装计数

## 快速开始

### 方式一：直接运行 exe（推荐）

1. 下载 `DeepSeekHarness启动器.exe`
2. 双击运行，无需 Python 环境
3. 点击「一键启动」即可

### 方式二：源码运行

```bash
# 克隆仓库
git clone https://github.com/songying2024/dsh-launcher.git
cd dsh-launcher

# 安装依赖
pip install pillow pystray

# 运行
python dsh_launcher.py
```

## 环境要求

- **操作系统**：Windows 10/11
- **Node.js**：>= 18（提供 npx 命令）[下载地址](https://nodejs.org/)
- **pnpm**：自动检测并安装（如缺失会自动执行 `npm install -g pnpm`）

## 从源码构建 exe

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建独立 exe
python build_exe.py
```

生成的 exe 在 `dist/` 目录下。

## 项目结构

```
dsh-launcher/
├── dsh_launcher.py        # 主程序源码
├── build_exe.py           # PyInstaller 打包脚本
├── app_icon.ico           # 应用图标（ICO 格式，多尺寸）
├── app_icon.png           # 应用图标（PNG 格式）
├── 一键启动.bat            # 批处理启动文件
├── 一键启动.vbs            # 无控制台窗口启动脚本
├── README.md              # 项目说明
├── LICENSE                # MIT 许可证
├── CHANGELOG.md           # 更新日志
└── .gitignore             # Git 忽略规则
```

## 技术栈

| 组件 | 技术 |
|------|------|
| GUI 框架 | tkinter + PIL |
| 系统托盘 | pystray |
| 图标处理 | Pillow (ICO 多尺寸) |
| 打包工具 | PyInstaller |
| 核心命令 | npx @deepseek-ai/dsh web |
| 插件管理 | npx @deepseek-ai/dsh plugin --profile web |

## 插件分类说明

| 分类 | 说明 | 示例插件 |
|------|------|---------|
| 主题外观 | 主题、皮肤、配色 | dsh-catppuccin, dsh-dracula-theme |
| 记忆增强 | 跨会话记忆、上下文管理 | dsh-mnemon, dsh-layered-memory |
| 界面优化 | UI 增强、工作流 | dshmarket, deepseek-flow |
| 工具增强 | 视觉、搜索、补丁 | dsh-vision-router, dsh-find-plugin |
| 安全认证 | 认证、访问控制 | deepseek-harness-auth |
| 中文增强 | 中文本地化 | deepseek-harness-zh_pro |
| 模型接入 | 模型集成 | @memtensor/memos-local-plugin |

## 版本历史

- **v3.0** — 标签页系统 + 插件管理（分类浏览/安装/卸载/搜索/动态刷新）
- **v2.0** — UI 美化（深色顶栏、脉冲动画、ToggleSwitch、深色日志）
- **v1.0** — 基础功能（启动/停止/端口/托盘/日志）

## 致谢

- [DeepSeek Harness](https://www.deepseek.com/harness/) — DeepSeek 开源 Agent 运行时框架
- 所有 DSH 社区插件作者

## License

[MIT](LICENSE)
