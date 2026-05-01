from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from tools import scan_cargo, forecast_capacity, prioritize_operations, assess_risk, fleet_efficiency, inspection_alerts
import os

os.environ["GROQ_API_KEY"] = "Your API key here "

def create_agent():
    llm = ChatGroq(
        api_key=os.environ["GROQ_API_KEY"],
        model_name="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=800
    )

    tools = [scan_cargo, forecast_capacity, prioritize_operations,
             assess_risk, fleet_efficiency, inspection_alerts]

    prompt = hub.pull("hwchase17/react")

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
        max_execution_time=60,
        return_intermediate_steps=True
    )

    return agent_executor