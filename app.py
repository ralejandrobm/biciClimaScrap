from src.main import App
from src.apps.api_app.ApiApp import ApiApp

import argparse


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


if __name__ == "__main__":
    main()
