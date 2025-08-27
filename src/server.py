from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

server = FastMCP("SSE Platzi")

app = Starlette(
    routes=[
        Mount('/', app=server.run_sse_async()),
    ]
)

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
