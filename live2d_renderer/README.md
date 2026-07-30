# Live2D 模型使用指南

## 快速开始

### 1. 获取 Live2D 模型

您可以从以下渠道获取 Live2D 模型：

- **官方资源**: [Live2D Cubism Sample Models](https://www.live2d.com/en/learn/sample/)
- **社区资源**: 
  - [Vroid Hub](https://hub.vroid.com/) (需转换为 Live2D)
  - [BOOTH](https://booth.pm/) (日本同人作品平台)
  - [Fantia](https://fantia.jp/) (部分创作者提供)
- **定制模型**: 联系画师或建模师定制专属模型

### 2. 模型文件结构

标准的 Live2D Cubism 4 模型应包含以下文件：

```
assets/models/arisis_model/
├── arisis.model3.json      # 模型主文件（必需）
├── arisis.moc3             # 模型数据（必需）
├── textures/               # 贴图文件夹
│   ├── texture_00.png
│   └── ...
├── motions/                # 动作文件
│   ├── idle_01.motion3.json
│   ├── tap_head_01.motion3.json
│   └── ...
└── expressions/            # 表情文件
    ├── normal.exp3.json
    ├── happy.exp3.json
    └── ...
```

### 3. 配置文件修改

编辑 `config/live2d_config.json`，更新模型路径和表情映射：

```json
{
  "model_name": "your_model_name",
  "model_path": "assets/models/your_model/",
  "expressions": {
    "normal": "normal.exp3.json",
    "happy": "happy.exp3.json",
    "angry": "angry.exp3.json"
  },
  "motions": {
    "idle": ["idle_01.motion3.json"],
    "speak": ["speak_01.motion3.json"]
  }
}
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

额外需要安装 PyQt5：
```bash
pip install PyQt5 websockets
```

### 5. 启动 Live2D 渲染器

```bash
python live2d_renderer/renderer.py
```

然后启动主程序：
```bash
streamlit run webui.py
```

## 差分图方案（替代方案）

如果您不想使用 Live2D，也可以使用静态差分图：

### 准备图片

在 `avatar/` 目录下准备以下 PNG 图片（支持透明背景）：

- `normal.png` - 普通表情
- `happy.png` - 开心
- `angry.png` - 生气
- `shy.png` - 害羞
- `thinking.png` - 思考
- `surprised.png` - 惊讶
- `cry.png` - 哭泣

### 图片规格建议

- 分辨率：800x1200 或更高
- 格式：PNG（支持透明通道）
- 背景：透明或纯色
- 命名：使用英文小写，避免特殊字符

## 常见问题

### Q: 模型不显示？
A: 检查模型路径是否正确，确保 `.model3.json` 文件存在。

### Q: 表情切换无效？
A: 确认表情文件名与配置文件一致，检查 LLM 输出是否包含正确的表情标记。

### Q: 窗口无法置顶？
A: Windows 系统可能需要管理员权限，或尝试重启渲染器。

### Q: 口型不同步？
A: 当前版本使用简单模拟，完整版需要集成语音识别时间戳。

## 进阶配置

### 自定义表情映射

编辑 `live2d_renderer/controller.py` 中的 `expression_map`：

```python
self.expression_map = {
    "normal": ["plain", "awake", "neutral"],
    "happy": ["happy", "smile", "laugh", "joy"],
    # 添加更多映射...
}
```

### 添加新动作

在配置文件中添加新动作：

```json
"motions": {
    "wave": ["wave_01.motion3.json"],
    "bow": ["bow_01.motion3.json"]
}
```

然后在代码中调用：
```python
await controller.play_motion("wave")
```

## 资源推荐

- [Live2D 官方文档](https://docs.live2d.com/)
- [Cubism SDK for Python](https://github.com/live2d/CubismSdkForPython)
- [PyQt5 教程](https://www.pythonguis.com/tutorials/pyqt6-creating-applications/)
- [VTuber 模型制作教程](https://www.bilibili.com/video/BV1xx411c7mD)
