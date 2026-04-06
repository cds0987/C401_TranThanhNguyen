from src.tools.get_product_detail import get_product_detail
from src.tools.compare_product import compare_product
from src.tools.check_inventory import check_inventory  # thêm
from src.core.azure_provider import AzureOpenAIProvider
from src.agent.agent import ReActAgent
from dotenv import load_dotenv
import os
load_dotenv()
# --- Adapter: wrap OpenAI tool schema into ReAct format ---
def openai_tools_to_react(openai_tools: list, fn_map: dict) -> list:
    """
    openai_tools : your existing `tools` list (OpenAI JSON schema)
    fn_map       : { "tool_name": callable }
    """
    react_tools = []
    for t in openai_tools:
        fn_def = t["function"]
        name = fn_def["name"]
        react_tools.append({
            "name": name,
            "description": fn_def["description"],
            "parameters": fn_def["parameters"],   # kept for reference
            "fn": fn_map[name]                     # actual Python callable
        })
    return react_tools


openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_product_detail",
            "description": "Xem thông tin chi tiết một sản phẩm theo ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "ID sản phẩm. Ví dụ: 'p001'"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_product",
            "description": "So sánh nhiều sản phẩm cùng lúc. Input: danh sách product_id cách nhau bởi dấu phẩy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_list": {"type": "string", "description": "Ví dụ: 'p001,p003'"}
                },
                "required": ["product_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Kiểm tra số lượng tồn kho của một sản phẩm. Input: product_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "ID sản phẩm. Ví dụ: 'p001'"}
                },
                "required": ["product_id"]
            }
        }
    }
]
llm = AzureOpenAIProvider(
    model_name="gpt-4o",
    api_key= os.getenv('GithubAPI'),
    base_url="https://models.inference.ai.azure.com/"
)
fn_map = {
    "get_product_detail": get_product_detail,
    "compare_product": compare_product,
    "check_inventory": check_inventory,  # thêm
}

react_tools = openai_tools_to_react(openai_tools, fn_map)
agent = ReActAgent(llm=llm, tools=react_tools, max_steps=3)

# Tool 1
agent.run("Cho tôi thông tin sản phẩm p001")

# Tool 2
agent.run("So sánh sản phẩm p001 và p003")

# Tool 3
agent.run("Kiểm tra tồn kho sản phẩm p002")