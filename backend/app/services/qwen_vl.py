import base64
import httpx
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class QwenVLService:
    """Qwen-VL API服务"""
    
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY", "your-qwen-api-key-here")
        self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        prompt: str = "请分析这张图片的内容，用中文回答。"
    ) -> Dict[str, Any]:
        """分析图片内容"""
        try:
            # 将图片转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 构建请求数据
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-vl-plus",  # Qwen-VL图像分析模型
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {})
                }
            else:
                logger.error(f"Qwen-VL API错误: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Qwen-VL服务错误: {str(e)}")
            return {
                "success": False,
                "error": f"服务错误: {str(e)}"
            }
    
    async def chat_with_image(
        self, 
        image_data: bytes, 
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """与图片进行对话"""
        try:
            # 构建对话历史
            messages = []
            
            # 添加系统消息
            messages.append({
                "role": "system",
                "content": "你是一个专业的图像分析助手，能够准确分析图片内容并回答用户问题。请用中文回答，并使用Markdown格式来组织你的回答，包括标题、列表、强调等。"
            })
            
            # 添加对话历史
            if conversation_history:
                for msg in conversation_history[-5:]:  # 只保留最近5条消息
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前用户消息和图片
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
                        }
                    }
                ]
            })
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-vl-plus",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7,
                "stream": False
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {})
                }
            else:
                logger.error(f"Qwen-VL API错误: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Qwen-VL对话错误: {str(e)}")
            return {
                "success": False,
                "error": f"对话错误: {str(e)}"
            }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

# 创建全局服务实例
qwen_vl_service = QwenVLService()
