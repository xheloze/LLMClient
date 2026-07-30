# 天童爱丽丝 - 差分版 Neuro-sama

一个基于 PyQt5 的桌面宠物程序，具有完整的语音交互、LLM 对话和 DDSP 变声功能。

## ✨ 特性

- 🎭 **差分图表情系统**：支持 14+ 种表情自动切换
- 🗣️ **语音交互**：语音识别 (STT) + 语音合成 (TTS)
- 🤖 **免费高智商 AI**：集成 SiliconFlow 免费 API (Qwen2.5-7B/32B)
- 🎵 **DDSP 变声**：支持本地 .sf_pkg 模型推理（可选）
- 🖥️ **桌面挂件**：透明背景、鼠标穿透、系统托盘
- 📝 **完整人设**：内置天童爱丽丝详细 Prompt

## 🚀 快速开始

### 1. 准备资源

```bash
# 创建文件夹
mkdir assets/models
mkdir assets/avatar
```

**差分图**：将图片放入 `assets/avatar/`，命名示例：
- plain.png (普通)
- happy.png (开心)
- smile.png (微笑)
- angry.png (生气)
- sad.png (伤心)
- shy.png (害羞)
- ...

**DDSP 模型**：将 `.sf_pkg` 文件放入 `assets/models/`

### 2. 配置 API Key

编辑 `config_alice.json`：
```json
{
  "ai": {
    "api_key": "你的 SiliconFlow API Key"
  }
}
```

获取免费 API Key：https://cloud.siliconflow.cn/

### 3. 一键启动

**Windows**: 双击 `start_alice.bat`

**手动启动**:
```bash
# 安装依赖
python install_deps.py

# 运行程序
python neuro_alice_core.py
```

## 📁 项目结构

```
/workspace/
├── start_alice.bat          # 一键启动脚本
├── install_deps.py          # 智能依赖安装器
├── neuro_alice_core.py      # 主程序
├── config_alice.json        # 配置文件
├── alice_prompt.txt         # 人设 Prompt
├── assets/
│   ├── models/              # DDSP 模型 (.sf_pkg)
│   └── avatar/              # 差分图 (PNG)
└── README_ALICE.md          # 本文件
```

## 🎮 使用说明

### 操作方式
- **拖拽**：左键拖动调整位置
- **右键菜单**：
  - 对爱丽丝说话（语音输入）
  - 切换鼠标穿透
  - 退出程序

### 表情触发
LLM 回复中自动解析表情标记：
- `【表情：happy】` → 切换到 happy.png
- `[表情：开心]` → 切换到 happy.png

### DDSP 变声
在 `config_alice.json` 中启用：
```json
{
  "voice": {
    "ddsp_enabled": true,
    "ddsp_model_path": "assets/models/your_model.sf_pkg"
  }
}
```

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| ai.api_key | SiliconFlow API Key | 必填 |
| ai.model | LLM 模型名称 | Qwen/Qwen2.5-7B-Instruct |
| avatar.images_path | 差分图文件夹 | assets/avatar |
| avatar.window_width | 窗口宽度 | 400 |
| avatar.window_height | 窗口高度 | 600 |
| voice.ddsp_enabled | 启用 DDSP | false |
| voice.edge_voice | Edge-TTS 音色 | zh-CN-XiaoxiaoNeural |
| bilibili.room_id | B 站直播间 ID | 空 |

## 🔧 故障排除

### 依赖安装失败
```bash
# 手动安装核心依赖
pip install PyQt5 Pillow requests edge-tts playsound SpeechRecognition
```

### DDSP 无法使用
程序会自动降级为 Edge-TTS，不影响基本功能。

### 语音识别不工作
- 检查麦克风权限
- 确保网络连接正常（使用 Google 识别）

### 图片不显示
- 检查图片路径是否正确
- 确保图片格式为 PNG/JPG
- 查看控制台错误信息

## 📊 性能要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 6 核+ |
| 内存 | 8GB | 16GB+ |
| GPU | 无要求 | RTX 2060+ (DDSP) |
| 存储 | 1GB | 5GB+ |

您的配置 (i5-8400 + RTX 2060 + 32GB) **完美适用**！

## 🌟 进阶功能

### 自定义 Prompt
编辑 `alice_prompt.txt` 修改人设。

### 添加新表情
1. 将图片放入 `assets/avatar/`
2. 在 `neuro_alice_core.py` 的 `ExpressionMapper` 中添加映射

### 集成 B 站直播
在配置文件中设置 `bilibili.room_id`，未来版本将支持自动回复弹幕。

## 📝 许可证

本项目基于 Momotalk 项目改造，遵循原项目许可证。

## 🙏 致谢

- [SiliconFlow](https://siliconflow.cn/) - 免费 LLM API
- [Edge-TTS](https://github.com/rany2/edge-tts) - 微软语音合成
- [DDSP-SVC](https://github.com/yxlllc/ddsp-svc) - 音色转换
- [Blue Archive](https://bluearchive.jp/) - 天童爱丽丝角色

---

**邦邦卡邦!! 爱丽丝准备好和你一起冒险了！** 🎮✨
