from bs4 import BeautifulSoup


def strip_html_tags(html_text):
    """Удаляет HTML-теги и возвращает чистый текст."""
    return BeautifulSoup(html_text, "html.parser").get_text()
