from bs4 import BeautifulSoup
from datetime import datetime
import requests

url = "https://erzelli.alpiristorazione.cloud/menu"

_copyright = "@menumensaerzelli"
_data = "\U0001F449 Menù <b>{giorno}</b> {data}\n\n"
_portata = "<b><u>{portata}</u></b> {emoji}\n"
_piatto = "  \U000025AB <i>{piatto}{info}</i>\n"

def get_info(piatto):
  msg = ""
  try:
    response = requests.get(piatto.find("a")['href'])
    response.raise_for_status()
  except requests.HTTPError as e:
      print(e)
      return msg
  html = response.text
  soup = BeautifulSoup(html, "html.parser")
  glutine = "https://erzelli.alpiristorazione.cloud/images/allergeni/glutine.png" in html
  if glutine:
      msg+=" \U0001F33E"
  try:
    kcal = soup.find("div", {"class": "div_gda"}).find("p", {"class": "valore_gda"}).decode_contents()
    if not kcal:
        raise Exception("Kcal not found")
    kcal = kcal.split(">")[1].strip()
  except Exception as e:
      print(e)
      return msg
  msg+=f" [{kcal}]"
  return msg

def get_piatti(piatti_table):
    piatti = []
    for piatto in piatti_table.find_all("p")[:3]:
        piatti.append({'nome': piatto.getText().strip(), 'info': get_info(piatto)})
    return piatti

def get_menu():
  dt = datetime.now()
  day = dt.weekday() + 1
  response = requests.get(url)
  response.raise_for_status()
  html = response.text
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find('table', { "class": "tabella_menu_settimanale" })

  menu = {
    'giorno':   table.find_all('th',{ 'class': 'giorno_della_settimana'})[day-1].getText().lower(),
    'primi':    get_piatti(table.find('td', {"data-giorno": day , "data-tipo-piatto": 1})),
    'secondi':  get_piatti(table.find('td', {"data-giorno": day , "data-tipo-piatto": 2})),
    'contorni': get_piatti(table.find('td', {"data-giorno": day , "data-tipo-piatto": 4})),
  }
  return menu

def render_piatti(piatti):
    msg=""
    for piatto in piatti:
        msg+= _piatto.format(piatto=piatto['nome'], info=piatto['info'])
    msg+="\n"
    return msg

def render_message():
  dt = datetime.now()
  data = dt.strftime('%d/%m/%Y')
  menu = get_menu()

  msg = ""
  msg += _data.format(giorno = menu['giorno'], data=data)
  msg += _portata.format(emoji='\U0001F35D',portata='Primi')
  msg += render_piatti(menu['primi'])
  msg += _portata.format(emoji='\U0001F35B',portata='Secondi')
  msg += render_piatti(menu['secondi'])
  msg += _portata.format(emoji='\U0001F966',portata='Contorni')
  msg += render_piatti(menu['contorni'])
  msg+= _copyright

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
