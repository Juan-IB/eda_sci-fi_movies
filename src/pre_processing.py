# -*-coding:utf-8 -*-
"""
@File    :   pre_processing.py
@Time    :   2025/06/07 12:51:49
@Author  :   Juan Ignacio Bianchini
@Version :   1.0
@Desc    :   Contains the preprocessing process of datasets.
"""
# %%
import os.path
import pandas as pd
import kagglehub as kgg

import ast
import pandas
import duckdb as dd

from functions import hasCountryTarget

# %%
def main():
    # Crea la estructura de carpetas
    if not os.path.isdir("datasets/post"): 
        os.makedirs("datasets/post")
    # %%
    files: list[str] = ["movie_data_tmbd.csv", "Cine_ciencia_ficcion_espacial_1940-1979_Actualizado.xlsx"]

    # Download dataset form kaggle
    def checkFiles(files) -> bool:
        if (len(files) != 1):
            return os.path.isfile(files[0]) and checkFiles(files[1:])
        else:
            return os.path.isfile(files[0])

    if (checkFiles(files[0])):
        path = kgg.dataset_download("kakarlaramcharan/tmdb-data-0920")
        print("Path to dataset files:", path)

    movies_raw = pd.read_csv(r"datasets\movie_data_tmbd.csv", sep="|", lineterminator='\n')

    # %%

    # %%
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ Extracción de índices internos                                              ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """
    # Extraer índices internos del dataset en atributos multivaluados

    # Cada película tiene un array de diccionarios
    # (cada diccionario es un género)
    genres: dict[int, str] = {}
    for i in range(0, len(movies_raw['genres'].values), 1):
        movie_genres = ast.literal_eval(movies_raw['genres'].values[i])
        for genre in movie_genres:
            if (not (genre['id'] in genres)):
                genres[genre['id']] = genre['name']
                print(f"Nuevo genero ({i}): {genre['id']}")
            elif (genres[genre['id']] != genre['name']):
                # Corrobora que no hay generos diferentes con un mismo id
                print("Superposición de géneros (mismo id)")

    pd.DataFrame(data={'id': genres.keys(), 'name': genres.values()}).to_csv(r"datasets/post/genres.csv")

    # %%
    # Extrae todos los países del dataset
    countries: dict[str, str] = {}

    for i in range(0, len(movies_raw['production_countries'].values), 1):
        movie_countries = ast.literal_eval(movies_raw['production_countries'].values[i])
        for countrie in movie_countries:
            if (not(countrie['iso_3166_1'] in countries)):
                countries[countrie['iso_3166_1']] = countrie['name']
                print(f"Nuevo país ({i}): {countrie['iso_3166_1']}")
            elif (countries[countrie['iso_3166_1']] != countrie['name']):
                # Corrobora que no hay generos diferentes con un mismo id
                print("Superposición de país (mismo id)")

    pd.DataFrame(data={'id': countries.keys(), 'name': countries.values()}).to_csv(r"datasets/post/countries.csv")
    

    # %%
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ Extracción de datos relevantes                                              ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """

    # %%

    # 40 - 49, 50 - 59, 60 - 69, 70- 79
    # EE.UU. - Reino Unido - Italia - URSS - Japón
    # Lista de países de interes
    countries_target: dict[str, str] = {"US": "United States of America",
                            "GB": "United Kingdom",
                            "IT": "Italy", "SU": "Soviet Union", "JP": "Japan"}

    # Devuelve las entradas que tienen presupuesto y país definido
    movies = movies_raw[(movies_raw['budget'] != 0 ) & (movies_raw['production_countries'] != "[]")].copy()
    #%%
    # Filtra la lista de países
    movies = movies[movies["production_countries"].apply(lambda m: hasCountryTarget(m, countries_target))].copy()
    query = f"""--sql
        SELECT budget, YEAR(DATE(release_date)) AS year, title, 
        original_title, overview, production_countries, genres, directors
        FROM movies
        WHERE year BETWEEN 1940 AND 1979
        ORDER BY year ASC, budget DESC
    """
    movies = dd.sql(query).df()

    # %%
    # https://data.bls.gov/timeseries/CUUR0000SA0?years_option=all_years
    cpi = pd.read_excel(r"datasets\SeriesReport-20250607233838_4a532a.xlsx", engine="openpyxl", header=11)
    cpi.rename(columns={'Year':'year', 'Annual': 'cpi'}, inplace=True) 

    movies['year'] = movies['year'].astype(int)
    cpi['year'] = cpi['year'].astype(int)

    # Paso 2: Unir CPI al DataFrame de películas según el año
    movies = movies.merge(cpi[(cpi['year'] >= 1940) & (cpi['year'] <= 1979)][['year','cpi']], on='year', how='left', suffixes=('', '_cpi'))
    cpi_now = cpi[cpi['year'] == 2025]['Apr'].values[0]
    movies['cpi'] =  (movies['budget'] * (cpi_now / movies['cpi'])).round().astype(int)
    movies.rename(columns={'cpi': 'budget_now'}, inplace=True)

    movies.to_csv("datasets/post/movies.csv", index=False)
# %%
