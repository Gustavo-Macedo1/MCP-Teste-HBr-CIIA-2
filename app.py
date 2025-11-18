import streamlit as st
import nest_asyncio
import asyncio
import os
import json
import pandas as pd
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.llms import ChatMessage
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from llama_index.core.memory import Memory
from streamlit_chat_widget import chat_input_widget
from streamlit_extras.bottom_container import bottom

st.title("🤖 Demo - Servidor MCP HBr - CIIA")
st.divider()

# Carrega a API key de um arquivo .env nesse repositório
load_dotenv()
nest_asyncio.apply()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        ChatMessage(role="system", content="Você é um assistente para chamada de ferramentas. Antes de ajudar um usuário, você deve trabalhar com ferramentas para interagir com nossa base de dados."),
        ChatMessage(role="assistant", content="Bem-vindo ao servidor MCP de teste da HBr - CIIA!"),
        ]

if "memory" not in st.session_state:
    memory = Memory.from_defaults(session_id="my_session", token_limit=40000)
    messages = st.session_state["messages"]
    memory.put_messages(messages)

    st.session_state["memory"] = memory

SYSTEM_PROMPT = """
Você é um assistente para chamada de ferramentas.

Antes de ajudar um usuário, você deve trabalhar com ferramentas 
para interagir com nossa base de dados.
"""

async def get_agent():
    api_key = os.getenv('sua_api_key') #"OPENAI_API_KEY do .env"
    llm = OpenAI(model="gpt-4o-mini", api_key=api_key)
    Settings.llm = llm

    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tool = McpToolSpec(client=mcp_client)

    tools = await mcp_tool.to_tool_list_async()

    agent = FunctionAgent(
        name="Agente HBr",
        description="Um agente que trabalha com a base de dados do tomógrafo.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )

    agent_context = Context(agent)
    return agent, agent_context

async def handle_user_message(message_content, agent, agent_context, verbose=False):
    memory = st.session_state['memory']
    chat_history = memory.get()
    handler = agent.run(message_content, ctx=agent_context, chat_history=chat_history)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned {event.tool_output}")
    response = await handler
    return str(response)

def run_async(coro):
    loop = asyncio.get_event_loop()
    task = loop.create_task(coro)
    loop.run_until_complete(task)
    return task.result()


container = st.container(height=570, border=True)


# Mensagem de boas-vindas
if "started" not in st.session_state:
    container.chat_message("assistant").write("Bem-vindo ao servidor MCP de teste da HBr - CIIA!")
    st.session_state["started"] = True
else:
    # Resgate das mensagens até o momento
    current_memo = st.session_state["memory"]
    msgs = current_memo.get()
    for msg in msgs[1:]:
        if msg.role == 'user':
            container.chat_message("user").write(msg.content)
        else:
            container.chat_message("assistant").write(msg.content)

# Chat
prompt = st.chat_input("Digite algo...", accept_file=True, file_type=['jpg', 'csv'])

if prompt and prompt.text:
    container.chat_message("user").write(prompt.text)
    agent, agent_ctx = run_async(get_agent())
    response = run_async(handle_user_message(prompt.text, agent, agent_ctx))

    try:
        print("ENTREI AQUI")
        response_json = json.loads(response)
        print(response_json)
        if isinstance(response_json, dict) and response_json.get("type") == "bar_chart":
            df = pd.DataFrame({
                response_json["x_label"]: response_json["x"],
                response_json["y_label"]: response_json["y"]
            })
            container.chat_message("assistant").bar_chart(df, 
                x=response_json["x_label"], 
                y=response_json["y_label"]
            )
        else:
            container.chat_message("assistant").write(response)
    except json.JSONDecodeError:
        container.chat_message("assistant").write(response)

    # container.chat_message("assistant").write(response)

    new_msgs = []
    new_msgs.append(ChatMessage(role="user", content=prompt.text))
    new_msgs.append(ChatMessage(role="assistant", content=response))

    memory = st.session_state['memory']
    memory.put_messages(new_msgs)
    st.session_state['memory'] = memory

if prompt and prompt["files"]:
    st.image(prompt["files"][0])


# my_input = chat_input_widget()

# if my_input:
#         if "text" in my_input:
#             user_text = my_input["text"]
#         elif "audioFile" in my_input:
#             audio_bytes = bytes(my_input["audioFile"])
#             st.audio(audio_bytes)