import sys
import requests
import os
import shutil
import html
from datetime import timedelta
import dateutil.parser
from ics import Calendar, Event
from bs4 import BeautifulSoup

OUT_DIR = os.environ.get('OUT_DIR', './out')
BASE_URL = os.environ.get('BASE_URL', 'http://www.derecho.uba.ar/')
IN_URL = os.environ.get('IN_URL', 'http://www.derecho.uba.ar/agenda/')
debug = os.environ.get('DEBUG', 'false') == 'true'
if debug:
    with open('example.html') as fp:
        html_doc = fp.read()
else:
    req = requests.get(IN_URL)
    html_doc = req.text

calendar = Calendar()
soup = BeautifulSoup(html_doc, 'html.parser')
for article in soup.find_all('article', class_='item-agenda'):
    fecha = article.find('time')['datetime']
    link = article.find('a')
    title = link.get_text()
    calendar.events.add(Event(
        name=title,
        begin=fecha + '-03:00',
        description=BASE_URL + link['href'],
        duration=timedelta(hours=2),
    ))


shutil.rmtree(OUT_DIR, ignore_errors=True)
os.mkdir(OUT_DIR)

with open(f'{OUT_DIR}/agenda.ics', 'w') as f:
    f.writelines(calendar.serialize_iter())

with open(f'{OUT_DIR}/index.html', 'w') as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html lang="es">\n')
    f.write('<head><title>Agenda de actividades | Facultad de Derecho - Universidad de Buenos Aires</title></head>\n')
    f.write('<body>\n')
    f.write('<p><a href="agenda.ics">Agregar Calendario</a></p>\n')
    f.write('<table>\n')
    for ev in sorted(calendar.events, key=lambda ev: str(ev.begin)):
        f.write('<tr>\n')
        f.write(f'<td>{ev.name}</td>\n')
        f.write(f'<td>{dateutil.parser.isoparse(str(ev.begin)).strftime("%d/%m/%y %H:%M")}</td>\n')
        f.write(f'<td><a href="{ev.description}">Más información</a></td>\n')
        f.write('</tr>\n')
    f.write('</table>\n')
    f.write('</body>\n')
    f.write('</html>\n')
