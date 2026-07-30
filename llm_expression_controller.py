"""
LLM 输出控制器 - 解析表情标记并发送到桌面宠物
自动将 LLM 输出的【表情】标记转换为 WebSocket 指令
"""

import json
import asyncio
import websockets
from typing import Optional, Dict, Any


class ExpressionController:
    """表情控制器"""
    
    def __init__(self, websocket_host: str = "127.0.0.1", websocket_port: int = 8766):
        self.host = websocket_host
        self.port = websocket_port
        self.websocket = None
        self.connected = False
        
        # 表情映射表（中文关键词 -> 英文表情名）
        self.expression_map = {
            # 开心类
            "开心": "happy",
            "高兴": "happy",
            "笑": "smile",
            "微笑": "smile",
            "大笑": "happy",
            
            # 生气类
            "生气": "angry",
            "愤怒": "angry",
            "恼火": "angry",
            
            # 伤心类
            "伤心": "sad",
            "哭": "cry",
            "难过": "sad",
            "悲伤": "sad",
            
            # 惊讶类
            "惊讶": "surprised",
            "吃惊": "surprised",
            "震惊": "surprised",
            "思考": "thinking",
            
            # 害羞类
            "害羞": "shy",
            "羞涩": "shy",
            "不好意思": "shy",
            
            # 尴尬类
            "尴尬": "awkward",
            "为难": "awkward",
            "冷汗": "sweating",
            
            # 自信类
            "自信": "confident",
            "得意": "confident",
            
            # 感动类
            "感动": "touching",
            "触动": "touching",
            
            # 清醒类
            "清醒": "awake",
            "睡醒": "awake",
            
            # 失败类
            "失败": "screwup",
            "搞砸": "screwup",
            
            # 默认
            "普通": "normal",
            "平静": "normal",
        }
    
    async def connect(self):
        """连接到桌面宠物"""
        try:
            self.websocket = await websockets.connect(
                f"ws://{self.host}:{self.port}"
            )
            self.connected = True
            print(f"✅ 已连接到桌面宠物：ws://{self.host}:{self.port}")
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            self.connected = False
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
    
    def parse_expression(self, text: str) -> Optional[str]:
        """从文本中解析表情标记
        
        支持格式:
        - 【表情：happy】
        - 【表情=开心】
        - [表情：smile]
        """
        import re
        
        # 匹配【表情：xxx】或【表情=xxx】
        patterns = [
            r'【表情 [:：=]\s*(\w+)】',
            r'\[表情 [:：=]\s*(\w+)\]',
            r'<表情 [:：=]\s*(\w+)>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        # 如果没有显式标记，尝试从关键词推断
        for keyword, expression in self.expression_map.items():
            if keyword in text:
                return expression
        
        return None
    
    async def set_expression(self, expression: str):
        """设置表情"""
        if not self.connected:
            await self.connect()
        
        if self.connected:
            try:
                message = json.dumps({
                    "action": "set_expression",
                    "expression": expression
                })
                await self.websocket.send(message)
                print(f"🎭 表情已切换：{expression}")
            except Exception as e:
                print(f"❌ 发送失败：{e}")
                self.connected = False
    
    async def start_speaking(self):
        """开始说话"""
        if self.connected:
            message = json.dumps({"action": "start_speaking"})
            await self.websocket.send(message)
    
    async def stop_speaking(self):
        """停止说话"""
        if self.connected:
            message = json.dumps({"action": "stop_speaking"})
            await self.websocket.send(message)
    
    async def process_llm_output(self, text: str) -> str:
        """处理 LLM 输出，提取表情并发送指令
        
        Returns:
            清理后的文本（移除表情标记）
        """
        import re
        
        # 提取表情
        expression = self.parse_expression(text)
        
        if expression:
            # 标准化表情名
            if expression in self.expression_map.values():
                await self.set_expression(expression)
            elif expression in self.expression_map:
                standardized = self.expression_map[expression]
                await self.set_expression(standardized)
            else:
                # 尝试直接使用
                await self.set_expression(expression)
        
        # 清理文本中的表情标记
        cleaned_text = re.sub(r'【表情 [:：=]\s*\w+】', '', text)
        cleaned_text = re.sub(r'\[表情 [:：=]\s*\w+\]', '', cleaned_text)
        
        return cleaned_text.strip()


# 同步包装器（用于非异步代码）
class SyncExpressionController:
    """同步版本的控制器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8766):
        self.controller = ExpressionController(host, port)
        self.loop = asyncio.new_event_loop()
    
    def set_expression(self, expression: str):
        """设置表情（同步）"""
        asyncio.run_coroutine_threadsafe(
            self.controller.set_expression(expression),
            self.loop
        )
    
    def process_output(self, text: str) -> str:
        """处理输出（同步）"""
        future = asyncio.run_coroutine_threadsafe(
            self.controller.process_llm_output(text),
            self.loop
        )
        return future.result()
    
    def start(self):
        """启动异步循环"""
        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        import threading
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()


# 使用示例
if __name__ == "__main__":
    async def main():
        controller = ExpressionController()
        
        # 测试连接
        await controller.connect()
        
        # 测试表情切换
        test_texts = [
            "【表情：happy】今天天气真好呢！",
            "【表情=生气】不要这样做啦",
            "【表情：shy】人家会害羞的",
            "普通对话没有标记",
        ]
        
        for text in test_texts:
            print(f"\n原始：{text}")
            cleaned = await controller.process_llm_output(text)
            print(f"清理：{cleaned}")
            await asyncio.sleep(1)
        
        await controller.disconnect()
    
    asyncio.run(main())
