import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from urllib.parse import urljoin
from requests import Session

url_mibici = 'https://www.mibici.net/es/datos-abiertos/'
csv_directory = '/assets/csv'
links_file = '/assets/csv/links.txt' 

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
})

def status_code_url(url):
    r = session.get(url)
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'lxml')
    else:
        print('Error, el status no es correcto')
        return None

def get_csv_links(s):
    section_dl = s.select('section.data-year-container dl.open-dl')
    csv_links = [completar_url(link.get('href')) for dl in section_dl for link in dl.find_all('a') if link.get('href').endswith('.csv')]
    return csv_links

def completar_url(url):
    url_base = 'https://www.mibici.net/es'
    return urllib.parse.urljoin(url_base, url)

def download_csv(url, file_name):
    r = session.get(url)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)
        print(f'Archivo {file_name} descargado con éxito.')
    else:
        print(f'Error al descargar {url}: Estado {r.status_code}')

def load_downloaded_links():
    if os.path.exists(links_file):
        with open(links_file, 'r') as f:
            return set(line.strip() for line in f.readlines())
    else:
        return set()

def save_downloaded_links(links):
    with open(links_file, 'w') as f:
        for link in links:
            f.write(link + '\n')

if __name__ == '__main__':
    s = status_code_url(url_mibici)
    csv_links = get_csv_links(s)
    csv_links = list(set(csv_links))  # Eliminar duplicados

    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    # Enlaces de los archivos ya descargados
    downloaded_links = load_downloaded_links()

    for url in csv_links:
        if url not in downloaded_links:  # Si el enlace no se ha descargado antes
            print(f'Descargando {url}')
            file_name = os.path.join(csv_directory, os.path.basename(url))
            download_csv(url, file_name)
            downloaded_links.add(url)
        else:
            print(f'El archivo {os.path.basename(url)} ya ha sido descargado anteriormente.')

    # Guardar los enlaces 
    save_downloaded_links(downloaded_links)