import asyncio
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from config import CSS_SELECTOR, REQUIRED_KEYS, CATEGORIAS_URLS
from utils.data_utils import (
    save_teams_to_csv, 
    save_failed_urls, 
    load_failed_urls, 
    update_failed_urls,
    save_to_mongodb
)
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
)

load_dotenv()


async def crawl_standings(urls_to_process=None):
    """
    Main function to crawl hockey standings from the website.
    
    Args:
        urls_to_process: List of (categoria, url) tuples to process. If None, uses all URLs.
    """
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "hockey_standings_session"

    all_teams = []
    failed_urls = []
    successful_urls = []  # Track successful URLs for retry mode

    # Use provided URLs or all URLs from config
    urls = urls_to_process if urls_to_process is not None else CATEGORIAS_URLS

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, (categoria, url) in enumerate(urls):
            print(f"\n🔎 Procesando categoría: {categoria} ({i+1}/{len(urls)})")
            teams, no_results_found = await fetch_and_process_page(
                crawler=crawler,
                base_url=url,
                css_selector=CSS_SELECTOR,
                llm_strategy=llm_strategy,
                session_id=session_id,
                required_keys=REQUIRED_KEYS,
                categoria=categoria,
            )

            if not teams:
                print(f"⚠️ No se extrajeron datos para {categoria}.")
                failed_urls.append({"categoria": categoria, "url": url})
            else:
                print(f"✅ Se extrajeron {len(teams)} equipos para {categoria}.")
                all_teams.extend(teams)
                # Save teams for this category immediately
                save_teams_to_csv(teams, categoria)
                # Save to MongoDB
                save_to_mongodb(teams, categoria)
                # Track successful URL if in retry mode
                if urls_to_process is not None:
                    successful_urls.append({"categoria": categoria, "url": url})

            # Aumentamos el tiempo de espera entre categorías
            if i < len(urls) - 1:  # No esperar después de la última categoría
                wait_time = 30  # 30 segundos entre categorías
                print(f"💤 Esperando {wait_time} segundos antes de la siguiente categoría...")
                await asyncio.sleep(wait_time)

    if not all_teams:
        print("⚠️ No se extrajeron datos para ninguna categoría.")
    else:
        print(f"\n📄 Proceso completado. Se han guardado las tablas de posiciones para cada categoría en la carpeta 'output' y en MongoDB.")
        
        # Mostrar el uso de tokens
        print("\n📊 Uso de tokens:")
        llm_strategy.show_usage()

    # Save failed URLs if any
    if failed_urls:
        save_failed_urls(failed_urls)
        print("\n💡 Para reintentar solo las URLs fallidas, ejecuta el script con el argumento --retry")
    
    # Update failed URLs list if in retry mode and we have successful URLs
    if urls_to_process is not None and successful_urls:
        update_failed_urls(successful_urls)


async def main():
    """
    Entry point of the script.
    """
    import sys
    
    if "--retry" in sys.argv:
        failed_urls = load_failed_urls()
        if not failed_urls:
            print("No hay URLs fallidas para reintentar.")
            return
        
        print(f"\n🔄 Reintentando {len(failed_urls)} URLs fallidas...")
        urls_to_process = [(item["categoria"], item["url"]) for item in failed_urls]
        await crawl_standings(urls_to_process)
    else:
        await crawl_standings()


if __name__ == "__main__":
    asyncio.run(main())
