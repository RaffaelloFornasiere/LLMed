import os
import json
import httpx
from typing import Optional, Dict, Any, AsyncIterator, List
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")


async def proxy_to_groq(request_body: Dict[str, Any], stream: bool = False):
    """
    Proxy requests to Groq API with API key injection
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Ensure stream parameter is set correctly
    request_body["stream"] = stream
    
    if stream:
        # For streaming responses
        async def generate():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    GROQ_API_URL,
                    json=request_body,
                    headers=headers,
                    timeout=60.0
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Groq API error: {error_text.decode()}"
                        )
                    
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # For non-streaming responses
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_API_URL,
                json=request_body,
                headers=headers,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Groq API error: {response.text}"
                )
            
            return response.json()


async def get_available_models() -> List[Dict[str, Any]]:
    """
    Fetch available models from Groq API
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GROQ_MODELS_URL,
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch models: {response.text}"
            )
        
        models_data = response.json()
        # Extract model IDs and relevant info
        models = []
        for model in models_data.get("data", []):
            models.append({
                "id": model.get("id"),
                "owned_by": model.get("owned_by"),
                "active": model.get("active", True),
                "context_window": model.get("context_window")
            })
        return models


def convert_template_to_messages(template_prompt: str, completion_init: str = "") -> list:
    """
    Convert old template format to OpenAI/Groq message format
    """
    messages = []
    
    # Parse the template format
    lines = template_prompt.split('\n')
    current_role = None
    current_content = []
    
    for line in lines:
        if '<|im_start|>system' in line:
            if current_role and current_content:
                messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
            current_role = 'system'
            current_content = []
        elif '<|im_start|>user' in line:
            if current_role and current_content:
                messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
            current_role = 'user'
            current_content = []
        elif '<|im_start|>assistant' in line:
            if current_role and current_content:
                messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
            current_role = 'assistant'
            current_content = []
        elif '<|im_end|>' not in line and line.strip():
            current_content.append(line)
    
    # Add the last message
    if current_role and current_content:
        messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
    
    # Add completion_init as assistant message if provided
    if completion_init:
        messages.append({"role": "assistant", "content": completion_init})
    
    return messages