import csv
import os
import pandas as pd


from pymongo import MongoClient
from pymongo.server_api import ServerApi


class Scrapmibici:
    def __init__(self):
        self.url_bicis = "/app/assets/csv/"
        self.url_clima = "/app/assets/datos_clima/"

    def archivo_info_bicis(self):
        files = os.listdir(self.url_bicis)
        if files:
           # files.sort(key=lambda x: os.path.getmtime(os.path.join(self.url_bicis, x)))
           return os.path.join(self.url_bicis,"nomenclatura_2024_03.csv")
        else:
            return None

    def fusion_bicis(self):
        dfs = []
        csv_files = [file_name for file_name in os.listdir(self.url_bicis) if file_name.endswith('.csv')]
        csv_files_except_last = csv_files[:-1] #Excluye el último archivo
        for file_name in csv_files_except_last:
            file_path = os.path.join(self.url_bicis, file_name)
            df = pd.read_csv(file_path,encoding='latin-1', header=0)
            dfs.append(df)
        bicis_fusionadas = pd.concat(dfs, ignore_index=True)
        return bicis_fusionadas

    def anadir_lugar(self):
        ruta_info = self.archivo_info_bicis()
        df_info_bicis = pd.read_csv(ruta_info, encoding='latin-1', header=0)
        df_bicis = (self.fusion_bicis())
        merged_df = pd.merge(df_bicis, df_info_bicis, left_on='Origen_Id', right_on='id', how='left')
        return merged_df

    def datos_clima_gdl(self):
        ruta = self.url_clima+"Guadalajara"
        dfs = []
        for root,dirs,files in os.walk(ruta):
            for file in files:
                if "hourly_data" in file and file.endswith(".csv"):
                    df = pd.read_csv(os.path.join(root,file),encoding='latin-1', header=0)
                    dfs.append(df)
        return pd.concat(dfs, ignore_index=True)

    def datos_clima_tlq(self):
        ruta = self.url_clima + "Tlaquepaque"
        dfs = []
        for root, dirs, files in os.walk(ruta):
            for file in files:
                if "hourly_data" in file and file.endswith(".csv"):
                    df = pd.read_csv(os.path.join(root, file), encoding='latin-1', header=0)
                    dfs.append(df)
        return pd.concat(dfs, ignore_index=True)

    def datos_clima_zpn(self):
        ruta = self.url_clima + "Zapopan"
        dfs = []
        for root, dirs, files in os.walk(ruta):
            for file in files:
                if "hourly_data" in file and file.endswith(".csv"):
                    df = pd.read_csv(os.path.join(root, file), encoding='latin-1', header=0)
                    dfs.append(df)
        return pd.concat(dfs, ignore_index=True)

    def subir_datos_a_mongo(self,ruta_csv):
        uri = "mongodb+srv://porosengineers:Oy8ngC5FVvOFqKcZ@biciclimacluster.yyakcv9.mongodb.net/?retryWrites=true&w=majority&appName=BiciClimaCluster"
        cliente = MongoClient(uri,server_api=ServerApi('1'))
        db = cliente.BiciClima
        col = db.MiBiciClima
        with open(ruta_csv, 'r',encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                col.insert_one(row)
        print('Datos subidos con éxito')

    def start(self):
        df_bicis = self.anadir_lugar()
        #separar el clima en lugares
        lugares = ['GDL','ZPN','TLQ']
        dfs_dict = {}
        for lugar in lugares:
            filtered_df = df_bicis[df_bicis['name'].str.contains(lugar, regex=True)]
            dfs_dict[lugar] = filtered_df

        df_bicis_gdl = dfs_dict['GDL']
        df_bicis_zpn = dfs_dict['ZPN']
        df_bicis_tlq = dfs_dict['TLQ']

        df_bicis_gdl['Inicio_del_viaje'] = pd.to_datetime(df_bicis_gdl['Inicio_del_viaje']).dt.tz_localize(None)
        df_bicis_zpn['Inicio_del_viaje'] = pd.to_datetime(df_bicis_zpn['Inicio_del_viaje']).dt.tz_localize(None)
        df_bicis_tlq['Inicio_del_viaje'] = pd.to_datetime(df_bicis_tlq['Inicio_del_viaje']).dt.tz_localize(None)

        df_clima_gdl = self.datos_clima_gdl()
        df_clima_zpn = self.datos_clima_zpn()
        df_clima_tlq = self.datos_clima_tlq()

        df_clima_gdl['date'] = pd.to_datetime(df_clima_gdl['date']).dt.tz_localize(None)
        df_clima_zpn['date'] = pd.to_datetime(df_clima_zpn['date']).dt.tz_localize(None)
        df_clima_tlq['date'] = pd.to_datetime(df_clima_tlq['date']).dt.tz_localize(None)

        df_bicis_gdl = df_bicis_gdl.sort_values('Inicio_del_viaje')
        df_bicis_zpn = df_bicis_zpn.sort_values('Inicio_del_viaje')
        df_bicis_tlq = df_bicis_tlq.sort_values('Inicio_del_viaje')

        df_clima_gdl = df_clima_gdl.sort_values('date')
        df_clima_zpn = df_clima_zpn.sort_values('date')
        df_clima_tlq = df_clima_tlq.sort_values('date')

        df_gdl = pd.merge_asof(df_bicis_gdl, df_clima_gdl, left_on='Inicio_del_viaje', right_on='date')
        df_zpn = pd.merge_asof(df_bicis_zpn, df_clima_zpn, left_on='Inicio_del_viaje', right_on='date')
        df_tlq = pd.merge_asof(df_bicis_tlq, df_clima_tlq, left_on='Inicio_del_viaje', right_on='date')

        ruta = "assets/datos_finales/"
        if not os.path.exists(ruta):
            os.makedirs(ruta)
        df_gdl.to_csv(ruta+"datos_guadalajara.csv", index=False)
        df_zpn.to_csv(ruta+"datos_zapopan.csv", index=False)
        df_tlq.to_csv(ruta+"datos_tlaquepaque.csv", index=False)

        csv_final = pd.concat([df_gdl,df_zpn,df_tlq],ignore_index=True)
        csv_final.to_csv(ruta+"datos_finales.csv", index=False)

        self.subir_datos_a_mongo(ruta+"datos_finales.csv")

        print(f"Datos descargados y organizados en el directorio {ruta}")
