# 🎮 天童爱丽丝 - 差分版 Neuro-sama

一个基于 PyQt5 的桌面宠物程序，拥有完整的 AI 对话、语音交互和表情切换功能。

## ✨ 特性

- **差分图显示**：支持 13 种表情自动切换
- **免费 AI**：集成 SiliconFlow API（Qwen2.5-7B/32B）
- **语音交互**：Edge-TTS 语音合成 + 本地 DDSP 音色转换
- **桌面挂件**：透明背景、鼠标穿透、系统托盘
- **完整人设**：天童爱丽丝角色设定

## 📁 项目结构

```
/workspace/
├── neuro_alice_core.py    # 主程序
├── config.json            # 配置文件
├── alice_prompt.txt       # 人设文件
├── start_alice.bat        # Windows 一键启动
├── avatar/                # 差分图目录（已有 13 张图片）
│   ├── plain.png
│   ├── happy.png
│   ├── smile.png
│   └── ...
├── assets/models/         # DDSP 模型目录
└── README_ALICE.md        # 本文件
```

## 🚀 快速开始

### 1. 准备资源

**差分图**：已存在于 `avatar/` 文件夹，包含：
- plain.png, happy.png, smile.png, angry.png, cry.png
- shy.png, thinking.png, confident.png, awkward.png
- sweating.png, touching.png, screwup.png, awake.png

**DDSP 模型**（可选）：
- 将 `.sf_pkg` 模型放入 `assets/models/`
- 修改 `config.json` 中的 `ddsp_model_path`

### 2. 获取 API Key

1. 访问 https://cloud.siliconflow.cn/
2. 注册账号并登录
3. 在"API Keys"页面创建新密钥
4. 复制密钥到 `config.json`

### 3. 配置参数

编辑 `config.json`：
```json
{
  "api_key": "sk-你的 API Key",
  "model_name": "Qwen/Qwen2.5-7B-Instruct",
  "ddsp_model_path": "assets/models/你的模型.sf_pkg",
  "avatar_folder": "avatar",
  "use_ddsp": true,
  "window_width": 400,
  "window_height": 600
}
```

### 4. 启动程序

**Windows**：双击 `start_alice.bat`

**Linux/Mac**：
```bash
python neuro_alice_core.py
```

程序会自动检测并安装缺失的依赖。

## 🎮 使用说明

### 基本操作
- **拖动**：左键点击并拖动窗口
- **菜单**：右键点击系统托盘图标
- **测试对话**：托盘菜单 → "对爱丽丝说话 (测试)"
- **鼠标穿透**：托盘菜单 → "切换鼠标穿透"
- **退出**：托盘菜单 → "退出"

### 表情系统

AI 回复时会自动识别表情标记：
- 格式：`【表情：happy】` 或 `[表情：smile]`
- 也支持关键词自动匹配（如"开心"→happy）

可用表情：
| 表情名 | 对应图片 | 触发词 |
|--------|---------|--------|
| normal | plain.png | 普通、平静 |
| happy | happy.png | 开心、高兴 |
| smile | smile.png | 微笑 |
| angry | angry.png | 生气 |
| cry | cry.png | 哭、伤心 |
| shy | shy.png | 害羞 |
| thinking | thinking.png | 思考 |
| confident | confident.png | 自信 |
| awkward | awkward.png | 尴尬 |
| sweating | sweating.png | 流汗 |
| touching | touching.png | 感动 |
| screwup | screwup.png | 搞砸 |
| awake | awake.png | 清醒 |

## 🔧 高级配置

### DDSP 音色转换

如果需要使用 DDSP 变声：
1. 确保 `assets/models/` 中有 `.sf_pkg` 模型
2. 设置 `config.json` 中 `"use_ddsp": true`
3. 安装 ddsp-svc 库（可选，用于本地推理）

注意：当前版本使用简化方案，如需完整 DDSP 推理功能，需要集成 ddsp-svc 库。

### 自定义人设

编辑 `alice_prompt.txt` 修改角色设定。

### 更换 AI 模型

在 `config.json` 中修改 `model_name`：
- `Qwen/Qwen2.5-7B-Instruct`（推荐，平衡）
- `Qwen/Qwen2.5-32B-Instruct`（更智能，需要更高配额）
- `THUDM/glm-edge-1.5b-chat`（快速）

## ❓ 常见问题

### Q: 提示"API Key 无效"
A: 检查 `config.json` 中的 API Key 是否正确复制，确保没有多余空格。

### Q: 图片不显示
A: 确认 `avatar/` 文件夹中有对应的 PNG 图片，且文件名正确。

### Q: 没有声音
A: 检查系统音量，确保扬声器正常工作。首次运行会自动下载 TTS 音频文件。

### Q: 依赖安装失败
A: 以管理员身份运行命令行，或手动安装：
```bash
pip install PyQt5 Pillow requests edge-tts sounddevice webrtcvad -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: DDSP 推理不工作
A: 当前版本为简化实现，需要集成 ddsp-svc 库才能实现真正的音色转换。

## 📝 更新日志

- ✅ 自动依赖安装
- ✅ 差分图表情系统（13 种表情）
- ✅ SiliconFlow 免费 AI 接入
- ✅ Edge-TTS 语音合成
- ✅ 桌面透明悬浮窗
- ✅ 系统托盘菜单
- ⏳ DDSP 本地推理（占位符）
- ⏳ 语音识别输入

## 🎯 下一步计划

1. 集成完整的 ddsp-svc 推理
2. 添加语音识别（Whisper/VAD）
3. 支持 B 站直播弹幕互动
4. 添加更多表情和动作

---

**享受与爱丽丝的互动吧！邦邦卡邦!!** 🎮✨
