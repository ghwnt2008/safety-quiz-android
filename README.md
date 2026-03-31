# 安全员C证题库 - 安卓版

## 📱 项目说明

这是将桌面版 `safety_quiz_app.py` 转换为安卓 APP 的项目。

## 🚀 快速开始

### 方法一：使用 Buildozer（推荐，Linux 环境）

**前置要求：需要 Linux 环境（Ubuntu 20.04+）**

1. 安装 Buildozer：
```bash
pip install buildozer
```

2. 在项目目录执行：
```bash
cd android_app
buildozer init  # 已完成
buildozer android debug
```

3. 生成的 APK 位于：`bin/safetyquiz-1.0.0-arm64-v8a-debug.apk`

### 方法二：使用 GitHub Actions 自动构建（无需 Linux）

1. 将此项目上传到 GitHub 仓库

2. 创建 `.github/workflows/build.yml`：
```yaml
name: Build Android APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          workdir: android_app
          command: buildozer android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: safety-quiz-apk
          path: android_app/bin/*.apk
```

3. 推送代码后，在 Actions 页面下载生成的 APK

### 方法三：使用在线构建服务

推荐使用：
- **Google Colab** + Buildozer
- **GitHub Codespaces**（Linux 环境）

## 📦 项目结构

```
android_app/
├── safety_quiz_mobile.py    # Kivy 移动端主程序
├── buildozer.spec           # Buildozer 配置文件
├── questions.json           # 题库数据（需从父目录复制）
├── progress.json            # 答题进度（运行时生成）
└── README.md                # 本说明文件
```

## ⚙️ 配置说明

### buildozer.spec 关键配置

- **title**: APP 名称（显示在手机上）
- **package.name**: 包名（唯一标识）
- **orientation**: portrait（竖屏）/ landscape（横屏）
- **android.permissions**: 存储权限（保存答题进度）
- **android.api**: 目标 Android API（31 = Android 12）
- **android.minapi**: 最低支持 API（21 = Android 5.0）

## 📋 使用前准备

**重要：需要将题库数据文件复制到项目目录**

```bash
# 复制题库文件
cp ../questions.json .
```

## 🎨 自定义 APP 图标

1. 准备一张 PNG 图片（建议 512x512 像素）

2. 保存为 `icon.png`

3. 在 `buildozer.spec` 中取消注释：
```
icon.filename = %(source.dir)s/icon.png
```

## 🔧 本地测试（无需打包）

在电脑上测试移动版界面：

```bash
pip install kivy
python safety_quiz_mobile.py
```

## 📱 安装到手机

### 调试版 APK
```bash
adb install bin/safetyquiz-1.0.0-arm64-v8a-debug.apk
```

### 发布版 APK
```bash
buildozer android release
```

发布版需要签名，详见：https://buildozer.readthedocs.io/

## 🐛 常见问题

### 1. 打包失败：缺少依赖
```bash
buildozer android debug --verbose
```
查看详细错误日志

### 2. APK 安装失败
- 确保手机开启了"允许安装未知来源应用"
- 检查 Android 版本是否 >= 5.0

### 3. APP 启动后无题库
- 确保 `questions.json` 在 APK 中
- 检查 `source.include_exts` 是否包含 `json`

### 4. 答题进度无法保存
- 检查是否授予了存储权限
- Android 11+ 需要特殊权限处理

## 📚 相关资源

- [Kivy 官方文档](https://kivy.org/doc/stable/)
- [Buildozer 文档](https://buildozer.readthedocs.io/)
- [Android 打包指南](https://kivy.org/doc/stable/guide/packaging-android.html)

## 🔄 与桌面版的差异

| 功能 | 桌面版 | 移动版 |
|------|--------|--------|
| 界面框架 | Tkinter | Kivy |
| 字体缩放 | 自动 | 固定 |
| 窗口大小 | 自适应 | 全屏 |
| 触控操作 | 鼠标点击 | 触摸点击 |
| 导航方式 | 快捷键 | 按钮 |

## 📝 开发日志

- **v1.0.0** - 初始版本
  - 基本答题功能
  - 题型切换
  - 错题记录
  - 答题进度保存
