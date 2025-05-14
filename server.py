import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from tools import track_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PlaywrightMCP")

# Create an MCP server
mcp = FastMCP("Playwright MCP")


@mcp.tool()
async def obtener_request_from_url(url: str, headless: bool = True, timeout: int = 30000, accept_cookies: bool = True, cookies_selector: str = "#cookies-accept-full > a") -> list:
    """
    Devuelve le listado de recursos cargados en la URL especificada, puede aceptar cookies automáticamente.
    Args:
        url (str): URL a visitar
        headless (bool): Si se debe ejecutar el navegador en modo headless
        timeout (int): Tiempo máximo de espera en milisegundos  
        accept_cookies (bool): Si se deben aceptar las cookies automáticamente
        cookies_selector (str): Selector CSS del botón para aceptar cookies
    Returns:
        list: Lista de diccionarios con información sobre cada recurso cargado
    """
    
    
    
    # Ejecutar el rastreador de recursos
    resources = asyncio.run(track_resources(
        url, 
        headless, 
        timeout, 
        accept_cookies,
        cookies_selector
    ))
    return resources
    

if __name__ == "__main__":
    mcp.run(transport="stdio")
