from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.chat_session import ChatSession
from ..models.message import Message, MessageType
from ..schemas.chat import ChatRequest, ChatResponse, ChatSessionResponse
from ..services.qwen_vl import qwen_vl_service
import uuid
from datetime import datetime
import httpx
import os
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """与AI进行对话"""
    try:
        # 获取或创建会话
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")
        else:
            # 创建新会话
            session = ChatSession(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # 添加用户消息
        user_message = Message(
            id=str(uuid.uuid4()),
            chat_session_id=session.id,
            content=request.message,
            type=MessageType.user,
            image_url=request.image_url
        )
        db.add(user_message)
        db.commit()  # 立即提交用户消息
        
        # 调用AI服务
        if request.image_url:
            # 处理图片URL - 下载并分析图片
            try:
                # 配置HTTP客户端，禁用SSL验证以避免证书问题
                async with httpx.AsyncClient(
                    timeout=30.0,
                    verify=False,  # 禁用SSL验证
                    follow_redirects=True
                ) as client:
                    # 下载图片
                    logger.info(f"正在下载图片: {request.image_url}")
                    image_response = await client.get(request.image_url)
                    
                    if image_response.status_code == 200:
                        image_data = image_response.content
                        logger.info(f"图片下载成功，大小: {len(image_data)} bytes")
                        
                        # 调用Qwen-VL进行图片分析
                        result = await qwen_vl_service.analyze_image(
                            image_data=image_data,
                            prompt=request.message or "请分析这张图片的内容，用中文详细描述你看到了什么。"
                        )
                        
                        if result["success"]:
                            ai_response = result["content"]
                        else:
                            ai_response = f"图片分析失败：{result['error']}"
                    else:
                        ai_response = f"无法下载图片，状态码：{image_response.status_code}"
                        
            except httpx.ConnectError as e:
                ai_response = f"网络连接失败，无法下载图片：{str(e)}"
                logger.error(f"网络连接错误: {str(e)}")
            except httpx.TimeoutException as e:
                ai_response = f"下载图片超时：{str(e)}"
                logger.error(f"超时错误: {str(e)}")
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"图片处理错误详情: {error_details}")
                ai_response = f"图片处理出错：{str(e)}"
        else:
            # 调用Qwen-VL进行文本对话
            try:
                # 构建对话历史
                conversation_history = []
                recent_messages = db.query(Message).filter(
                    Message.chat_session_id == session.id
                ).order_by(Message.timestamp.desc()).limit(10).all()
                
                for msg in reversed(recent_messages):
                    role = "user" if msg.type == MessageType.user else "assistant"
                    conversation_history.append({
                        "role": role,
                        "content": msg.content
                    })
                
                # 调用Qwen API进行文本对话
                headers = {
                    "Authorization": f"Bearer {os.getenv('QWEN_API_KEY')}",
                    "Content-Type": "application/json"
                }
                
                messages = [
                    {"role": "system", "content": "你是一个有帮助的AI助手，请用中文回答用户的问题，并使用Markdown格式来组织你的回答，包括标题、列表、强调等。"}
                ]
                
                # 添加对话历史
                messages.extend(conversation_history[-5:])  # 只保留最近5条消息
                
                # 添加当前用户消息
                messages.append({"role": "user", "content": request.message})
                
                data = {
                    "model": "qwen-plus",  # 使用文本模型
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')}/chat/completions",
                        headers=headers,
                        json=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                    else:
                        ai_response = f"抱歉，AI服务暂时不可用。错误代码：{response.status_code}"
                        
            except Exception as e:
                ai_response = f"AI服务调用失败：{str(e)}"
        
        # 添加AI回复
        ai_message = Message(
            id=str(uuid.uuid4()),
            chat_session_id=session.id,
            content=ai_response,
            type=MessageType.bot
        )
        db.add(ai_message)
        
        # 更新会话时间
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return ChatResponse(
            message=ai_response,
            session_id=session.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")

@router.post("/chat/stream")
async def chat_with_ai_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """与AI进行流式对话"""
    
    async def generate_stream():
        try:
            # 获取或创建会话
            if request.session_id:
                session = db.query(ChatSession).filter(
                    ChatSession.id == request.session_id,
                    ChatSession.user_id == current_user.id
                ).first()
                if not session:
                    yield f"data: {json.dumps({'error': '会话不存在'})}\n\n"
                    return
            else:
                # 创建新会话
                session = ChatSession(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    title=request.message[:50] + "..." if len(request.message) > 50 else request.message
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            
            # 发送会话ID
            yield f"data: {json.dumps({'session_id': session.id})}\n\n"
            
            # 添加用户消息
            user_message = Message(
                id=str(uuid.uuid4()),
                chat_session_id=session.id,
                content=request.message,
                type=MessageType.user,
                image_url=request.image_url
            )
            db.add(user_message)
            db.commit()
            
            # 调用AI服务
            if request.image_url:
                # 处理图片URL - 下载并分析图片
                try:
                    async with httpx.AsyncClient(
                        timeout=30.0,
                        verify=False,
                        follow_redirects=True
                    ) as client:
                        logger.info(f"正在下载图片: {request.image_url}")
                        image_response = await client.get(request.image_url)
                        
                        if image_response.status_code == 200:
                            image_data = image_response.content
                            logger.info(f"图片下载成功，大小: {len(image_data)} bytes")
                            
                            # 将图片转换为base64
                            import base64
                            import mimetypes
                            from PIL import Image
                            import io
                            
                            # 检查图片大小，如果太大则压缩
                            image_size_mb = len(image_data) / (1024 * 1024)
                            print(f"原始图片大小: {image_size_mb:.2f} MB")
                            
                            if image_size_mb > 5:  # 如果大于5MB，进行压缩
                                try:
                                    # 使用PIL压缩图片
                                    image = Image.open(io.BytesIO(image_data))
                                    
                                    # 计算新的尺寸，保持宽高比
                                    max_size = 1920  # 最大尺寸
                                    if image.width > max_size or image.height > max_size:
                                        ratio = min(max_size / image.width, max_size / image.height)
                                        new_width = int(image.width * ratio)
                                        new_height = int(image.height * ratio)
                                        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                    
                                    # 转换为JPEG格式并压缩
                                    output = io.BytesIO()
                                    image.save(output, format='JPEG', quality=85, optimize=True)
                                    image_data = output.getvalue()
                                    output.close()
                                    
                                    compressed_size_mb = len(image_data) / (1024 * 1024)
                                    print(f"压缩后图片大小: {compressed_size_mb:.2f} MB")
                                    
                                    # 更新MIME类型为JPEG
                                    mime_type = 'image/jpeg'
                                except Exception as e:
                                    print(f"图片压缩失败: {str(e)}")
                                    # 如果压缩失败，继续使用原始图片
                            
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            
                            # 根据图片URL或内容检测MIME类型
                            if request.image_url:
                                # 从URL中检测文件扩展名
                                if request.image_url.lower().endswith('.png'):
                                    mime_type = 'image/png'
                                elif request.image_url.lower().endswith('.jpg') or request.image_url.lower().endswith('.jpeg'):
                                    mime_type = 'image/jpeg'
                                elif request.image_url.lower().endswith('.gif'):
                                    mime_type = 'image/gif'
                                elif request.image_url.lower().endswith('.webp'):
                                    mime_type = 'image/webp'
                                else:
                                    # 默认使用jpeg
                                    mime_type = 'image/jpeg'
                            else:
                                mime_type = 'image/jpeg'
                            
                            print(f"=== 图片处理调试信息 ===")
                            print(f"图片URL: {request.image_url}")
                            print(f"检测到的MIME类型: {mime_type}")
                            print(f"图片大小: {len(image_data)} bytes")
                            print(f"Base64长度: {len(image_base64)}")
                            logger.info(f"图片URL: {request.image_url}")
                            logger.info(f"检测到的MIME类型: {mime_type}")
                            logger.info(f"图片大小: {len(image_data)} bytes")
                            
                            # 构建带图片的流式请求
                            headers = {
                                "Authorization": f"Bearer {os.getenv('QWEN_API_KEY')}",
                                "Content-Type": "application/json"
                            }
                            
                            messages = [
                                {
                                    "role": "system",
                                    "content": "你是一个专业的图像分析助手，能够准确分析图片内容并回答用户问题。请用中文回答，并使用Markdown格式来组织你的回答，包括标题、列表、强调等。"
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": request.message or "请分析这张图片的内容，用中文详细描述你看到了什么。"
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{mime_type};base64,{image_base64}"
                                            }
                                        }
                                    ]
                                }
                            ]
                            
                            data = {
                                "model": "qwen-vl-plus",
                                "messages": messages,
                                "max_tokens": 1500,
                                "temperature": 0.7,
                                "stream": True  # 启用流式输出
                            }
                            
                            async with httpx.AsyncClient(timeout=60.0) as client:
                                async with client.stream(
                                    "POST",
                                    f"{os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')}/chat/completions",
                                    headers=headers,
                                    json=data
                                ) as response:
                                    if response.status_code == 200:
                                        ai_response = ""
                                        async for line in response.aiter_lines():
                                            if line.startswith("data: "):
                                                data_str = line[6:]  # 移除 "data: " 前缀
                                                if data_str.strip() == "[DONE]":
                                                    break
                                                try:
                                                    chunk = json.loads(data_str)
                                                    if "choices" in chunk and len(chunk["choices"]) > 0:
                                                        delta = chunk["choices"][0].get("delta", {})
                                                        if "content" in delta:
                                                            content = delta["content"]
                                                            ai_response += content
                                                            yield f"data: {json.dumps({'content': content, 'type': 'chunk'})}\n\n"
                                                except json.JSONDecodeError:
                                                    continue
                                    else:
                                        # 获取详细的错误信息
                                        try:
                                            # 对于流式响应，我们需要先检查状态码
                                            print(f"=== Qwen API错误详情 ===")
                                            print(f"状态码: {response.status_code}")
                                            print(f"响应头: {dict(response.headers)}")
                                            
                                            # 尝试读取响应内容
                                            if response.status_code != 200:
                                                try:
                                                    error_text = await response.text()
                                                    print(f"错误响应: {error_text}")
                                                    logger.error(f"Qwen API错误详情: {error_text}")
                                                    ai_response = f"图片分析失败，错误代码：{response.status_code}，详情：{error_text}"
                                                except Exception as read_error:
                                                    print(f"读取错误响应失败: {str(read_error)}")
                                                    ai_response = f"图片分析失败，错误代码：{response.status_code}，无法读取详细错误信息"
                                            else:
                                                ai_response = f"图片分析失败，错误代码：{response.status_code}"
                                        except Exception as e:
                                            print(f"=== 获取错误信息失败 ===")
                                            print(f"异常: {str(e)}")
                                            ai_response = f"图片分析失败，错误代码：{response.status_code}"
                                        yield f"data: {json.dumps({'content': ai_response, 'type': 'error'})}\n\n"
                        else:
                            ai_response = f"无法下载图片，状态码：{image_response.status_code}"
                            yield f"data: {json.dumps({'content': ai_response, 'type': 'error'})}\n\n"
                            
                except Exception as e:
                    ai_response = f"图片处理出错：{str(e)}"
                    yield f"data: {json.dumps({'content': ai_response, 'type': 'error'})}\n\n"
            else:
                # 调用Qwen-VL进行文本对话
                try:
                    # 构建对话历史
                    conversation_history = []
                    recent_messages = db.query(Message).filter(
                        Message.chat_session_id == session.id
                    ).order_by(Message.timestamp.desc()).limit(10).all()
                    
                    for msg in reversed(recent_messages):
                        role = "user" if msg.type == MessageType.user else "assistant"
                        conversation_history.append({
                            "role": role,
                            "content": msg.content
                        })
                    
                    # 调用Qwen API进行文本对话
                    headers = {
                        "Authorization": f"Bearer {os.getenv('QWEN_API_KEY')}",
                        "Content-Type": "application/json"
                    }
                    
                    messages = [
                        {"role": "system", "content": "你是一个有帮助的AI助手，请用中文回答用户的问题，并使用Markdown格式来组织你的回答，包括标题、列表、强调等。"}
                    ]
                    
                    # 添加对话历史
                    messages.extend(conversation_history[-5:])
                    
                    # 添加当前用户消息
                    messages.append({"role": "user", "content": request.message})
                    
                    data = {
                        "model": "qwen-plus",
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.7,
                        "stream": True  # 启用流式输出
                    }
                    
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        async with client.stream(
                            "POST",
                            f"{os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')}/chat/completions",
                            headers=headers,
                            json=data
                        ) as response:
                            if response.status_code == 200:
                                ai_response = ""
                                async for line in response.aiter_lines():
                                    if line.startswith("data: "):
                                        data_str = line[6:]  # 移除 "data: " 前缀
                                        if data_str.strip() == "[DONE]":
                                            break
                                        try:
                                            chunk = json.loads(data_str)
                                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                                delta = chunk["choices"][0].get("delta", {})
                                                if "content" in delta:
                                                    content = delta["content"]
                                                    ai_response += content
                                                    yield f"data: {json.dumps({'content': content, 'type': 'chunk'})}\n\n"
                                        except json.JSONDecodeError:
                                            continue
                            else:
                                ai_response = f"抱歉，AI服务暂时不可用。错误代码：{response.status_code}"
                                yield f"data: {json.dumps({'content': ai_response, 'type': 'error'})}\n\n"
                                
                except Exception as e:
                    ai_response = f"AI服务调用失败：{str(e)}"
                    yield f"data: {json.dumps({'content': ai_response, 'type': 'error'})}\n\n"
            
            # 保存完整的AI回复到数据库
            ai_message = Message(
                id=str(uuid.uuid4()),
                chat_session_id=session.id,
                content=ai_response,
                type=MessageType.bot
            )
            db.add(ai_message)
            
            # 更新会话时间
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'message_id': ai_message.id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': f'聊天失败: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@router.get("/sessions")
async def get_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的聊天会话列表"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    result = []
    for session in sessions:
        session_data = {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": []
        }
        
        # 添加消息 - 按时间戳升序排列
        messages = db.query(Message).filter(
            Message.chat_session_id == session.id
        ).order_by(Message.timestamp.asc()).all()
        
        for message in messages:
            message_data = {
                "id": message.id,
                "chat_session_id": message.chat_session_id,
                "content": message.content,
                "type": message.type,
                "image_url": message.image_url,
                "image_path": message.image_path,
                "timestamp": message.timestamp
            }
            session_data["messages"].append(message_data)
        
        result.append(session_data)
    
    return result

@router.post("/sessions")
async def create_chat_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title="新对话"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": []
    }

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(session)
    db.commit()
    
    return {"message": "会话删除成功"}
