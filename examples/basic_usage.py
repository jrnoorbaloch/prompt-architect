"""Use Prompt Architect from your own Python code."""
from prompt_architect import engineer

# Claude (needs ANTHROPIC_API_KEY)
result = engineer("write a blog about AI", provider="anthropic", target_model="Claude")
print(result.to_markdown())

# Local & free with Ollama:
# result = engineer("make a chatbot for my shop", provider="ollama", model="llama3.1", mode="system")

# Any OpenAI-compatible API (Groq, DeepSeek, Together, LM Studio ...):
# result = engineer("summarize this report", provider="custom",
#                   base_url="https://api.groq.com/openai/v1", model="llama-3.3-70b-versatile", api_key="...")
