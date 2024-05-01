from bs4 import BeautifulSoup
from datetime import datetime
import jmespath
import json
import requests

base_url = "https://alpisanmarco.itchef.it/ITChefWebAPP"

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

def raw_query(filter: str) -> str:
    return f'[?DescrGruppo==`{filter}`].{{nome: DescrPiatto, kcal: ValoriNutrizionali.KCal}}'

def get_menu(iso_data, username, password):

  menu = {}
  login_data = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT':'',
    'txtResetPassword': '',
    'cmdLogin': 'ENTRA',
    'inputEmail': username,
    'inputPassword': password
  }

  with requests.Session() as s:
    response = s.get(f'{base_url}/Account/Login')
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    login_data["__VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
    login_data["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
    login_data["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]

    response = s.post(f'{base_url}/Account/Login', data=login_data)
    response.raise_for_status()

    menu_data = {
      'IdCliente':'6',
      'IdDestinazione':'6',
      'IdDieta':'2',
      'IdTipologia':'0',
      'IdServizio':'2',
      'sData':f'"{iso_data}"'
    }

    response = s.post(f"{base_url}/LocalServiceInterface.asmx/GetMenu",json=menu_data)
    response.raise_for_status()

    json_object = json.loads(response.json()["d"])    # Perdoname Spidi

    portate = {
      "Primo":"primi",
      "Secondo":"secondi",
      "Contorno":"contorni"
    }
    
    for piatto,nome in portate.items():
      expression = jmespath.compile(raw_query(piatto))
      menu[nome] = expression.search(json_object)[:3]
      
    s.get(f"{base_url}/Account/DoLogout")
     
  return menu

def render_piatto(piatto):
  allergeni_emoji = {
    'latte': emojis['glass_of_milk'],
    'glutine': emojis['ear_of_rice']
  }

  allergeni = ''
  if piatto.get('allergeni',False):
    allergeni = "".join(map(lambda x: f" {allergeni_emoji[x]}", piatto['allergeni']))

  return f"  {emojis['white_small_square']} <i>{piatto['nome']}{allergeni} [{piatto['kcal']} kcal]</i>"

def render_piatti(piatti):
  return "\n".join(map(render_piatto, piatti))

def render_message(username, password, dt=None):
  if not dt:
    dt = datetime.now()
  day = dt.weekday()
  data = dt.strftime('%d/%m/%Y')
  iso_data = dt.strftime('%Y-%m-%dT00:00:00')

  menu = get_menu(iso_data, username, password)

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
    publish_message_to_telegram(sys.argv[3], sys.argv[4], render_message(sys.argv[1], sys.argv[2]))
