from bs4 import BeautifulSoup
from datetime import datetime
import requests
import sys

url_tg = f"https://api.telegram.org/bot{sys.argv[1]}/sendMessage"

url = "https://erzelli.alpiristorazione.cloud/menu"
html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")
table = soup.find('table', { "class": "tabella_menu_settimanale" })

giorni = [
    "Lunedi'",
     "Martedi'",
     "Mercoledi'",
     "Giovedi'",
     "Venerdi'"
]

dt = datetime.now()
menu = {}
day =  dt.weekday() + 1
msg = ""

msg += f"====== {giorni[day-1]} ======\n"
menu[day]= {"giorno": giorni[day-1]}
for portata in table.find_all('tr', { "class": "portata"}):
    menu[day][portata.find('th').getText().strip()] = []
    msg += "==> " + portata.find('th').getText().strip() +" <==\n"
    for giorno in portata.find_all('td', {"data-giorno": day }):
          for piatto in giorno.find_all("p"):
            menu[day][portata.find('th').getText().strip()].append(piatto.getText().strip())
            msg += piatto.getText().strip()+ "\n"

try:
    response = requests.post(url_tg, json={'chat_id': sys.argv[2], 'text': msg})
except Exception as e:
    print(e)
