
from datetime import datetime
from playwright.async_api import async_playwright

async def track_resources(url, headless=True, timeout=30000, accept_cookies=True, cookies_selector="#cookies-accept-full > a"):
    """
    Visita la URL especificada y registra todos los recursos cargados.
    
    Args:
        url (str): URL a visitar
        headless (bool): Si se debe ejecutar el navegador en modo headless
        timeout (int): Tiempo máximo de espera en milisegundos
        accept_cookies (bool): Si se deben aceptar las cookies automáticamente
        cookies_selector (str): Selector CSS del botón para aceptar cookies
        
    Returns:
        list: Lista de diccionarios con información sobre cada recurso cargado
    """
    resources = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        
        # Crear una página nueva sin capturar aún los recursos (para aceptar cookies primero)
        page = await context.new_page()
        
        try:
            # Visitar la URL inicialmente
            print(f"Visitando {url}...")
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            
            # Aceptar cookies si está habilitado
            if accept_cookies:
                try:
                    print(f"Buscando y aceptando cookies con selector: {cookies_selector}...")
                    # Intentar hacer clic en el botón de aceptar cookies
                    await page.click(cookies_selector, timeout=5000)
                    print("Cookies aceptadas exitosamente")
                    # Esperar a que se procese la aceptación
                    await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"No se pudo aceptar las cookies: {e}")
            
            # Cerrar la página inicial y crear una nueva para rastrear los recursos
            await page.close()
            
            # Crear una nueva página con la captura de solicitudes habilitada
            page = await context.new_page()
            
            # Escuchar todos los eventos de solicitud para la nueva página
            page.on("request", lambda request: resources.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'is_navigation_request': request.is_navigation_request(),
                'timestamp': datetime.now().isoformat(),
            }))
            
            # Visitar la URL nuevamente para capturar todos los recursos post-cookies
            print("Volviendo a cargar la página para capturar recursos...")
            response = await page.goto(url, timeout=timeout, wait_until="networkidle")
            
            # Esperar un poco más para cargas dinámicas
            await page.wait_for_timeout(2000)
            
            # Desplazamiento para activar cargas adicionales
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Obtener información del documento actual
            title = await page.title()
            print(f"Título de la página: {title}")
            print(f"Total de recursos capturados: {len(resources)}")
            
        except Exception as e:
            print(f"Error al cargar la página: {e}")
        finally:
            await browser.close()
            
    return resources