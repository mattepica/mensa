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

days_text = [
   "Domenica",
   "Lunedì",
   "Martedì"
   "Mercoledì",
   "Giovedì",
   "Venerdì",
   "Sabato"
]

#
# menu = {
#   'primi': [
#     { 'nome': 'nome1', 'allergeni': ['glutine'], 'kcal': 300 },
#     { 'nome': 'nome2', 'allergeni': ['latte'],   'kcal': 200 },
#   ],
#   'secondi':  [],
#   'contorni': [],
# }
#

copyright = "@menumensaerzelli"

def get_menu(day_of_week):
  response = requests.get(f"{base_url}/menu")
  response.raise_for_status()
  html = response.text
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find('table', { "class": "tabella_menu_settimanale" })

  menu = {
    'primi':    {},
    'secondi':  {},
    'contorni': {},
  }
  return menu

def render_piatto(piatto):
  allergeni_emoji = {
    'latte': emojis['glass_of_milk'],
    'glutine': emojis['ear_of_rice']
  }
  allergeni = "".join(map(lambda x: allergeni_emoji[x], piatto['allergeni']))
  return f"  {emojis['white_small_square']} <i>{piatto['nome']} {allergeni} [{piatto['kcal']} kcal]</i>"

def render_piatti(piatti):
  return "\n".join(map(render_piatto, piatti))

def render_message():
  dt = datetime.now()
  day = dt.weekday()
  data = dt.strftime('%d/%m/%Y')
  menu = get_menu(day)

  msg = f'''\
{emojis['white_right_pointing_backhand_index']} Menù <b>{days_text[day]}</b> {data}

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
      response = requests.post(url_tg, json={'chat_id': chat_id, 'parse_mode': "html", 'text':  msg})
      response.raise_for_status()
  except requests.HTTPError:
      print(response.json())

if __name__ == "__main__":
    import sys
    publish_message_to_telegram(sys.argv[1], sys.argv[2], render_message())
