import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class MiBici:
    global url_mibici
    url_mibici = 'https://www.mibici.net/es/datos-abiertos/'

    # Función para obtener el objeto BeautifulSoup de una URL
    def get_soup(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f'Error: No se pudo obtener el contenido de {url} {response.status_code}')
            return None

    # Función para obtener la lista de URL de archivos CSV
    def get_csv_links(self,soup):
        csv_links = []
        for link in soup.select('section.data-year-container a[href$=".csv"]'):
            csv_links.append(urljoin(url_mibici, link['href']))
        return csv_links

    # Función para descargar y guardar un archivo CSV
    def save_csv(self,url, filename):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            if response.headers.get('content-type') == 'text/csv' and '2024' in url:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f'Archivo {filename} descargado con éxito.')
            else:
                print(f'El archivo no es un CSV o no corresponde al año 2024.')
        else:
            print(f'Error al descargar {url}: Estado {response.status_code}')

    def start(self):
        soup = self.get_soup(url_mibici)
        if soup:
            csv_links = self.get_csv_links(soup)
            directorio = 'assets/datos_bicis'
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            for i, csv_link in enumerate(csv_links, start=1):
                self.save_csv(csv_link, directorio.format(i))
            print(f'Total de archivos CSV descargados: {len(csv_links)}')

if __name__ == "__main__":
    scrapmibici = MiBici()
    scrapmibici.start()