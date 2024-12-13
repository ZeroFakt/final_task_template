import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def fetch_news():
    options = Options()
    options.add_argument('--headless=new')  # Обновленный синтаксис для headless режима
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')  # Добавляем для стабильности
    
    try:
        # Добавляем обработку таймаута
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)  # Устанавливаем таймаут
        
        driver.get("https://www.csu.ru/news")

        # Получение рендеренного HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Извлечение заголовков и ссылок
        news_data = []
        for short_div in soup.find_all("div", class_="short")[:3]:  # Берем только первые 3 блока
            a_tag = short_div.find("a", href=True)
            title = short_div.find("h3").get_text(strip=True) if short_div.find("h3") else "Без названия"
            if a_tag:
                href = a_tag['href']
                full_url = href if href.startswith("http") else f"https://www.csu.ru{href}"
                news_data.append({"title": title, "url": full_url})

        return news_data

    except Exception as e:
        print(f"Error fetching news: {e}")
        return []  # Возвращаем пустой список в случае ошибки

    finally:
        try:
            driver.quit()
        except:
            pass
