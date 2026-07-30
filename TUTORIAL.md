# 🎮 完整使用教程 - 天童爱丽丝桌面宠物

## ✅ 您的配置状态

**硬件**: i5-8400 + RTX 2060 + 32GB RAM  
**结论**: 🎉 **完美配置，可以流畅运行所有功能！**

---

## 📋 完整启动流程

### 步骤 1: 安装依赖 (只需一次)

```bash
cd /workspace
pip install PyQt5 websockets
```

### 步骤 2: 启动桌面宠物

打开**第一个命令行窗口**:

```bash
# 差分图模式（推荐，立即能用）
python desktop_pet.py --mode avatar
```

你会看到:
```
============================================================
🎭 天童爱丽丝 - 桌面宠物 (差分图模式)
============================================================
✅ 加载图片：avatar/plain.png
✅ 加载图片：avatar/happy.png
✅ 加载图片：avatar/angry.png
...
✅ 窗口已创建，位置：(100, 100)
✅ WebSocket 服务器：ws://127.0.0.1:8766

💡 提示:
   - 窗口将保持在桌面最上层
   - 支持鼠标穿透（点击穿透到桌面）
   - 按 Ctrl+C 退出程序

🚀 现在可以启动主程序：streamlit run webui.py
============================================================
```

此时桌面上会出现一个**透明悬浮窗**，显示爱丽丝的立绘！

### 步骤 3: 启动主程序

打开**第二个命令行窗口**:

```bash
streamlit run webui.py
```

浏览器会自动打开 `http://localhost:8501`

### 步骤 4: 配置并连接

1. 在 WebUI 中配置 B 站直播间号
2. 配置 LLM API 地址
3. 启动直播连接
4. 开始互动！

---

## 🎯 工作原理

```
┌─────────────┐    WebSocket    ┌──────────────┐
│  主程序     │ ──────────────→ │ 桌面宠物窗口 │
│  webui.py   │   ws:8766       │ desktop_pet  │
│             │                 │              │
│ 生成回复：   │                 │  显示立绘     │
│ 【表情：     │                 │  切换表情     │
│ happy】      │                 │  口型同步     │
│ 你好呀！     │                 │              │
└─────────────┘                 └──────────────┘
       ↓                               ↓
   处理弹幕                        显示在桌面
   调用 LLM                       透明悬浮窗
   提取表情                       始终置顶
```

---

## 🎨 表情系统

### 已有图片 (14 张)

| 文件名 | 表情名称 | 触发场景 |
|--------|---------|---------|
| plain.png | normal | 普通对话 |
| happy.png | happy | 开心、高兴 |
| smile.png | smile | 微笑、温和 |
| angry.png | angry | 生气、愤怒 |
| cry.png | sad | 伤心、哭泣 |
| thinking.png | surprised | 惊讶、思考 |
| shy.png | shy | 害羞、羞涩 |
| awkward.png | awkward | 尴尬、为难 |
| confident.png | confident | 自信、得意 |
| sweating.png | sweating | 冷汗、紧张 |
| touching.png | touching | 感动、触动 |
| awake.png | awake | 清醒、睡醒 |
| screwup.png | screwup | 失败、搞砸 |

### LLM 输出格式

在 System Prompt 中添加:

```
你是一个虚拟主播助手，回复时请在开头标注表情，格式：
【表情：表情名】你的回复内容

表情名可选：normal, happy, smile, angry, sad, surprised, 
shy, awkward, confident, sweating, touching, awake, screwup
```

示例输出:
```
【表情：happy】今天直播好开心呀！谢谢大家的支持！

【表情：shy】诶？突然被夸有点不好意思呢...

【表情：angry】不要发送奇怪的弹幕啦！
```

---

## ⚙️ 自定义配置

### 调整窗口位置

编辑 `config/avatar_config.json`:

```json
{
  "window": {
    "width": 500,      // 宽度
    "height": 700,     // 高度
    "x": 100,          // X 坐标（距左边）
    "y": 100           // Y 坐标（距顶部）
  }
}
```

### 添加新表情

1. 将图片放入 `avatar/` 目录
2. 编辑 `config/avatar_config.json`:

```json
{
  "images": {
    "new_expression": "my_image.png"
  }
}
```

3. 重启桌面宠物

---

## 🔧 故障排除

### 问题 1: 窗口不显示

**检查**:
```bash
pip list | grep PyQt5
```

**解决**:
```bash
pip install PyQt5
```

### 问题 2: 图片加载失败

**检查**:
```bash
ls avatar/*.png
```

**解决**: 确保图片存在且格式正确

### 问题 3: 表情不切换

**检查**: LLM 输出是否包含【表情：xxx】标记

**解决**: 在 System Prompt 中添加表情格式要求

### 问题 4: 窗口阻挡鼠标点击

**说明**: 这是正常设计（鼠标穿透），窗口不会阻挡操作

如需临时禁用，修改代码:
```python
# 删除这行
Qt.WindowTransparentForInput
```

---

## 🎓 Live2D 模式（进阶）

### 获取 Live2D 模型

1. **免费模型**:
   - [BOOTH](https://booth.pm/) - 搜索「Live2D 無料」
   - [Nizima](https://nizima.com/) - 部分免费模型
   
2. **付费定制**:
   - 淘宝/闲鱼搜索「Live2D 模型定制」
   - 价格：300-3000 元不等

### 集成步骤

1. 下载 `.model3.json` 文件
2. 放入 `assets/models/你的模型名/`
3. 编辑 `config/live2d_config.json`
4. 启动：`python desktop_pet.py --mode live2d`

> ⚠️ 当前版本为占位实现，需要集成 Cubism SDK 才能显示真实 Live2D

---

## 📊 性能监控

### 资源占用

| 模式 | CPU | 内存 | GPU |
|------|-----|------|-----|
| 差分图 | 2-5% | ~80MB | 0% |
| Live2D | 5-10% | ~250MB | 5-10% |

### 您的配置余量

- ✅ 可同时运行本地 LLM (7B 模型)
- ✅ 可同时运行语音识别
- ✅ 可同时运行 B 站连接
- ✅ 可流畅直播推流

---

## 🎬 演示效果

```
[桌面]
┌─────────────────────────────────────┐
│  浏览器 (Streamlit)                  │
│  ┌─────────────────────────────┐    │
│  │  天童爱丽丝控制面板          │    │
│  │  - 直播间：123456           │    │
│  │  - 状态：● 正在直播         │    │
│  │  - 弹幕：你好呀！           │    │
│  └─────────────────────────────┘    │
│                                     │
│         🎭 爱丽丝 (悬浮窗)           │
│         ┌───────────┐               │
│         │  爱丽丝    │ ← 透明背景    │
│         │  立绘     │ ← 自动切换    │
│         │  😊      │ ← 表情        │
│         └───────────┘               │
│                                     │
│  [其他桌面图标...]                   │
└─────────────────────────────────────┘
```

---

## 📞 需要帮助？

遇到以下问题请告诉我:
1. ❌ 依赖安装失败
2. ❌ 窗口显示异常
3. ❌ 表情不切换
4. ❌ 想添加新功能
5. ❌ Live2D 模型集成

---

**现在开始体验吧!**

```bash
# 终端 1
python desktop_pet.py --mode avatar

# 终端 2
streamlit run webui.py
```

🎉 让天童爱丽丝陪伴你的每一刻！
