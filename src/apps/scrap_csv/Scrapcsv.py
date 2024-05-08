import os
import urllib.parse
import requests
from bs4 import BeautifulSoup

class MiBiciScraper:
    
    def __init__(self, url_mibici='https://www.mibici.net/es/datos-abiertos/', csv_directory='/app/assets/csv', links_file='/app/assets/csv/links.txt'):
        self.url_mibici = url_mibici
        self.csv_directory = csv_directory
        self.links_file = links_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        })

    def start(self):
        self.run_scraper()

    def status_code_url(self, url):
        r = self.session.get(url)
        if r.status_code == 200:
            return BeautifulSoup(r.text, 'lxml')
        else:
            print('Error, el status no es correcto')
            return None

    def get_csv_links(self, s):
        section_dl = s.select('section.data-year-container dl.open-dl')
        csv_links = [self.completar_url(link.get('href')) for dl in section_dl for link in dl.find_all('a') if link.get('href').endswith('.csv')]
        return csv_links

    def completar_url(self, url):
        url_base = 'https://www.mibici.net/es'
        return urllib.parse.urljoin(url_base, url)

    def download_csv(self, url, file_name):
        r = self.session.get(url)
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(r.content)
            print(f'Archivo {file_name} descargado con éxito.')
        else:
            print(f'Error al descargar {url}: Estado {r.status_code}')

    def load_downloaded_links(self):
        if os.path.exists(self.links_file):
            with open(self.links_file, 'r') as f:
                return set(line.strip() for line in f.readlines())
        else:
            return set()

    def save_downloaded_links(self, links):
        with open(self.links_file, 'w') as f:
            for link in links:
                f.write(link + '\n')

    def run_scraper(self):
        s = self.status_code_url(self.url_mibici)
        csv_links = self.get_csv_links(s)
        csv_links = list(set(csv_links))  # Eliminar duplicados

        if not os.path.exists(self.csv_directory):
            os.makedirs(self.csv_directory)

        # Enlaces de los archivos ya descargados
        downloaded_links = self.load_downloaded_links()

        for url in csv_links:
            if url not in downloaded_links:  # Si el enlace no se ha descargado antes
                print(f'Descargando {url}')
                file_name = os.path.join(self.csv_directory, os.path.basename(url))
                self.download_csv(url, file_name)
                downloaded_links.add(url)
            else:
                print(f'El archivo {os.path.basename(url)} ya ha sido descargado anteriormente.')

        # Guardar los enlaces 
        self.save_downloaded_links(downloaded_links)
