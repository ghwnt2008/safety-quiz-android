# 安全员C证题库 - 快速打包指南

## 🎯 最简单的方法：GitHub Actions 自动构建

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库，例如：`safety-quiz-android`
3. 不要初始化 README（我们已有文件）

### 步骤 2：上传代码

在 `android_app` 目录执行：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "初始提交：安全员C证题库安卓版"

# 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/safety-quiz-android.git

# 推送
git branch -M main
git push -u origin main
```

### 步骤 3：下载 APK

1. 推送后，GitHub Actions 会自动开始构建
2. 访问仓库的 **Actions** 标签页
3. 等待构建完成（约 10-20 分钟）
4. 点击构建记录，在 **Artifacts** 中下载 `safety-quiz-apk.zip`
5. 解压得到 APK 文件

### 步骤 4：安装到手机

1. 将 APK 传输到手机
2. 点击安装（可能需要开启"允许安装未知来源应用"）

---

## 🚀 备用方法：Google Colab 在线构建

如果 GitHub Actions 失败，可以使用 Google Colab：

1. 访问 https://colab.research.google.com/
2. 创建新笔记本
3. 运行以下代码：

```python
# 安装依赖
!pip install buildozer

# 克隆你的仓库（或上传文件）
!git clone https://github.com/你的用户名/safety-quiz-android.git
%cd safety-quiz-android/android_app

# 构建 APK（约 15 分钟）
!buildozer android debug

# 下载 APK
from google.colab import files
files.download('bin/safetyquiz-1.0.0-arm64-v8a-debug.apk')
```

---

## 📦 所有生成的文件

```
android_app/
├── safety_quiz_mobile.py      # 移动端主程序（Kivy）
├── main.py                    # 入口文件
├── buildozer.spec             # 打包配置
├── questions.json             # 题库数据
├── README.md                  # 项目说明
├── BUILD.md                   # 本文件
└── .github/
    └── workflows/
        └── build.yml          # 自动构建配置
```

---

## ✅ 检查清单

打包前确保：

- [ ] `questions.json` 已复制到 `android_app` 目录
- [ ] `buildozer.spec` 中的包名已修改（可选）
- [ ] 已添加 APP 图标（可选）
- [ ] 在电脑上测试过：`python safety_quiz_mobile.py`

---

## 🔗 相关链接

- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [Buildozer 官方文档](https://buildozer.readthedocs.io/)
- [Kivy 打包指南](https://kivy.org/doc/stable/guide/packaging-android.html)

---

**如有问题，请查看 Actions 构建日志，或使用 Google Colab 方式构建。**
