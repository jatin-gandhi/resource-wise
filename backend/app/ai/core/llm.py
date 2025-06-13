"""LLM implementation using OpenAI."""

import json
import time
from typing import AsyncGenerator

import structlog
from openai import AsyncOpenAI

from app.ai.core.config import AIConfig
from app.core.config import settings

logger = structlog.get_logger()


class LLMService:
    """LLM service using OpenAI API."""

    def __init__(self, config: AIConfig):
        """Initialize the LLM service."""
        self.config = config
        
        # Use OpenAI API key from main settings
        api_key = config.api_key or settings.OPENAI_API_KEY
        
        if not api_key:
            logger.warning("openai api key missing")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=config.api_base
            )
            logger.info(f"openai client ready ({config.model_name})")

    def _create_prompt(self, user_message: str) -> str:
        """Create a prompt for the OpenAI API."""
        return f"""You are a versatile chat assistant for a user for day to day task. The user is a software developer.
Respond for this message from the user: {user_message}"""

    async def stream_completion(
        self,
        user_message: str,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion response."""
        if not self.client:
            logger.error("openai client not available")
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'OpenAI API key not configured'}})}\n\n"
            return

        try:
            logger.info(f"msg received: {len(user_message)}chars")
            
            prompt = self._create_prompt(user_message)
            
            logger.info("calling openai api...")
            
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'data': {'session_id': session_id}})}\n\n"

            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=self.config.temperature,
                max_tokens=1000,
            )

            logger.info("openai streaming started")
            
            accumulated_content = ""
            token_count = 0
            
            # Process streaming response
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    accumulated_content += token
                    token_count += 1
                    
                    # Send token event
                    yield f"data: {json.dumps({'type': 'token', 'data': {'token': token, 'content': accumulated_content}})}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'data': {'content': accumulated_content, 'session_id': session_id}})}\n\n"
            yield "data: [DONE]\n\n"

            logger.info(f"response sent: {len(accumulated_content)}chars, {token_count}tokens")

        except Exception as e:
            logger.error(f"openai api failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': f'LLM API error: {str(e)}'}})}\n\n"

    async def get_completion(
        self,
        user_message: str,
    ) -> str:
        """Get a non-streaming chat completion response."""
        if not self.client:
            logger.error("openai client not available")
            raise ValueError("OpenAI API key not configured")

        try:
            logger.info(f"msg received: {len(user_message)}chars")
            
            prompt = self._create_prompt(user_message)
            
            logger.info("calling openai api...")

            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=1000,
            )

            content = response.choices[0].message.content or ""
            
            # Extract token usage if available
            usage = response.usage
            tokens_used = f", {usage.total_tokens}tokens" if usage else ""
            
            logger.info(f"response received: {len(content)}chars{tokens_used}")
            
            return content

        except Exception as e:
            logger.error(f"openai api failed: {str(e)}")
            raise
