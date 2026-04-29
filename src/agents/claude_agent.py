from typing import List, Dict, Optional
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

from agents.agent_memory import AgentMemory
from constants.memory_constants import MEMORY_PATH

class ClaudeAgent:
  api_key: str
  model_name: str
  memory: AgentMemory

  def __init__(self, api_key: str, memory_dir: str = MEMORY_PATH):
    self.memory = AgentMemory(memory_dir)
    self.api_key = api_key
    self.model_name = 'claude-sonnet-4-6'

    # Init agent facts
    self.memory.add_fact('I am an AI assistant with memory capabilities.')
    self.memory.add_fact('I can remember user interactions and recall them later.')
    self.memory.add_fact('I can store and retrieve factural information.')
    self.memory.add_fact('I can remember and execute procedure and workflows.')

  def generate_system_prompt(self) -> str:
    return """You are an AI assistant with memory capabilities. You can remember user interactions, facts you have learned and procedures you know.
Use provided context to give the personalised, contextually relevant responses. If you don't have relevant memory information, you can draw your general knowledge.
Always be helpful, accurate and conversational.
"""

  def query(self, user_message: str) -> str:
    """Process user message and generate a response."""
    context = self.memory.generate_context_for_llm(user_message)
    messages: List[Dict[str, str]] = [
      {
        'role': 'system',
        'content': self.generate_system_prompt()
      },
      {
        'role': 'system',
        'content': f'Context from memory:\n{context}'
      },
      {
        'role': 'user',
        'content': user_message
      }
    ]

    llm_model = ChatAnthropic(
      api_key=self.api_key,
      model_name=self.model_name,
      temperature=0.9
    )
    agent = create_agent(llm_model)

    try:
      response = agent.invoke({
        'messages': messages
      })

      result = response['messages'][-1].content

      self.memory.add_conversation(
        user_message=user_message,
        agent_response=result,
      )

      return result
    except Exception as error:
      error_message = f"Error: API request failed:\n{str(error)}"
      return error_message

  def learn_fact(self, fact: str, category: Optional[str] = None) -> str:
    self.memory.add_fact(fact, category)
    return f"I have learned this fact: {fact}"
  
  def learn_procedure(self, name: str, steps: List[str], description: Optional[str] = None) -> str:
    self.memory.add_procedure(name, steps, description)
    return f"I have learned this procedure: {name}"