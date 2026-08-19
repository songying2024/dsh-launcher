# -*- coding: utf-8 -*-
"""PyInstaller 打包脚本 — 修复 tkinter DLL 问题"""
import PyInstaller.__main__ as pyi
import os
import sys
import shutil

PY_BASE = os.path.dirname(sys.executable)
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 收集所有需要额外包含的二进制文件
binaries = []

# 1. _tkinter.pyd
tkinter_pyd = os.path.join(PY_BASE, "DLLs", "_tkinter.pyd")
if os.path.exists(tkinter_pyd):
    binaries.append(f"--add-binary={tkinter_pyd};.")

# 2. tcl86t.dll, tk86t.dll
for dll in ["tcl86t.dll", "tk86t.dll"]:
    path = os.path.join(PY_BASE, "Library", "bin", dll)
    if os.path.exists(path):
        binaries.append(f"--add-binary={path};.")

# 3. tcl/tk 运行时库目录
for libdir in ["tcl8.6", "tk8.6"]:
    src = os.path.join(PY_BASE, "Library", "lib", libdir)
    if os.path.exists(src):
        binaries.append(f"--add-data={src};{libdir}")

# 4. pystray
import pystray
pystray_dir = os.path.dirname(pystray.__file__)
binaries.append(f"--add-data={pystray_dir};pystray")

args = [
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "DeepSeekHarness启动器",
    "--icon", os.path.join(APP_DIR, "app_icon.ico"),
    *binaries,
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.ttk",
    "--hidden-import=tkinter.font",
    "--hidden-import=tkinter.messagebox",
    "--hidden-import=pystray",
    "--collect-all", "PIL",
    "--add-data", os.path.join(APP_DIR, "app_icon.png") + ";.",
    os.path.join(APP_DIR, "dsh_launcher.py"),
]

print("=== PyInstaller 打包参数 ===")
for a in args:
    print(f"  {a}")
print()

pyi.run(args)
print("\n打包完成！")
