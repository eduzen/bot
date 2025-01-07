import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache, cached

ALTERNATIVA = "http://www.alternativateatral.com/"


def get_response(url, verify=False):
    try:
        response = requests.get(url, verify=verify)
    except requests.exceptions.ConnectionError:
        return

    return response


@cached(cache=TTLCache(maxsize=1048, ttl=360))
def process_alternativa(response):
    data = response.text
    if not data:
        return False

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("ol", {"class": "ranking scroll"})

    if not data:
        return False

    data = data[0]
    results = []
    for li in data.find_all("li"):
        for a in li.find_all("a", href=True):
            a["href"]
        results.append(li.get_text())

    return results


def parse_alternativa():
    r = get_response(ALTERNATIVA)

    if r and r.status_code == 200:
        return process_alternativa(r)

    else:
        return
