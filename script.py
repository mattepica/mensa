from bs4 import BeautifulSoup
from datetime import datetime
import requests

base_url = "https://erzelli.alpiristorazione.cloud"

emojis = {
    'glass_of_milk': '\U0001F95B',
    'ear_of_rice': '\U0001F33E',
    'white_small_square': '\U000025AB',
    'broccoli': '\U0001F966',
    'curry_and_rice': '\U0001F35B',
    'spaghetti': '\U0001F35D',
    'white_right_pointing_backhand_index': '\U0001F449'
}

copyright = "@menumensaerzelli"


def get_info(piatto):
    info = {}
    try:
        response = requests.get(piatto.find("a")['href'])
        response.raise_for_status()
    except requests.HTTPError as e:
        print(e)
        return info
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    allergeni = []
    if f"{base_url}/images/allergeni/glutine.png" in html:
        allergeni.append('glutine')
    if f"{base_url}/images/allergeni/latte.png" in html:
        allergeni.append('latte')
    info['allergeni'] = allergeni
    try:
        kcal = soup.find("div", {"class": "div_gda"}).find(
            "p", {"class": "valore_gda"}).decode_contents()
        if not kcal:
            raise Exception("Kcal not found")
        kcal = kcal.split(">")[1]
        info['kcal'] = kcal.split()[0]
    except Exception as e:
        print(e)
    return info


def get_piatti(piatti_table):
    piatti = piatti_table.find_all("p")[:3]
    return [{'nome': piatto.getText().strip()} | get_info(piatto)
            for piatto in piatti]


def get_menu(day_of_week):
    response = requests.get(f"{base_url}/menu")
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table', {"class": "tabella_menu_settimanale"})

    menu = {
        'giorno': table.find_all('th', {'class': 'giorno_della_settimana'})[day_of_week - 1].getText().lower(),
        'primi': get_piatti(table.find('td', {"data-giorno": day_of_week, "data-tipo-piatto": 1})),
        'secondi': get_piatti(table.find('td', {"data-giorno": day_of_week, "data-tipo-piatto": 2})),
        'contorni': get_piatti(table.find('td', {"data-giorno": day_of_week, "data-tipo-piatto": 4})),
    }
    return menu


def render_piatto(piatto):
    allergeni_emoji = {
        'latte': emojis['glass_of_milk'],
        'glutine': emojis['ear_of_rice']
    }
    allergeni = "".join(
        map(lambda x: allergeni_emoji[x], piatto['allergeni']))
    return f"  {emojis['white_small_square']} <i>{piatto['nome']} {allergeni} [{piatto['kcal']} kcal]</i>"


def render_piatti(piatti):
    return "\n".join(map(render_piatto, piatti))


def render_message():
    dt = datetime.now()
    day = dt.weekday() + 1
    data = dt.strftime('%d/%m/%Y')
    menu = get_menu(day)

    msg = f'''\
{emojis['white_right_pointing_backhand_index']} Menù <b>{menu['giorno']}</b> {data}

<b><u>Primi</u></b> {emojis['spaghetti']}
{render_piatti(menu['primi'])}

<b><u>Secondi</u></b> {emojis['curry_and_rice']}
{render_piatti(menu['secondi'])}

<b><u>Contorni</u></b> {emojis['broccoli']}
{render_piatti(menu['contorni'])}

{copyright}'''

    return msg


def publish_message_to_telegram(bot_name, chat_id, msg):
    url_tg = f"https://api.telegram.org/bot{bot_name}/sendMessage"
    try:
        response = requests.post(
            url_tg,
            json={
                'chat_id': chat_id,
                'parse_mode': "html",
                'text': msg})
        response.raise_for_status()
    except requests.HTTPError:
        print(response.json())


if __name__ == "__main__":
    import sys
    publish_message_to_telegram(sys.argv[1], sys.argv[2], render_message())
