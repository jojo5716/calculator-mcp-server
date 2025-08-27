from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request
from mcp.server.fastmcp import FastMCP

server = FastMCP("SSE Platzi")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@server.tool()
def substract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

@server.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@server.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def prompt_endpoint(request: Request):
    """
    Recibe JSON: { "prompt": "Suma 2 + 3" }
    """
    data = await request.json()
    prompt = data.get("prompt", "")
    if not prompt:
        return JSONResponse({"error": "No prompt provided"}, status_code=400)

    try:
        # Ejecutamos el prompt usando FastMCP
        result = await server.run_prompt(prompt)
        return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route("/prompt", prompt_endpoint, methods=["POST"]),
])