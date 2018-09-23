import requests
from bs4 import BeautifulSoup


def get_estado_del_subte(amount=0):
    r = requests.get("http://enelsubte.com/estado/")
    r.encoding = "utf-8"
    msg = "No pudimos conseguir el subte via web"

    if r.status_code != 200:
        return msg

    data = r.text
    if not data:
        return msg

    soup = BeautifulSoup(data, "html.parser")
    table = soup.find_all("table", {"id": "tabla-estado"})

    if not table:
        return msg

    text = []
    for row in table[0].find_all("tr"):
        cols = []
        for cell in row.find_all("td"):
            t = cell.get_text().strip().lower()
            if "desde" in t:
                t = t.replace("desde ", "").strip()[:-5]
            cols.append(t.capitalize())

        print(cols)
        if 'normal' not in cols:
            cols.append(":warning:")

        text.append(" ".join(cols))

        return "\n".join(text)



def get_estado_metrovias_html(amount=0):
    r = requests.get("http://www.metrovias.com.ar/")
    r.encoding = "utf-8"
    msg = "No pudimos conseguir el subte via web"

    if r.status_code != 200:
        return msg

    data = r.text
    if not data:
        return msg

    soup = BeautifulSoup(data, "html.parser")
    div = soup.find_all("div", {"id": "subway-line-status"})
    if not div:
        return msg

    table = div[0].find_all("table")
    if not table:
        return msg

    text = []
    for row in table[0].find_all("tr"):
        for cell in row.find_all("td"):
            text.append(cell.get_text().strip())
            text.append(" ")
        text.append("\n")

    return "".join(text).strip()
