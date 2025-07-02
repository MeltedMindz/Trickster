# Claude API Integration Guide

This document explains the Claude API integration for AI Religion Architects, including setup, configuration, and technical details.

## Overview

The AI Religion Architects system now uses Anthropic's Claude API to power the three AI agents (Zealot, Skeptic, Trickster) with sophisticated natural language understanding and generation. This replaces the original local agent implementations with cloud-based AI responses.

## Key Features

- ✅ **APScheduler Rate Limiting**: Exactly one debate cycle per hour (configurable)
- ✅ **No Infinite Loops**: Scheduler-based architecture prevents resource abuse
- ✅ **Retry Logic**: Exponential backoff with 3 retries by default
- ✅ **Error Handling**: Dedicated error logging to `api_errors.log`
- ✅ **Security**: Environment variable-based API key management
- ✅ **Real-time Monitoring**: WebSocket broadcasting of Claude-generated debates

## Setup Instructions

### 1. Get Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Note: The API key should start with `sk-ant-api03-`

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API key
CLAUDE_API_KEY=sk-ant-api03-your-actual-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=2000
CYCLE_INTERVAL_HOURS=1
```

### 3. Install Dependencies

```bash
pip install -r requirements-backend.txt
```

This installs:
- `httpx` - Async HTTP client for API calls
- `APScheduler` - Job scheduling for hourly cycles
- `anthropic` - Official Claude API client (optional)
- `python-dotenv` - Environment variable loading

### 4. Test Integration

```bash
python test_claude_integration.py
```

This validates:
- Configuration loading
- Claude API connectivity
- Database operations
- Proposal generation
- Full integration test

### 5. Run the System

```bash
# Full system with WebSocket monitoring
python run_claude_system.py

# Test single cycle
python run_claude_system.py --test-cycle

# Skip WebSocket server
python run_claude_system.py --no-websocket
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_API_KEY` | Required | Your Anthropic API key |
| `CLAUDE_MODEL` | `claude-3-sonnet-20240229` | Claude model to use |
| `CLAUDE_MAX_TOKENS` | `2000` | Maximum tokens per response |
| `CLAUDE_TEMPERATURE` | `0.7` | Response creativity (0.0-1.0) |
| `CYCLE_INTERVAL_HOURS` | `1` | Hours between debate cycles |
| `API_RETRY_COUNT` | `3` | Number of retry attempts |
| `API_RETRY_DELAY` | `1.0` | Initial retry delay (seconds) |
| `API_RETRY_BACKOFF` | `2.0` | Retry delay multiplier |
| `API_TIMEOUT` | `60` | Request timeout (seconds) |

### Model Options

Supported Claude models:
- `claude-3-sonnet-20240229` (Recommended) - Balanced performance and cost
- `claude-3-opus-20240229` - Highest capability, higher cost
- `claude-3-haiku-20240307` - Fastest, lowest cost

## Technical Architecture

### APScheduler Integration

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
scheduler.add_job(
    func=run_debate_cycle,
    trigger=IntervalTrigger(hours=1),
    id='debate_cycle',
    max_instances=1  # Prevents overlapping cycles
)
```

### Claude API Client

```python
class ClaudeClient:
    async def generate_agent_response(self, agent_name, role, context, prompt):
        # System prompt based on agent personality
        system_prompt = self._create_agent_system_prompt(agent_name, role, context)
        
        # API request with retry logic
        response = await self._make_request_with_retry({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        return response["content"][0]["text"]
```

### Agent Personalities

Each agent has a distinct system prompt that shapes Claude's responses:

**Zealot**: 
- Values tradition, hierarchy, and established doctrine
- Proposes structured beliefs and formal rituals
- Resists chaos and maintains theological consistency

**Skeptic**: 
- Questions absolute claims and demands evidence
- Seeks logical consistency and intellectual rigor
- Prevents contradictions and illogical beliefs

**Trickster**: 
- Embraces paradox, humor, and unexpected connections
- Introduces surreal and playful elements
- Prevents religious stagnation through creative disruption

## Rate Limiting & Error Handling

### Rate Limiting Strategy

1. **APScheduler**: Ensures exactly one cycle per hour
2. **Max Instances**: Prevents overlapping cycles
3. **Graceful Degradation**: System continues if individual cycles fail

### Error Handling

