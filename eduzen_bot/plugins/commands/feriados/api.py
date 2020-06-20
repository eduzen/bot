from datetime import datetime
import pytz
import structlog
from typing import List, Dict

import requests

from eduzen_bot.plugins.commands.feriados.aconstants import month_names, FERIADOS_URL

logger = structlog.get_logger(filename=__name__)


def get_feriados(year: int):
    try:
        url = FERIADOS_URL.format(year=year)
        r = requests.get(url, params={"incluir": "opcional"})
        logger.info(f"Retrieved feriados from {r.url}")
    except Exception:
        logger.error("Error requestion feriados", exc_info=True)
        return None
    if r.status_code != 200:
        logger.info(f"Response not 200. {r.status_code} {r.reason}")
        return None

    feriados = r.json()
    return feriados


def filter_feriados(today: datetime, feriados: List) -> List:
    """Returns the future feriados. Filtering past feriados."""
    return [f for f in feriados if (f["mes"] == today.month and f["dia"] >= today.day) or f["mes"] > today.month]


def prettify_feriados(today: datetime, feriados: Dict, compact=False) -> str:
    """Receives a feriado dict of following feriados and pretty prints them.
    [{
        "motivo": "Año Nuevo",
        "tipo": "inamovible",
        "dia": 1,
        "mes": 1,
        "id": "año-nuevo"
    }, {
        "motivo": "Carnaval",
        "tipo": "inamovible",
        "dia": 4,
        "mes": 3,
        "id": "carnaval"
    },
        ...
    ]
    """
    # Get days until next feriado
    nextest_feriado = feriados[0]
    next_feriado_date = datetime(
        day=nextest_feriado["dia"],
        month=nextest_feriado["mes"],
        year=today.year,
        tzinfo=pytz.timezone("America/Argentina/Buenos_Aires"),
    )
    faltan = next_feriado_date - today
    res = (
        f"Faltan *{faltan.days} días* para el próximo feriado"
        f" del *{nextest_feriado['dia']} de {month_names[nextest_feriado['mes']]}*\n\n"
    )

    for feriado in feriados:
        # Improvement. Print mes header before feriados of that month
        fecha = f"{feriado['dia']} de {month_names[feriado['mes']]}"
        res += f"👉 {fecha:<16} -  {feriado['motivo']} | _{feriado['tipo']}_\n"

    return res
