from bs4 import BeautifulSoup
from datetime import datetime
import requests
import sys

url_tg = f"https://api.telegram.org/bot{sys.argv[1]}/sendMessage"
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

def primi(piatti):
    msg = _portata.format(emoji='\U0001F35D',portata='Primi')
    for piatto in piatti.find_all("p")[:3]:
        msg+= _piatto.format(piatto= piatto.getText().strip(), info = get_info(piatto))
    msg+="\n"
    return msg

def secondi(piatti):
    msg = _portata.format(emoji='\U0001F35B',portata='Secondi')
    for piatto in piatti.find_all("p")[:3]:
        msg+= _piatto.format(piatto= piatto.getText().strip(), info = get_info(piatto))
    msg+="\n"
    return msg

def contorni(piatti):
    msg = _portata.format(emoji='\U0001F966',portata='Contorni')
    for piatto in piatti.find_all("p"):
        msg+= _piatto.format(piatto= piatto.getText().strip(), info = get_info(piatto))
    msg+="\n"
    return msg

def main():
  msg = ""
  dt = datetime.now()
  data = dt.strftime('%d/%m/%Y')
  day =  dt.weekday() + 1
  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.HTTPError as e:
      print(e)
      sys.exit(1)
  html = response.text
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find('table', { "class": "tabella_menu_settimanale" })

  msg+= _data.format(giorno = table.find_all('th',{ 'class': 'giorno_della_settimana'})[day-1].getText().lower(), data=data)
  msg+= primi(table.find('td', {"data-giorno": day , "data-tipo-piatto": 1}))
  msg+= secondi(table.find('td', {"data-giorno": day , "data-tipo-piatto": 2}))
  msg+= contorni(table.find('td', {"data-giorno": day , "data-tipo-piatto": 4}))

  msg+= _copyright

  try:
      response = requests.post(url_tg, json={'chat_id': sys.argv[2], 'parse_mode': "html",'text':  msg})
      response.raise_for_status()
  except requests.HTTPError:
        print(response.json())
  except Exception as e:
      print(e)

if __name__ == "__main__":
    main()
