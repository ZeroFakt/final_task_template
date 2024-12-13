import requests
from app.config import Config
from functools import lru_cache
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=100)
def search_links(query, max_results=5):
    if not Config.GOOGLE_API_KEY or not Config.GOOGLE_CX:
        return {"error": "API ключи Google Search не настроены"}
    
    params = {
        "key": Config.GOOGLE_API_KEY,
        "cx": Config.GOOGLE_CX,
        "q": f"{query} site:csu.ru",  # Изменен формат запроса
        "num": max_results,
        "hl": "ru"  # Добавлен параметр языка
    }
    
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1", 
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Поисковый запрос: {query}")
        
        if 'items' not in data:
            # Попробуем прямой поиск по сайту ЧелГУ
            direct_results = direct_site_search(query)
            if direct_results:
                return direct_results
            return []
        
        results = []
        for item in data['items'][:max_results]:
            result = {
                "title": item.get("title", "").replace("- Челябинский государственный университет", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            }
            results.append(result)
        
        return results
        
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса: {str(e)}")
        # Пробуем прямой поиск при ошибке API
        return direct_site_search(query)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return {"error": f"Ошибка поиска: {str(e)}"}

def direct_site_search(query, max_results=5):
    """Прямой поиск по сайту ЧелГУ"""
    try:
        base_url = "https://www.csu.ru"
        response = requests.get(f"{base_url}/search/", params={"q": query}, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Поиск результатов на странице
        search_results = soup.find_all('a', href=True)
        for link in search_results[:max_results]:
            if not link.get('href').startswith(('http', '#', 'javascript')):
                full_url = urljoin(base_url, link.get('href'))
                title = link.get_text(strip=True)
                if title and len(title) > 5:  # Фильтруем короткие заголовки
                    results.append({
                        "title": title,
                        "link": full_url,
                        "snippet": ""
                    })
        
        return results[:max_results]
        
    except Exception as e:
        logger.error(f"Ошибка прямого поиска: {str(e)}")
        return []
