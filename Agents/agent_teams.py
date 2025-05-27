#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oracle ATP execution file"""
###############################################################################
# Project - BroadieLLM
# Filename - invoke_intg.py
# Arguments - None
# Created By - Vivek Salgia
# Creation Date - 04/29/2025
# Reviewed By -
# Reviewed Date -
# Change logs -
# Version   Date         Type   Changed By                  Comments
# =======   ============ ====   ==============  ===============================
# 1.0       29-Apr-2025   I     Vivek Salgia    Initial Creation
###############################################################################


from typing import Generator
from phi.agent import Agent, AgentMemory
from phi.model.groq import Groq
from phi.model.openai import OpenAIChat
from phi.model.ollama import Ollama
from ATP.invoke_intg import invoke
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.memory.db.sqlite import SqliteMemoryDb

# import time

# from phi.tools.duckduckgo import DuckDuckGo
# from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv
import os


def invoke_agents(
    question: str, knowledge_base: str, load_kb: str, sessionid: str
) -> Generator[str, None, None]:

    load_dotenv()

    knowledge_db_location = os.getenv("KNOWLEDGE_AGENT_DB")
    agent_team_db_location = os.getenv("AGENT_TEAM_DB")

    # model=Groq(id="llama-3.3-70b-versatile")
    # model = OpenAIChat(id="gpt-4o")
    # model = Ollama(id="phi4-mini")
    model = Ollama(id="mistral-small3.1:latest")

    broad_agent = Agent(
        name="Broad Agent",
        role="For any Broad Integration calls",
        model=model,
        session_id=sessionid,
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
        session_id=sessionid,
        # Store the memories and summary in a database
        memory=AgentMemory(
            db=SqliteMemoryDb(table_name="agent_memory", db_file=knowledge_db_location),
            create_user_memories=True,
            create_session_summary=True,
        ),
        storage=SqlAgentStorage(
            table_name="agent_sessions", db_file=knowledge_db_location
        ),
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
        session_id=sessionid,
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
        session_id=sessionid,
        # model=OpenAIChat(id="gpt-4o"),
        # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
        # Store the memories and summary in a database
        memory=AgentMemory(
            db=SqliteMemoryDb(
                table_name="agent_memory", db_file=agent_team_db_location
            ),
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
            "Once you have the integration code and 1 VBCS role, transfer the task to broad_agent to invoke tool to submit integrations and get the display message from the return value of the tool.",
            "Use generic_agent to have meaningful conversation with user.",
        ],
        show_tool_calls=True,
        markdown=True,
        # debug_mode=True,
    )

    """agent_team.print_response(
        # "I want to get procurement data from keyusa to sap using procurement role",
        # "Please help me send requisition from Jaggaer to SAP",
        question,
        stream=False,
    )"""

    for delta in agent_team.run(question):
        # print(delta)
        # time.sleep(1)
        if delta[0] == "messages":
            # print(delta[1])
            for aresp in delta[1]:
                # if all(
                #     aresp.role not in values
                #     for values in ["system", "user", "developer"]
                # ):
                #     if aresp.content is not None:
                #         # print(aresp.content)
                #         yield aresp.content
                # yield delta[1][-1].content
                if aresp.role == "tool":
                    retdict = {
                        "role": "tool",
                        "toolname": aresp.tool_name,
                        "toolargs": aresp.tool_args,
                        "content": "",
                    }
                    # yield str(retdict)
                elif aresp.role == "assistant":
                    retdict = {
                        "role": "assistant",
                        "toolname": aresp.tool_name,
                        "toolargs": aresp.tool_args,
                        "content": aresp.content,
                    }
                    yield str(retdict.get("content"))

    # return response


if __name__ == "__main__":
    invoke_agents("Hi, How are you?")
