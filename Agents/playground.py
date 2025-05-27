from typing import Generator
from phi.agent import Agent, AgentMemory
from phi.model.groq import Groq
from phi.model.openai import OpenAIChat
from phi.model.ollama import Ollama
from ATP.invoke_intg import invoke
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.memory.db.sqlite import SqliteMemoryDb
from VectorDB.vector import create_vectordb

# import time

# from phi.tools.duckduckgo import DuckDuckGo
# from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv
import os

from phi.playground import Playground, serve_playground_app

load_dotenv()

data_file = os.getenv("VECTOR_DB_DATA")
knowledge_db_location = os.getenv("KNOWLEDGE_AGENT_DB")
agent_team_db_location = os.getenv("AGENT_TEAM_DB")

knowledge_base = create_vectordb(data_file)

# model=Groq(id="llama-3.3-70b-versatile")
model = OpenAIChat(id="gpt-4o")
# model = Ollama(id="phi4-mini")

broad_agent = Agent(
    name="Broad Agent",
    role="For any Broad Integration calls",
    model=model,
    # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    tools=[invoke],
    instructions=[
        "Once you have the integration code with only 1 VBCS role, use the integration code and invoke tool to submit integrations and get the display message from the return value of the tool.",
        "If there are multiple VBCS roles for an integration code, please confirm the VBCS role to be used by the user before doing the tool call",
    ],
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
)

knowledge_agent = Agent(
    name="Knowledge Agent",
    role="Searches the vector DB to get Integration code and VBCS Role",
    model=model,
    # Store the memories and summary in a database
    memory=AgentMemory(
        db=SqliteMemoryDb(table_name="agent_memory", db_file=knowledge_db_location),
        create_user_memories=True,
        create_session_summary=True,
    ),
    storage=SqlAgentStorage(table_name="agent_sessions", db_file=knowledge_db_location),
    # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    knowledge=knowledge_base,
    instructions=[
        "Search the knowledge base to get the integration code and VBCS roles.",
        "If there are multiple VBCS roles for an integration code, please confirm the VBCS role to be used by the user",
    ],
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
)

generic_agent = Agent(
    name="Generic Agent",
    role="Used for user chatting",
    model=model,
    # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    markdown=True,
    instructions=["Have meaningful conversation with user"],
)

agent_team = Agent(
    team=[knowledge_agent, broad_agent, generic_agent],
    model=model,
    # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
    # Store the memories and summary in a database
    memory=AgentMemory(
        db=SqliteMemoryDb(table_name="agent_memory", db_file=agent_team_db_location),
        create_user_memories=True,
        create_session_summary=True,
    ),
    storage=SqlAgentStorage(
        table_name="agent_sessions", db_file=agent_team_db_location
    ),
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    instructions=[
        "Use knowledge_agent to Search the knowledge base to get the integration code and VBCS role. If there are multiple VBCS roles for an integration code, please confirm with the user before calling the broad_agent for tool calls.",
        "Once you have the integration code and 1 VBCS role, use the broad_agent to invoke tool to submit integrations and get the display message from the return value of the tool.",
        "Use generic_agent to have meaningful conversation with user.",
    ],
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
)

app = Playground(agents=[agent_team]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
