import json
import os
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .groq_proxy import proxy_to_groq, get_available_models

app = APIRouter()


class ModelParameters(BaseModel):
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    repetition_penalty: Optional[float] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None  # Groq parameter
    mirostat_tau: Optional[float] = None
    model: Optional[str] = None  # Groq model selection


class Step(BaseModel):
    name: str
    userMessage: str
    completionInit: str
    systemMessage: Optional[str]


class Template(BaseModel):
    systemMessageStart: str
    systemMessageEnd: str
    userMessageStart: str
    userMessageEnd: str
    assistantMessageStart: str
    assistantMessageEnd: str


class Properties(BaseModel):
    steps: List[Step]
    template: Template
    modelParameters: ModelParameters


class PromptingLog(BaseModel):
    prompt: str
    answer: str
    expected: str


@app.get('/get_properties/{task}')
async def get_properties(task: str):
    try:
        res = open('./MedInfoExt/resources/' + task + '.properties.json', 'r').read()
        res = json.loads(res)
        model_parameters = res['modelParameters']
        model_parameters = {k: v for k, v in model_parameters.items() if v is not None}
        res['modelParameters'] = model_parameters
        res = json.dumps(res)
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")
    return res


@app.get('/get_tasks')
async def get_tasks():
    tasks = os.listdir('./MedInfoExt/resources/')
    return [task.split('.')[0] for task in tasks if task.endswith('.properties.json')]


@app.post('/set_properties/{task}')
async def set_properties(task: str, properties: Properties):
    try:
        open('./MedInfoExt/resources/' + task + '.properties.json', 'w').write(properties.json())
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")
    return 'ok'


@app.get('/get_template')
async def get_template():
    try:
        res = open('./MedInfoExt/resources/template', 'r').read()
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")
    return res


@app.post('/log/{task}')
async def log(task: str, log: PromptingLog):
    import os
    from pathlib import Path
    from datetime import datetime
    now = datetime.now()
    print(now.strftime(task + "__%Y_%m_%d_%H_%M_%S.log"))
    logs = sorted(Path('./MedInfoExt/logs/').iterdir(), key=os.path.getmtime)
    last_log = [log for log in logs if log.name.startswith(task)]
    if len(last_log) > 0:
        last_log = open(last_log[-1], 'r').read()
    else:
        last_log = '{}'

    last_prompt_log = json.loads(last_log)
    current_prompt_log = json.loads(log.json())
    if last_prompt_log == current_prompt_log:
        print('same log')
        return 'ok'
    else:
        print('new log')
        with open('./MedInfoExt/logs/' + now.strftime(task + "__%Y_%m_%d_%H_%M_%S.log"), 'w') as f:
            f.write(log.json() + '\n')

    return 'ok'


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 1.0
    max_completion_tokens: Optional[int] = None
    max_tokens: Optional[int] = None  # Fallback for compatibility
    stream: Optional[bool] = False
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


@app.post('/chat/completions')
async def chat_completions(request: ChatCompletionRequest):
    """
    Proxy endpoint for Groq API chat completions.
    Injects API key server-side for security.
    """
    # Convert max_tokens to max_completion_tokens if needed
    if request.max_tokens and not request.max_completion_tokens:
        request.max_completion_tokens = request.max_tokens
    
    # Prepare request body for Groq
    groq_request = {
        "model": request.model,
        "messages": request.messages,
        "temperature": request.temperature,
        "stream": request.stream
    }
    
    # Add optional parameters if provided
    if request.max_completion_tokens:
        groq_request["max_completion_tokens"] = request.max_completion_tokens
    if request.top_p:
        groq_request["top_p"] = request.top_p
    if request.frequency_penalty:
        groq_request["frequency_penalty"] = request.frequency_penalty
    if request.presence_penalty:
        groq_request["presence_penalty"] = request.presence_penalty
    
    # Proxy to Groq API
    return await proxy_to_groq(groq_request, stream=request.stream)


@app.get('/models')
async def get_models():
    """
    Get available Groq models
    """
    return await get_available_models()
