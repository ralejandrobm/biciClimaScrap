from src.main import App
from src.apps.api_app.ApiApp import ApiApp
from src.apps.scrap_mibici.Scrapmibici import Scrapmibici
from src.apps.scrap_csv.Scrapcsv import MiBiciScraper
from src.apps.openmeteo.OpenMeteo import OpenMeteo


import argparse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    parser = argparse.ArgumentParser(
        prog='Apps',
        description='Define all apps',
        epilog='Define all apps'
    )
    parser.add_argument('-app', '--application', default=None, required=False)
    parser.add_argument('-r', '--range', default=None, required=False)

    args = parser.parse_args()

    app_name = args.application
    print(f"\n\n 🏁 start app: {app_name}")

    if not app_name:
        App.start()
        return

    if app_name == "ApiApp":
        api_app = ApiApp()
        api_app.start()
        return

    if app_name == "Scrapmibici":
        scrapmibici = Scrapmibici()
        scrapmibici.start()
        return
    

    if app_name == "Scrapcsv":
        scraper = MiBiciScraper()
        scraper.start()

    if app_name == "OpenMeteo":
        om = OpenMeteo()
        om.start()
        return
    



if __name__ == "__main__":
    main()
