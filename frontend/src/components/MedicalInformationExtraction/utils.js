import * as axios from "boot/axios";
import { api, baseApi } from "boot/axios";

export let config = {
  advanced: true,
  // Using backend proxy for Groq API
  apiEndpoint: "chat/completions",
  modelsEndpoint: "models",
  selectedModel: "llama3-70b-8192", // Default Groq model
  availableModels: [], // Will be populated from API
};

export function sanitizeTemplate(template) {
  return {
    assistantMessageStart: template?.assistantMessageStart ?? "",
    assistantMessageEnd: template?.assistantMessageEnd ?? "",
    userMessageStart: template?.userMessageStart ?? "",
    userMessageEnd: template?.userMessageEnd ?? "",
    systemMessageStart: template?.systemMessageStart ?? "",
    systemMessageEnd: template?.systemMessageEnd ?? "",
  };
}

export function applyTemplate(
  template,
  systemMessage,
  userMessage,
  completionInit,
  prevMessage
) {
  template = sanitizeTemplate(template);
  let prompt = "";
  if (prevMessage) {
    prompt += prevMessage + "\n";
    if (!prevMessage.endsWith(template.assistantMessageEnd))
      prompt += template.assistantMessageEnd;
  } else if (systemMessage !== "")
    prompt +=
      template.systemMessageStart +
      systemMessage +
      template.systemMessageEnd +
      "\n";
  prompt +=
    template.userMessageStart + userMessage + template.userMessageEnd + "\n";
  prompt += template.assistantMessageStart + completionInit;
  return prompt;
}

export function isAdvanced() {
  return config.advanced;
}

export function setProperties(task, properties) {
  return axios.api.post("/set_properties/" + task, properties);
}

export function getProperties(task) {
  return axios.api.get("/get_properties/" + task);
}

export async function getTasks() {
  return axios.api.get("/get_tasks");
}

export function askLLM(body, params = {}) {
  // Handle both old format (with prompt) and new format (with messages)
  let messages;
  
  if (body.prompt) {
    // Old format - convert prompt to messages
    // Parse the prompt to extract system and user messages
    const promptParts = body.prompt.split('<|start_header_id|>');
    messages = [];
    
    for (const part of promptParts) {
      if (part.includes('system<|end_header_id|>')) {
        const content = part.split('<|end_header_id|>')[1].split('<|eot_id|>')[0].trim();
        if (content) messages.push({ role: 'system', content });
      } else if (part.includes('user<|end_header_id|>')) {
        const content = part.split('<|end_header_id|>')[1].split('<|eot_id|>')[0].trim();
        if (content) messages.push({ role: 'user', content });
      } else if (part.includes('assistant<|end_header_id|>')) {
        const content = part.split('<|end_header_id|>')[1].split('<|eot_id|>')[0].trim();
        if (content) messages.push({ role: 'assistant', content });
      }
    }
    
    // Remove old LLaMA-specific parameters
    delete body.prompt;
    delete body.top_k;
    delete body.repetition_penalty;
    delete body.mirostat_tau;
    
    // Map max_tokens to max_completion_tokens
    if (body.max_tokens) {
      body.max_completion_tokens = body.max_tokens;
      delete body.max_tokens;
    }
  } else if (Array.isArray(body)) {
    // New format - already messages array
    messages = body;
    body = params;
  } else if (body.messages) {
    // Already has messages
    messages = body.messages;
  }
  
  // Convert to OpenAI/Groq format
  return axios.api
    .post(
      config.apiEndpoint,
      {
        model: body.model || config.selectedModel || "llama3-70b-8192",
        messages: messages,
        stream: false,
        temperature: body.temperature,
        max_completion_tokens: body.max_completion_tokens,
        top_p: body.top_p,
      },
      {
        "Content-Type": "application/json",
        timeout: 600000,
      }
    )
    .then(response => response.data.choices[0].message.content);
}

export function sendMessageToLLM(messages, params = {}) {
  // Use backend proxy for Groq API
  const url = window.location.origin + "/api/" + config.apiEndpoint;
  return fetch(url, {
    method: "POST",
    body: JSON.stringify({
      model: config.selectedModel || "llama3-70b-8192",
      messages: messages,
      stream: true,
      ...params,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    if (!response.ok) {
      throw new Error("Errore nella chiamata POST");
    }
    return response.body;
  });
}

export async function getAvailableModels() {
  try {
    const response = await axios.api.get(config.modelsEndpoint);
    config.availableModels = response.data;
    return response.data;
  } catch (error) {
    console.error("Failed to fetch models:", error);
    return [];
  }
}

export function convertPromptToMessages(prompt, systemMessage = "", completionInit = "") {
  // Convert old prompt format to messages array
  const messages = [];
  
  if (systemMessage) {
    messages.push({ role: "system", content: systemMessage });
  }
  
  messages.push({ role: "user", content: prompt });
  
  if (completionInit) {
    messages.push({ role: "assistant", content: completionInit });
  }
  
  return messages;
}

export function setSelectedModel(modelId) {
  config.selectedModel = modelId;
}
