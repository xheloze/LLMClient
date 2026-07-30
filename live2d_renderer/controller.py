"""
Live2D 控制器 - 连接 LLM 输出与 Live2D 渲染器
解析 LLM 返回的表情标记并控制模型表现
"""

import json
import re
import asyncio
import websockets
from typing import Optional


class Live2DController:
    """Live2D 控制器，负责将 LLM 输出转换为渲染指令"""
    
    def __init__(self, websocket_url: str = "ws://127.0.0.1:8765"):
        self.websocket_url = websocket_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.current_expression = "normal"
        
        # 表情映射表（可根据实际模型调整）
        self.expression_map = {
            "normal": ["plain", "awake"],
            "happy": ["happy", "smile", "confident"],
            "angry": ["angry", "screwup"],
            "shy": ["shy", "awkward", "sweating"],
            "thinking": ["thinking"],
            "surprised": ["touching"],
            "cry": ["cry"],
            "sad": ["cry", "awkward"]
        }
    
    async def connect(self):
        """连接到 Live2D 渲染器"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            print(f"已连接到 Live2D 渲染器：{self.websocket_url}")
            return True
        except Exception as e:
            print(f"连接 Live2D 渲染器失败：{e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            print("已断开 Live2D 连接")
    
    def parse_expression_from_text(self, text: str) -> str:
        """从文本中解析表情标记
        
        支持的格式：
        - 【happy】
        - [angry]
        - (shy)
        """
        patterns = [
            r'【([^】]+)】',
            r'\[([^\]]+)\]',
            r'\(([^)]+)\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                emotion = match.group(1).strip().lower()
                return self._map_emotion(emotion)
        
        return "normal"
    
    def _map_emotion(self, emotion: str) -> str:
        """将情绪关键词映射到具体表情"""
        emotion = emotion.lower()
        
        # 直接匹配
        for standard_expr, keywords in self.expression_map.items():
            if emotion in keywords or emotion == standard_expr:
                return standard_expr
        
        # 模糊匹配
        if any(word in emotion for word in ["开心", "高兴", "笑", "happy", "smile"]):
            return "happy"
        elif any(word in emotion for word in ["生气", "怒", "angry", "mad"]):
            return "angry"
        elif any(word in emotion for word in ["害羞", "尴尬", "shy", "awkward"]):
            return "shy"
        elif any(word in emotion for word in ["思考", "想", "think"]):
            return "thinking"
        elif any(word in emotion for word in ["哭", "sad", "cry"]):
            return "cry"
        elif any(word in emotion for word in ["惊讶", "惊", "surprise"]):
            return "surprised"
        
        return "normal"
    
    async def set_expression(self, expression: str):
        """设置表情"""
        if not self.websocket:
            print("未连接到 Live2D 渲染器")
            return
        
        message = json.dumps({
            "action": "set_expression",
            "expression": expression
        })
        
        try:
            await self.websocket.send(message)
            self.current_expression = expression
            print(f"表情已切换：{expression}")
        except Exception as e:
            print(f"发送表情指令失败：{e}")
    
    async def start_speaking(self):
        """开始说话动画"""
        if not self.websocket:
            return
        
        message = json.dumps({"action": "start_speaking"})
        try:
            await self.websocket.send(message)
        except Exception as e:
            print(f"发送说话指令失败：{e}")
    
    async def stop_speaking(self):
        """停止说话动画"""
        if not self.websocket:
            return
        
        message = json.dumps({"action": "stop_speaking"})
        try:
            await self.websocket.send(message)
        except Exception as e:
            print(f"发送停止说话指令失败：{e}")
    
    async def play_motion(self, motion: str):
        """播放动作"""
        if not self.websocket:
            return
        
        message = json.dumps({
            "action": "play_motion",
            "motion": motion
        })
        
        try:
            await self.websocket.send(message)
        except Exception as e:
            print(f"发送动作指令失败：{e}")
    
    async def handle_llm_response(self, response_text: str):
        """处理 LLM 响应，自动提取表情并更新
        
        Args:
            response_text: LLM 返回的完整文本
        """
        # 解析表情
        expression = self.parse_expression_from_text(response_text)
        
        # 如果表情变化则更新
        if expression != self.current_expression:
            await self.set_expression(expression)
        
        # 启动说话动画
        await self.start_speaking()
        
        # 模拟说话时长（实际应该根据语音长度）
        await asyncio.sleep(len(response_text) * 0.1)
        
        # 停止说话动画
        await self.stop_speaking()


async def demo():
    """演示用法"""
    controller = Live2DController()
    
    if await controller.connect():
        # 测试表情切换
        test_texts = [
            "【happy】老师好呀！今天也要一起玩游戏哦~",
            "【thinking】嗯...让爱丽丝想想...",
            "【angry】老师又在摸鱼了！",
            "【shy】这、这样不太好吧...",
        ]
        
        for text in test_texts:
            print(f"\n处理文本：{text}")
            await controller.handle_llm_response(text)
            await asyncio.sleep(1)
        
        await controller.disconnect()


if __name__ == "__main__":
    asyncio.run(demo())
