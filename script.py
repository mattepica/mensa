from datetime import datetime
import jmespath
import requests

base_url = "https://alpisanmarco.itchef.it/ITChefAppWS/api/utente"

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
   "Lunedì",
   "Martedì",
   "Mercoledì",
   "Giovedì",
   "Venerdì",
   "Sabato",
   "Domenica"
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

def raw_query(filter: str) -> str:
  return f'[?descrizione==`{filter}`].piatti[:3].{{nome: descrizione, kcal: valoriNutrizionali.KCal, allergeni: elencoAllergeni}}'

def get_menu():

  menu = {}

  with requests.Session() as s:
    response = s.post(f'{base_url}/ExportMenu/C82DC5EE-FC90-42F0-B6DD-E95D7C33283A', json="{}")
    response.raise_for_status()

    portate = response.json()["menu"][0]["portate"] # Taking for granted the fact that there's only one menu

    portate_dict = {
      "Primo":"primi",
      "Secondo":"secondi",
      "Contorno":"contorni"
    }
    
    for piatto,nome in portate_dict.items():
      expression = jmespath.compile(raw_query(piatto))
      menu[nome] = expression.search(portate)[0]
     
  return menu

def render_piatto(piatto):
  allergeni_emoji = {
    'latte': emojis['glass_of_milk'],
    'glutine': emojis['ear_of_rice']
  }

  allergeni = ''
  if piatto.get('allergeni',False):
    allergeni = "".join(map(lambda x: f" {allergeni_emoji.get(x,'')}" if x in piatto["allergeni"] else '',allergeni_emoji.keys()))

  return f"  {emojis['white_small_square']} <i>{piatto['nome']}{allergeni} [{piatto['kcal']:.0f} kcal]</i>"

def render_piatti(piatti):
  return "\n".join(map(render_piatto, piatti))

def render_message(dt=None):
  if not dt:
    dt = datetime.now()
  day = dt.weekday()
  data = dt.strftime('%d/%m/%Y')

  menu = get_menu()

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
    import os
    import sys
    vars = [
       'BOT_TOKEN',
       'CHANNEL_ID',
    ]

    if len(sys.argv) < 1+len(vars):
       params = dict(os.environ.items())
    else:
       params = dict(map(lambda x,y : (x,y) , vars,sys.argv[1:]))

    publish_message_to_telegram(params['BOT_TOKEN'], params['CHANNEL_ID'], render_message())
