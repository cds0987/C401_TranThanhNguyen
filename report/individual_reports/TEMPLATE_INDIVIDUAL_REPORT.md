# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [TranThanhNguyen]
- **Student ID**: [2A202600311]
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

I implemented the tool layer and the action parser that connects LLM output to real tool execution.

- **Modules Implemented**:
  - `src/tools/product_tool.py` — `get_product_detail(product_id)`
  - `src/tools/inventory_tool.py` — `check_inventory(product_id)`
  - `src/tools/compare_tool.py` — `compare_product(id1, id2)`
  - `src/agent/parser.py` — parses `Action: tool_name(args)` from raw LLM text

- **Code Highlight** — the action parser:
```python
import re

def parse_action(response: str):
    match = re.search(r"Action:\s*(\w+)\((.+?)\)", response)
    if not match:
        return None, None
    tool_name = match.group(1)
    args = match.group(2).strip()
    return tool_name, args
```

- **Documentation**: The ReAct loop calls `parse_action(llm_response)` after each LLM call. If a valid action is found, it dispatches to the matching tool function and appends the result as an `Observation:` block for the next iteration. If `parse_action` returns `None` (no valid Action line found), the loop exits — which turned out to be the root cause of the hallucination bug described below.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: On the query "So sánh sản phẩm p001 và p003", the agent produced a confident Final Answer with `steps: 0` — meaning it never actually called any tool. Worse, it hallucinated p001 as "Laptop Dell XPS 13" when all prior confirmed runs identified p001 as "iPhone 15 128GB."

- **Log Evidence** (`logs/2026-04-06.log`, timestamp 10:50:08–10:50:11):
```json
{"event": "LLM_RESPONSE", "data": {"step": 0,
  "response": "Action: compare_product(p001,p003)\nObservation: {\"p001\": {\"name\": \"Laptop Dell XPS 13\"...}}\nFinal Answer: ..."}}
{"event": "AGENT_END", "data": {"steps": 0, ...}}
```
  No `TOOL_CALL` or `TOOL_RESULT` events appear between these two lines.

- **Diagnosis**: Three compounding causes: (1) No few-shot example for `compare_product` in the system prompt — the model had never seen a real tool call flow for this tool. (2) The parser's regex expected a plain `Action:` line, but the model embedded it inside a larger block, so `parse_action()` returned `None` and the loop exited at step 0. (3) No guard existed against a `steps=0` exit — the agent accepted the self-contained hallucinated answer silently.

- **Solution**: Added a few-shot example for `compare_product` to the system prompt. Added a post-loop check that raises a warning and retries when `steps == 0` but the query referenced multiple entities. Added an explicit system prompt constraint: *"Never generate an Observation yourself. Only write Final Answer after receiving a real Observation from the environment."*

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought:` block forced the model to identify the correct tool before acting — in every successful run, it explicitly named `get_product_detail` or `check_inventory` in its thought, which grounded the action step. A chatbot skips this planning entirely and answers from training data, which is stale for real-time fields like price and stock.

2. **Reliability — when the agent was worse**: The compare query was the clearest case. The agent produced a confident, well-formatted, fully fabricated answer — more convincing-looking than a chatbot's hedged "I'm not sure." The structured ReAct output made the hallucination harder to detect at a glance. For queries where the model has no real tool to call or the tool spec is ambiguous, the agent can be *more* dangerous than a simple chatbot.

3. **Observation**: In the inventory check run, the raw observation `"iPhone 15 256GB: Hết hàng"` directly controlled the Final Answer with no added information — the agent did not speculate beyond what the tool returned. This shows that when the tool call actually fires and returns clean data, grounding via observation is highly effective at preventing hallucination.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Use an async task queue (e.g., Celery + Redis) for tool calls so concurrent sessions don't block each other. Add a tool registry backed by a vector DB so the agent can select from 50+ tools via semantic search rather than enumerating all of them in the prompt.

- **Safety**: Deploy a supervisor LLM that cross-checks the Final Answer against the raw TOOL_RESULT — if they contradict, reject and retry. Enforce a hard cap of 5 loop iterations per session. Validate all tool arguments against a schema before dispatching.

- **Performance**: Cache `get_product_detail` results with a short TTL (60s) — 4 identical p001 lookups appeared in today's log and could have been served from cache after the first call. Stream the LLM response and begin parsing the `Action:` line as it arrives to reduce perceived latency.