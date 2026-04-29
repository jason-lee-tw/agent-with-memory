import os
import json
import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple

from constants.memory_constants import MEMORY_PATH


class AgentMemory:
  """Simple memory system for AI agent."""

  __storage_dir: str

  __fact_file_path: str
  __conversation_file_path: str
  __procedure_file_path: str

  facts: List
  conversations: List
  procedures: Dict[str, Dict]

  working_memory: List
  working_memory_capacity: int

  def __init__(self, storage_dir: str = MEMORY_PATH):
    # Create memory folder
    self.__storage_dir = storage_dir
    os.makedirs(self.__storage_dir, exist_ok=True)

    # Memory components files
    self.__fact_file_path = os.path.join(self.__storage_dir, 'facts_semantic.json')
    self.__conversation_file_path = os.path.join(self.__storage_dir, 'converstation_epicsodic.json')
    self.__procedure_file_path = os.path.join(self.__storage_dir, 'procedures.json')

    # Init memory components
    self.facts = self._load_json(self.__fact_file_path, default=[])
    self.conversations = self._load_json(self.__conversation_file_path, default=[])
    self.procedures = self._load_json(self.__procedure_file_path, default={})

    # Init working memory (in RAM)
    self.working_memory = []
    self.working_memory_capacity = 10

  def _load_json[T](self, path: str, default:T) -> T:
    """Load data from JSON file or return default if file does not exist."""

    if not os.path.exists(path):
      return default
    
    try:
      with open(path, 'r') as content:
        return json.load(content)
    except json.JSONDecodeError:
      return default

  def _save_json(self, data: Any, path: str) -> None:
    """Save data into JSON file."""
    with open(path, "w") as content:
      json.dump(data, content, indent=2)

  def __get_timestamp_now(self) -> str :
    return datetime.datetime.now().isoformat()

  def add_fact(self, content: str, category: Optional[str] = None) -> None:
    """Add a fact to semantic memory"""
    timestamp = self.__get_timestamp_now()

    fact = {
      "content": content,
      "category": category,
      "timestamp": timestamp
    }

    self.facts.append(fact)
    self._save_json(self.facts, self.__fact_file_path)

  def add_procedure(self, name: str, steps: List[str], description: Optional[str] = None) -> None:
    timestamp = self.__get_timestamp_now()
    
    procedure = {
      "name": name,
      "steps": steps,
      "description": description,
      "timestamp": timestamp,
      "usage_count": 0
    }

    self.procedures[name] = procedure
    self._save_json(self.procedures, self.__procedure_file_path)

  def add_conversation(
    self, 
    user_message: str,
    agent_response: str,
    metadata: Optional[Dict] = None
  ) -> None:
    timestamp = self.__get_timestamp_now()
    
    conversation = {
      "user_message": user_message,
      "agent_response": agent_response,
      "timestamp": timestamp,
      "metadata": metadata or {}
    }

    self.conversations.append(conversation)
    self._save_json(self.conversations, self.__conversation_file_path)

    # Update working memory
    self.add_working_memory(f"User: {user_message}", importance=1.0)
    self.add_working_memory(f"Agent: {agent_response}", importance=0.9)

  def add_working_memory(self, content: str, importance: float = 1.0) -> None:
    item = {
      "content": content,
      "importance": importance,
      "timestamp": self.__get_timestamp_now()
    }

    self.working_memory.append(item)

    # remove least importance item if list is overflow
    if len(self.working_memory) > self.working_memory_capacity:
      self.working_memory.sort(key=lambda x: (x['importance'], x['timestamp']))
      self.working_memory = self.working_memory[1:] # remove least important

  def search_facts(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Keyword search for fact"""
    query_terms = query.lower().split()
    results = []

    for fact in self.facts:
      content = fact['content'].lower()
      score = sum(1 for term in query_terms if term in content)
      if score > 0:
        results.append((fact, score))

    results.sort(key=lambda x: x[1], reverse=True)
    
    limited_results = [item[0] for item in results[:limit]]
    return limited_results
  
  def search_conversations(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Keyword search for conversation"""

    query_terms = query.lower().split()
    results: List[Tuple[str, int]] = []

    for conversation in self.conversations:
      full_convo = f"{conversation['user_message']} {conversation['agent_response']}".lower()
      score = sum(1 for term in query_terms if term in full_convo)
      
      if score > 0:
        results.append((full_convo, score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in results[:limit]]
  
  def search_procedures(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Search for procedure by keyword matching."""
    query = query.lower()
    results: List[Dict[str, Any]] = []

    for name, procedure in self.procedures.items():
      text = f"{name} {procedure.get('description', '')}".lower()
      if query in text:
        results.append(procedure)

    results.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
    return results[:limit]
  
  def get_recent_conversations(self, count: int = 5) -> List[Dict[str, Any]]:
    if len(self.conversations) <= count:
      return self.conversations
    
    return self.conversations[-count:]
  
  def generate_context_for_llm(self, current_message: str) -> str:
    """Generate a context string for the LLM using relevant memory."""
    # Get working memory
    working_items = sorted(
      self.working_memory,
      key=lambda x: (x['importance'], x['timestamp']),
      reverse=True
    )
    working_item_text = "\n".join(
      [f"- {item['content']}" for item in working_items]
    )

    # Get recent conversations
    recent_conversations = self.get_recent_conversations()
    recent_conversations_text = '\n'.join(
      [
        f"User: {conversation['user_message']}\nAgent: {conversation['agent_response']}" for conversation in recent_conversations
      ]
    )

    # Get relevant facts
    facts = self.search_facts(current_message)
    facts_text = '\n'.join(
      [f"- {fact['content']}" for fact in facts]
    )

    # Get relevant procedures
    procedures = self.search_procedures(current_message)
    procedure_text = ''
    for procedure in procedures:
      step_string = '\n'.join([f'  {i+1}. {step}' for i, step in enumerate(procedure['steps'])])
      procedure_text += f'Procedure: {procedure['name']}\nProcedure Description: {procedure['description']}\nSteps:\n{step_string}\n\n'

    # Combine all context into a string
    context = f'''### Current context (Working Memory):
{working_item_text}

### Recent conversations history:
{recent_conversations_text}

### Relevant facts from memory:
{facts_text}

### Relevant procedures:
{procedure_text}
'''

    return context.strip()

