# 安全员C证题库 - Google Colab 构建脚本
# 复制此代码到 Google Colab 运行，自动构建安卓 APK

# ==================== 步骤 1：安装 Buildozer ====================
print("正在安装 Buildozer...")
!pip install buildozer
!pip install cython==0.29.33

# ==================== 步骤 2：创建项目文件 ====================
print("\n正在创建项目文件...")

import os
import json

# 创建项目目录
os.makedirs('/content/safety_quiz_app', exist_ok=True)
os.chdir('/content/safety_quiz_app')

# buildozer.spec 配置文件
buildozer_spec = '''[app]
title = 安全员C证题库
package.name = safetyquiz
package.domain = org.safety
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
'''

with open('buildozer.spec', 'w', encoding='utf-8') as f:
    f.write(buildozer_spec)

print("✓ buildozer.spec 已创建")

# ==================== 步骤 3：上传题库数据 ====================
print("\n请上传 questions.json 文件...")
from google.colab import files
uploaded = files.upload()

if 'questions.json' not in uploaded:
    print("⚠️ 警告：未检测到 questions.json，请手动上传")
else:
    print("✓ questions.json 已上传")

# ==================== 步骤 4：创建主程序 ====================
print("\n正在创建主程序...")

# 这里应该是完整的 safety_quiz_mobile.py 内容
# 由于代码较长，请从本地复制 safety_quiz_mobile.py 的内容
# 或者使用以下命令上传：

print("请上传 safety_quiz_mobile.py 文件...")
uploaded_code = files.upload()

if 'safety_quiz_mobile.py' not in uploaded_code:
    print("⚠️ 未检测到主程序文件")
    print("请从本地路径复制 safety_quiz_mobile.py 的内容")
else:
    print("✓ 主程序已上传")

# 创建 main.py
main_py = '''# -*- coding: utf-8 -*-
from safety_quiz_mobile import SafetyQuizApp
if __name__ == '__main__':
    SafetyQuizApp().run()
'''
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_py)

print("✓ main.py 已创建")

# ==================== 步骤 5：构建 APK ====================
print("\n开始构建 APK（此过程约需 15-20 分钟）...")
print("首次构建会下载 Android SDK/NDK，请耐心等待...\n")

!buildozer android debug

# ==================== 步骤 6：下载 APK ====================
print("\n构建完成！正在查找 APK 文件...")

import glob
apk_files = glob.glob('bin/*.apk')

if apk_files:
    print(f"\n✓ 找到 APK 文件：{len(apk_files)} 个")
    for apk in apk_files:
        print(f"  - {apk}")
    
    print("\n正在准备下载...")
    files.download(apk_files[0])
else:
    print("\n⚠️ 未找到 APK 文件，请检查构建日志")
    print("可能的错误原因：")
    print("  1. 缺少 questions.json")
    print("  2. safety_quiz_mobile.py 语法错误")
    print("  3. 网络问题导致依赖下载失败")

# ==================== 完成提示 ====================
print("\n" + "="*50)
print("构建流程完成！")
print("="*50)
print("\n如果构建成功，APK 文件会自动下载")
print("如果构建失败，请查看上方的错误日志")
print("\n常见问题：")
print("  - 缺少文件：确保上传了 questions.json 和 safety_quiz_mobile.py")
print("  - 依赖错误：尝试重新运行此脚本")
print("  - 权限问题：忽略，不影响 APK 功能")
