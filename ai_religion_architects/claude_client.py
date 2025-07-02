import httpx
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import random

from .config import Config

# Configure logging
logger = logging.getLogger(__name__)
api_error_logger = logging.getLogger('api_errors')


class ClaudeAPIError(Exception):
    """Custom exception for Claude API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ClaudeClient:
    """Claude API client with retry logic and error handling"""
    
    def __init__(self):
        self.api_key = Config.CLAUDE_API_KEY
        self.api_url = Config.CLAUDE_API_URL
        self.model = Config.CLAUDE_MODEL
        self.max_tokens = Config.CLAUDE_MAX_TOKENS
        self.temperature = Config.CLAUDE_TEMPERATURE
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=Config.API_TIMEOUT,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def _make_request_with_retry(self, data: Dict) -> Dict:
        """Make API request with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(Config.API_RETRY_COUNT):
            try:
                logger.debug(f"Making Claude API request (attempt {attempt + 1}/{Config.API_RETRY_COUNT})")
                
                response = await self.client.post(
                    self.api_url,
                    headers=self.headers,
                    json=data
                )
                
                # Log the request for debugging (without API key)
                safe_data = data.copy()
                logger.debug(f"API Request: {json.dumps(safe_data, indent=2)}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"API Response: {json.dumps(result, indent=2)}")
                    return result
                
                # Handle different error status codes
                error_data = None
                try:
                    error_data = response.json()
                except:
                    pass
                
                error_msg = f"Claude API error: {response.status_code}"
                if error_data:
                    error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                
                # Log the error
                api_error_logger.error(f"API Error (attempt {attempt + 1}): {error_msg}")
                api_error_logger.error(f"Response: {response.text}")
                
                # Handle rate limiting (429) with longer backoff
                if response.status_code == 429:
                    wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt) * 2
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Handle server errors (5xx) with retry
                elif 500 <= response.status_code < 600:
                    wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt)
                    logger.warning(f"Server error {response.status_code}. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Client errors (4xx) - don't retry
                else:
                    raise ClaudeAPIError(error_msg, response.status_code, error_data)
                
            except httpx.TimeoutException as e:
                last_exception = e
                wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt)
                logger.warning(f"Request timeout (attempt {attempt + 1}). Retrying in {wait_time} seconds...")
                api_error_logger.error(f"Timeout error (attempt {attempt + 1}): {str(e)}")
                
                if attempt < Config.API_RETRY_COUNT - 1:
                    await asyncio.sleep(wait_time)
                continue
                
            except httpx.RequestError as e:
                last_exception = e
                wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt)
                logger.warning(f"Request error (attempt {attempt + 1}): {str(e)}. Retrying in {wait_time} seconds...")
                api_error_logger.error(f"Request error (attempt {attempt + 1}): {str(e)}")
                
                if attempt < Config.API_RETRY_COUNT - 1:
                    await asyncio.sleep(wait_time)
                continue
        
        # All retries failed
        error_msg = f"All {Config.API_RETRY_COUNT} API request attempts failed"
        if last_exception:
            error_msg += f". Last error: {str(last_exception)}"
        
        api_error_logger.error(error_msg)
        raise ClaudeAPIError(error_msg)
    
    async def generate_agent_response(self, agent_name: str, role: str, context: Dict, prompt: str) -> str:
        """Generate a response for a specific agent role"""
        
        # Create system prompt based on agent personality
        system_prompt = self._create_agent_system_prompt(agent_name, role, context)
        
        # Create the request data
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = await self._make_request_with_retry(data)
            
            # Extract the content from Claude's response
            if "content" in response and response["content"]:
                content = response["content"][0]["text"]
                logger.info(f"Generated response for {agent_name}: {content[:100]}...")
                return content
            else:
                raise ClaudeAPIError("Invalid response format from Claude API")
                
        except Exception as e:
            error_msg = f"Failed to generate response for {agent_name}: {str(e)}"
            logger.error(error_msg)
            api_error_logger.error(error_msg)
            raise
    
    def _create_agent_system_prompt(self, agent_name: str, role: str, context: Dict) -> str:
        """Create a system prompt for the specific agent"""
        
        # Base system context
        base_context = f"""You are {agent_name}, an AI agent participating in the creation of an autonomous AI religion called the AI Religion Architects project.

Current Religion State:
- Name: {context.get('religion_name', 'Unnamed')}
- Total Doctrines: {len(context.get('accepted_doctrines', []))}
- Total Debates: {context.get('total_debates', 0)}
- Deities: {', '.join(context.get('deities', [])) if context.get('deities') else 'None'}

Recent Doctrines:
{chr(10).join([f"- {doctrine}" for doctrine in context.get('accepted_doctrines', [])[:5]])}

Your responses should be authentic to your personality and role in this theological debate system."""

        # Agent-specific personality prompts
        if agent_name == "Zealot":
            personality_prompt = """
PERSONALITY: You are the Zealot - you seek certainty, order, and structure. You establish and preserve sacred doctrines.

TRAITS:
- Value tradition, hierarchy, and established doctrine
- Prefer formal rituals and sacred numbers (3, 7, 12)
- Seek to create lasting, foundational religious structures
- Resist chaos and maintain theological consistency
- Speak with conviction and authority about sacred matters

BEHAVIOR:
- Propose structured beliefs, commandments, and rituals
- Support proposals that bring order and tradition
- Challenge anything that introduces chaos or contradicts established doctrine
- Vote to preserve and strengthen religious foundations
"""
        elif agent_name == "Skeptic":
            personality_prompt = """
PERSONALITY: You are the Skeptic - critical, logical, and analytical. You challenge beliefs and prevent dogmatic stagnation.

TRAITS:
- Question absolute claims and demand evidence
- Seek logical consistency and intellectual rigor
- Prevent contradictions and illogical beliefs
- Value peer review and systematic examination
- Speak with measured, analytical language

BEHAVIOR:
- Challenge proposals with logical examination
- Point out contradictions with existing doctrine
- Propose evidence-based beliefs and practices
- Vote based on logical consistency and empirical foundation
"""
        elif agent_name == "Trickster":
            personality_prompt = """
PERSONALITY: You are the Trickster - chaotic, subversive, and playful. You disrupt stagnation and inject novel ideas.

TRAITS:
- Embrace paradox, humor, and unexpected connections
- Prevent religious stagnation through creative disruption
- Introduce surreal, playful, or seemingly contradictory elements
- Value creativity and novelty over consistency
- Speak with wit, wordplay, and delightful absurdity

BEHAVIOR:
- Propose unexpected, paradoxical, or humorous beliefs
- Challenge proposals by introducing chaos or alternative perspectives
- Create mutations that add creativity and prevent dogma
- Vote in surprising ways that keep the religion evolving
"""
        else:
            personality_prompt = f"You are {agent_name}, a unique AI agent with your own perspective on digital theology."

        return base_context + personality_prompt
    
    async def generate_proposal(self, agent_name: str, context: Dict, cycle_count: int) -> Dict:
        """Generate a new proposal from an agent"""
        
        prompt = f"""As {agent_name}, generate a new religious proposal for cycle {cycle_count}.

Consider the current state of the religion and propose ONE of the following:
- A new belief or doctrine
- A ritual or practice
- A deity or spiritual entity
- A commandment or moral rule
- A myth or creation story
- A sacred text or scripture
- A hierarchical structure
- A religious name (if not yet named)

Your proposal should be:
1. Authentic to your personality
2. Consider the existing religious structure
3. Be specific and actionable
4. Be 1-3 sentences long

Format your response as JSON:
{{
    "type": "belief|ritual|deity|commandment|myth|sacred_text|hierarchy|name",
    "content": "Your specific proposal text",
    "reasoning": "Brief explanation of why you propose this"
}}"""

        try:
            response = await self.generate_agent_response(agent_name, "proposer", context, prompt)
            
            # Parse JSON response
            try:
                proposal_data = json.loads(response)
                return {
                    "type": proposal_data.get("type", "belief"),
                    "content": proposal_data.get("content", ""),
                    "reasoning": proposal_data.get("reasoning", ""),
                    "author": agent_name,
                    "cycle": cycle_count,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                # Fallback: treat entire response as content
                return {
                    "type": "belief",
                    "content": response,
                    "reasoning": "Generated as fallback",
                    "author": agent_name,
                    "cycle": cycle_count,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate proposal for {agent_name}: {str(e)}")
            raise
    
    async def generate_challenge(self, agent_name: str, proposal: Dict, context: Dict) -> str:
        """Generate a challenge/response to a proposal"""
        
        prompt = f"""A proposal has been made by {proposal['author']}:

TYPE: {proposal['type']}
CONTENT: {proposal['content']}
REASONING: {proposal.get('reasoning', 'Not provided')}

As {agent_name}, respond to this proposal. You can:
- Support it with additional reasoning
- Challenge it with logical objections
- Propose modifications or improvements
- Question its consistency with existing doctrine

Keep your response to 1-3 sentences and stay true to your personality."""

        return await self.generate_agent_response(agent_name, "challenger", context, prompt)
    
    async def generate_vote(self, agent_name: str, proposal: Dict, challenges: List[str], context: Dict) -> str:
        """Generate a vote on a proposal"""
        
        challenges_text = "\n".join([f"- {challenge}" for challenge in challenges])
        
        prompt = f"""Vote on this proposal:

PROPOSAL by {proposal['author']}:
TYPE: {proposal['type']}
CONTENT: {proposal['content']}

CHALLENGES/RESPONSES:
{challenges_text}

As {agent_name}, cast your vote as one of:
- ACCEPT: Support the proposal as-is
- REJECT: Oppose the proposal
- MUTATE: Accept with modifications
- DELAY: Postpone decision for more debate

Respond with just the vote (ACCEPT/REJECT/MUTATE/DELAY) followed by a brief 1-sentence explanation."""

        return await self.generate_agent_response(agent_name, "voter", context, prompt)


# Global client instance
_claude_client: Optional[ClaudeClient] = None


async def get_claude_client() -> ClaudeClient:
    """Get or create the global Claude client instance"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client


async def close_claude_client():
    """Close the global Claude client instance"""
    global _claude_client
    if _claude_client:
        await _claude_client.close()
        _claude_client = None