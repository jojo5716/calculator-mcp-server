import os
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

import json

AZURE_API_KEY = os.getenv("AZURE_API_KEY", None)
AZURE_ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o"

client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_API_KEY)
)

# --- Tools ---
def add(a: int, b: int) -> int:
    return a + b

def substract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide por cero.")
    return a / b

TOOLS = {
    "add": add,
    "substract": substract,
    "multiply": multiply,
    "divide": divide
}

TOOL_DESCRIPTIONS = {
    "add": "Suma dos números",
    "substract": "Resta dos números",
    "multiply": "Multiplica dos números",
    "divide": "Divide dos números"
}

async def homepage(request: Request):
    return JSONResponse({"hello": "world"})

async def prompt_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    if not prompt:
        return JSONResponse({"error": "No prompt provided"}, status_code=400)

    # Preparar mensaje para el LLM
    tool_descriptions_text = "\n".join([f"{name}: {desc}" for name, desc in TOOL_DESCRIPTIONS.items()])
    system_message = f"Eres un asistente que puede usar las siguientes herramientas:\n{tool_descriptions_text}\nResponde solo con un JSON indicando qué tools usar y con qué argumentos."
    user_message = f"Prompt: {prompt}\nDevuelve solo un JSON de la forma:\n[{{'tool':'add','args':{{'a':5,'b':3}}}}, ...]"

    try:
        response = client.complete(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=MODEL_NAME,
            temperature=0.0,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        tool_calls = json.loads(content.replace("'", '"'))
    except Exception as e:
        return JSONResponse({"error": f"Error al procesar el prompt: {str(e)}"}, status_code=500)

    results = []
    for call in tool_calls:
        tool_name = call.get("tool")
        args = call.get("args", {})
        tool_func = TOOLS.get(tool_name)
        if not tool_func:
            results.append({"tool": tool_name, "error": "Tool no encontrada"})
            continue
        try:
            result = tool_func(**args)
            results.append({"tool": tool_name, "result": result})
        except Exception as e:
            results.append({"tool": tool_name, "error": str(e)})

    return JSONResponse({"results": results})

app = Starlette(debug=True, routes=[
    Route("/", homepage),
    Route("/prompt", prompt_endpoint, methods=["POST"])
])
