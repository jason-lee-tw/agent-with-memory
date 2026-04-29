import os
from dotenv import load_dotenv
from agents.claude_agent import ClaudeAgent

def prepare_knowledge(agent: ClaudeAgent) -> None:
    agent.learn_fact(
        'Python is a high level programming language known for its readability.',
        'programming'
    )
    agent.learn_fact(
        'Memory system in AI agents are crutial for continuity and personalization.',
        'AI'
    )
    agent.learn_procedure(
        name="Create a simple AI agent with memory",
        steps=[
            "Initialize memory storage (file, database, etc.).",
            "Create functions to add facts into semantic memory.",
            "Create functions to add past conversation history in episodic memory.",
            "Create functions to retrieve relevant memory based on context.",
            "Connect memory system to LLM like OpenAI ChatGPT",
            "Implement a query function that includes memory context in prompts.",
            "Add memory updating after each interaction."
        ],
        description="Steps to create an AI agent with memory capabilities."
    )

def main():
    load_dotenv()

    # Init AI agent
    api_key = os.getenv("ANTHROPIC_API_KEY")
    agent = ClaudeAgent(
        api_key=api_key,
    )

    # Init memory
    prepare_knowledge(agent)

    # Prompt for quit
    print('AI Assistant with Memory initialized!\nType `exit` to quit.')
    print('-' * 50)

    # Execution Loop
    while (True):
        user_input = input('\nYou: ')
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nAssistant: Bye bye! Nice to talk with you.")
            break

        result = agent.query(user_input)
        print(f"\nAssistant:\n```\n{result}\n```")


if __name__ == "__main__":
    main()