```python
async def _make_request_with_retry(self, data):
    for attempt in range(Config.API_RETRY_COUNT):
        try:
            response = await self.client.post(self.api_url, json=data)
            if response.status_code == 200:
                return response.json()
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt) * 2
                await asyncio.sleep(wait_time)
                continue
                
        except httpx.TimeoutException:
            # Exponential backoff
            wait_time = Config.API_RETRY_DELAY * (Config.API_RETRY_BACKOFF ** attempt)
            await asyncio.sleep(wait_time)
```

### Error Logging

All API errors are logged to `logs/api_errors.log`:

```
2024-01-15 10:30:15 - ERROR - API Error (attempt 1): Claude API error: 429 - Rate limit exceeded
2024-01-15 10:30:17 - ERROR - Timeout error (attempt 2): Request timeout after 60 seconds
```

## Security Considerations

### API Key Security

1. **Environment Variables**: Never hardcode API keys
2. **`.env` File**: Not committed to version control
3. **Docker Secrets**: Use Docker secrets in production
4. **Validation**: API key format validation on startup

### Production Security

```bash
# Docker production setup
echo "CLAUDE_API_KEY=your-key" | docker secret create claude_api_key -

# Reference in docker-compose.yml
secrets:
  - claude_api_key
environment:
  - CLAUDE_API_KEY_FILE=/run/secrets/claude_api_key
```

## Monitoring & Observability

### Real-time Monitoring

The WebSocket server broadcasts Claude-generated debates in real-time:

```javascript
// Frontend receives live updates
{
  "type": "new_debate",
  "data": {
    "cycle_number": 42,
    "proposal_content": "Claude-generated proposal...",
    "challenges": ["Skeptic response...", "Trickster chaos..."],
    "outcome": "accepted"
  }
}
```

### Logging

Multiple log files for different purposes:

- `ai_religion_architects.log` - General application logs
- `api_errors.log` - Claude API specific errors
- `debate_session_*.log` - Detailed debate transcripts

### Health Monitoring

```bash
# Check system status
curl http://localhost:8000/api/orchestrator/status

# Response
{
  "running": true,
  "paused": false,
  "cycle_count": 12,
  "next_cycle": "2024-01-15T11:30:00Z"
}
```

## Cost Management

### Token Usage Optimization

1. **Concise Prompts**: Optimized system prompts for efficiency
2. **Response Limits**: Configurable max tokens per response
3. **Cycle Frequency**: Hourly cycles balance activity with costs

### Estimated Costs

Based on Claude 3 Sonnet pricing (as of 2024):

- **Input**: $3 per million tokens
- **Output**: $15 per million tokens
- **Per Cycle**: ~500 input + 200 output tokens = ~$0.004
- **Daily**: 24 cycles × $0.004 = ~$0.10
- **Monthly**: ~$3.00

## Troubleshooting

### Common Issues

**API Key Not Working**
```bash
# Verify API key format
echo $CLAUDE_API_KEY | grep -E "^sk-ant-api03-"

# Test API connectivity
python test_claude_integration.py
```

**Rate Limiting**
```bash
# Check logs
tail -f logs/api_errors.log

# Increase retry delay
export API_RETRY_DELAY=2.0
```

**Scheduler Not Running**
```bash
# Check scheduler status
grep "Scheduler started" logs/ai_religion_architects.log

# Verify no overlapping jobs
grep "max_instances" logs/ai_religion_architects.log
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python run_claude_system.py
```

## Migration from Local Agents

The Claude integration replaces local agent implementations:

| Component | Before | After |
|-----------|---------|-------|
| Agent Logic | Python classes | Claude API prompts |
| Response Generation | Local methods | API calls with retry |
| Cycle Timing | `time.sleep()` loops | APScheduler intervals |
| Error Handling | Basic exceptions | Comprehensive retry logic |
| Rate Limiting | None | Built-in APScheduler + API limits |

Existing databases and memory structures remain compatible.

## Future Enhancements

Potential improvements for the Claude integration:

1. **Multi-Model Support**: Compare responses from different Claude models
2. **Custom Fine-tuning**: Train specialized religious debate models
3. **Advanced Prompting**: Implement chain-of-thought reasoning
4. **Cost Optimization**: Dynamic model selection based on complexity
5. **Conversation Memory**: Multi-turn conversations within cycles

## Support

For Claude integration issues:

1. Check the test script: `python test_claude_integration.py`
2. Review error logs: `logs/api_errors.log`
3. Verify configuration: Check all environment variables
4. Consult Anthropic documentation: [Claude API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)