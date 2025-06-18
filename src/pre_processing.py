# -*-coding:utf-8 -*-
"""
@File    :   pre_processing.py
@Time    :   2025/06/07 12:51:49
@Author  :   Juan-IB
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

from functions import hasCountryTarget, checkFiles

# %%
def main():
    # Create folder structure
    if not os.path.isdir("datasets/post"): 
        os.makedirs("datasets/post")
    # %%
    # List of required files
    files: list[str] = ["movie_data_tmbd.csv", "Cine_ciencia_ficcion_espacial_1940-1979_Actualizado.xlsx"]
    
    # Load dataset 
    # Source: https://www.kaggle.com/datasets/kakarlaramcharan/tmdb-data-0920
    # License: CC0 - Public Domain
    # Load dataset from kaggle
    if (checkFiles(files[0])):
        path = kgg.dataset_download("kakarlaramcharan/tmdb-data-0920")
        print("Path to dataset files:", path)
    # 

    movies_raw = pd.read_csv(r"datasets\movie_data_tmbd.csv", sep="|", lineterminator='\n')

    # %%
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ Extract index lists                                                         ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """
    # Extract internal indexes from the dataset on multi-valued attributes
    # Each film has values stored in Abstract Syntax Trees (ABS)
    # ('genres' and 'production_countries')

    # Each genre entry has a sequence of values,
    # where each value has a genre id and the genre in question

    genres: dict[int, str] = {}
    
    for i in range(0, len(movies_raw['genres'].values), 1):
        # Evaluate Python ABG(Abstract Syntax Grammar)
        movie_genres = ast.literal_eval(movies_raw['genres'].values[i])

        for genre in movie_genres:
            if (not (genre['id'] in genres)):
                genres[genre['id']] = genre['name']
                # print(f"Nuevo genero ({i}): {genre['id']}")
            elif (genres[genre['id']] != genre['name']):
                # Verify that there are no different genders with the same id.
                print("Superposición de géneros (mismo id)")

    # Store genres in csv file
    pd.DataFrame(data={'id': genres.keys(), 'name': genres.values()}).to_csv(r"datasets/post/genres.csv")

    # %%
    # Each country entry has a sequence of values,
    # where each value has a country ID and the country in question.

    countries: dict[str, str] = {}

    for i in range(0, len(movies_raw['production_countries'].values), 1):
        # Evaluate Python ABG(Abstract Syntax Grammar)
        movie_countries = ast.literal_eval(movies_raw['production_countries'].values[i])

        for countrie in movie_countries:
            if (not(countrie['iso_3166_1'] in countries)):
                countries[countrie['iso_3166_1']] = countrie['name']
                # print(f"Nuevo país ({i}): {countrie['iso_3166_1']}")
            elif (countries[countrie['iso_3166_1']] != countrie['name']):
                # Verify that there are no different countries with the same ID.
                print("Superposición de país (mismo id)")

    # Store countries in csv file
    pd.DataFrame(data={'id': countries.keys(), 'name': countries.values()}).to_csv(r"datasets/post/countries.csv")

    # %%
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ Extraction of relevant data                                                 ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """

    # %%
    # Values ​​of interest
    # Years: 40 - 49, 50 - 59, 60 - 69, 70- 79
    # Countries: US - UK - Italy - SU - JP
    countries_target: dict[str, str] = {"US": "United States of America",
                            "GB": "United Kingdom",
                            "IT": "Italy", "SU": "Soviet Union", "JP": "Japan"}

    # Returns entries that have a budget and country defined
    movies = movies_raw[(movies_raw['budget'] != 0 ) & (movies_raw['production_countries'] != "[]")].copy()
    #%%
    # Filter the list of countries
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
    # Import Consumer Price Index from U.S. Bureau of Labor page
    # https://data.bls.gov/timeseries/CUUR0000SA0?years_option=all_years
    cpi = pd.read_excel(r"datasets\SeriesReport-20250607233838_4a532a.xlsx", engine="openpyxl", header=11)
    cpi.rename(columns={'Year':'year', 'Annual': 'cpi'}, inplace=True) 

    movies['year'] = movies['year'].astype(int)
    cpi['year'] = cpi['year'].astype(int)

    # Apply the CPI to film data by year
    movies = movies.merge(cpi[(cpi['year'] >= 1940) & (cpi['year'] <= 1979)][['year','cpi']], on='year', how='left', suffixes=('', '_cpi'))
    cpi_now = cpi[cpi['year'] == 2025]['Apr'].values[0]
    movies['cpi'] =  (movies['budget'] * (cpi_now / movies['cpi'])).round().astype(int)
    movies.rename(columns={'cpi': 'budget_now'}, inplace=True)

    movies.to_csv("datasets/post/movies.csv", index=False)

    # %%
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ Science Fiction DB (sci-fi)                                                 ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """
    movies_scifi = pd.read_excel(
        r"datasets\Cine_ciencia_ficcion_espacial_1940-1979_Actualizado.xlsx",
        engine="openpyxl",
    )

    # %%
    movies_scifi.rename(
        columns={
            "Año": "year",
            "Presupuesto original (USD)": "budget",
            "Presupuesto actual aprox. (2025)": "budget_now",
            "Título": 'title'
        },
        inplace=True,
    )
    movies_scifi = (
        movies_scifi[
            (movies_scifi["budget_now"].notna()) & (movies_scifi["budget_now"] != "Bajo")
        ]
        .astype({"budget": int, "budget_now": int})
        .copy()
    )

    # %%
    movies_scifi.to_csv("datasets/post/movies_scifi.csv", index=False)
