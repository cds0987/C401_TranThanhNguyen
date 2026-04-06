from fastapi import FastAPI
from src.tools.buildagent import ReActAgent, react_tools, llm

app = FastAPI()

# init agent (tránh tạo lại mỗi request)
agent = ReActAgent(llm=llm, tools=react_tools, max_steps=3)


@app.get("/")
def home():
    return {"message": "Agent API is running 🚀"}


@app.post("/chat")
def chat(query: str):
    result = agent.run(query)
    return {"response": result}