import requests
import json
from typing import List, Dict
from .config import POLLINATIONS_TOKEN, pollinations_err_info, new_chat_info

POLLINATIONS_API_URL = "https://text.pollinations.ai/openai"

def generate_content(prompt: str) -> str:
    """Generate text from prompt using Pollinations AI"""
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        params = {
            "token": POLLINATIONS_TOKEN
        }
        
        response = requests.post(
            POLLINATIONS_API_URL,
            headers=headers,
            json=data,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return f"{pollinations_err_info}\nUnexpected response format"
        else:
            return f"{pollinations_err_info}\nAPI Error: {response.status_code}"
            
    except Exception as e:
        return f"{pollinations_err_info}\n{repr(e)}"


class ChatConversation:
    """
    Manages ongoing chat conversation with Pollinations AI
    """

    def __init__(self) -> None:
        self.history: List[Dict[str, str]] = []

    def send_message(self, prompt: str) -> str:
        """Send message and maintain conversation history"""
        if prompt.startswith("/new"):
            self.__init__()
            return new_chat_info
        
        try:
            # Add user message to history
            self.history.append({"role": "user", "content": prompt})
            
            # Prepare messages for API (include recent history)
            messages = self.history[-10:]  # Keep last 10 messages to avoid token limits
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }
            
            params = {
                "token": POLLINATIONS_TOKEN
            }
            
            response = requests.post(
                POLLINATIONS_API_URL,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    assistant_message = result['choices'][0]['message']['content']
                    # Add assistant response to history
                    self.history.append({"role": "assistant", "content": assistant_message})
                    return assistant_message
                else:
                    return f"{pollinations_err_info}\nUnexpected response format"
            else:
                return f"{pollinations_err_info}\nAPI Error: {response.status_code}"
                
        except Exception as e:
            return f"{pollinations_err_info}\n{repr(e)}"

    @property
    def history_length(self):
        return len(self.history)