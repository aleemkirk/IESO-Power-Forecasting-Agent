"""
LangGraph Agent Orchestrator for IESO Power Forecasting

This module implements the main agent loop using LangGraph.
Phase 1: Basic agent with simple tool calling.
"""

import os
from typing import TypedDict, Annotated, List
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from loguru import logger

from .tools import ALL_TOOLS
from .prompts import SYSTEM_PROMPT


class AgentState(TypedDict):
    """State definition for the agent."""
    messages: Annotated[List, add_messages]
    goal: str
    iteration: int


class IESOForecastAgent:
    """Main agent orchestrator using LangGraph."""

    def __init__(self, model_name: str = "llama3.1", temperature: float = 0.1):
        """Initialize the agent.

        Args:
            model_name: Ollama model name to use
            temperature: LLM temperature (lower = more deterministic)
        """
        self.model_name = model_name
        self.temperature = temperature

        # Initialize the LLM
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")
        )

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)

        # Build the graph
        self.graph = self._build_graph()
        logger.info(f"Agent initialized with model: {model_name}")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine.

        Returns:
            Compiled LangGraph workflow
        """
        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(ALL_TOOLS))

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        # Compile the graph
        return workflow.compile()

    def _call_model(self, state: AgentState) -> AgentState:
        """Call the LLM with current state.

        Args:
            state: Current agent state

        Returns:
            Updated state with LLM response
        """
        messages = state["messages"]

        # Add system message if this is the first iteration
        if len(messages) == 1:
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        # Call the LLM
        response = self.llm_with_tools.invoke(messages)

        # Update iteration count
        iteration = state.get("iteration", 0) + 1

        return {
            "messages": [response],
            "iteration": iteration
        }

    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue or end.

        Args:
            state: Current agent state

        Returns:
            "continue" if tool calls are needed, "end" otherwise
        """
        last_message = state["messages"][-1]

        # If there are tool calls, continue
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"

        # Otherwise, end
        return "end"

    def run(self, user_input: str, verbose: bool = True) -> str:
        """Run the agent with a user input.

        Args:
            user_input: User's question or command
            verbose: Whether to print debug information

        Returns:
            Agent's response as a string
        """
        logger.info(f"Processing user input: {user_input}")

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "goal": user_input,
            "iteration": 0
        }

        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)

            # Extract the final response
            last_message = final_state["messages"][-1]

            if verbose:
                logger.info(f"Agent completed in {final_state['iteration']} iterations")

            # Return the content of the last message
            if hasattr(last_message, "content"):
                return last_message.content
            else:
                return str(last_message)

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return f"I encountered an error: {str(e)}"

    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("\n" + "=" * 60)
        print("IESO Power Forecasting Agent - Interactive Mode")
        print("=" * 60)
        print("\nPhase 1: Basic Tool Testing")
        print("Commands: 'exit' or 'quit' to stop\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                # Run the agent
                response = self.run(user_input, verbose=True)
                print(f"\nAgent: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\nError: {e}")
