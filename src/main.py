# -*-coding:utf-8 -*-
"""
@File    :   main.py
@Time    :   2025/06/01 14:47:36
@Author  :   Juan Ignacio Bianchini
@Version :   1.0
@Desc    :   Main file movedb.
"""
# https://www.kaggle.com/datasets/kakarlaramcharan/tmdb-data-0920
# %%
import pandas as pd
import openpyxl

import pre_processing
from functions import hasCountryTarget, statsbyDecade

# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Import, pre-process and clean datasets                                      ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""
pre_processing.main()

# Import datasets
movies = pd.read_csv(
    r"datasets\post\movies.csv",
)
movies_scifi = pd.read_excel(
    r"datasets\Cine_ciencia_ficcion_espacial_1940-1979_Actualizado.xlsx",
    engine="openpyxl",
)

# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Science Fiction DB (sci-fi)                                                 ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""
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

movie_matched = movies[movies["original_title"].isin(movies_scifi["title"])]
moviesnoUS = movies[
    movies["production_countries"].apply(
        lambda m: not hasCountryTarget(m, {"US": "United States of America"})
    )
].copy()
# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Gráficos                                                                    ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

# Datos películos de todos los géneros y de sci-f
data: list[pd.DataFrame] = [movies, movies_scifi]
labels: list[str] = ["Todos los géneros", "Sci-fi"]
colors: list[str] = ["black", "blue"]
atributes: list[str] = ['budget', 'budget_now']

# movies_scifi['budget'].apply(lambda x: isinstance(x, int)).all()

# %%
for atr in atributes:
    statsbyDecade(data, atr, 40, 70, "Promedio", labels=labels, colors=colors, image_path=f"img/{atr}")
    statsbyDecade(data, atr, 40, 70, "Mediana", labels=labels, colors=colors, image_path=f"img/{atr}")

    # Sin EEUU
    statsbyDecade(
        [moviesnoUS],
        atr,
        40,
        70,
        "Promedio",
        "Decada (sin EE.UU)",
        labels=["Todos los géneros"],
        colors=["black"], 
        image_path=f"img/{atr}",
    )
    statsbyDecade(
        [moviesnoUS],
        atr,
        40,
        70,
        "Mediana",
        "Decada (sin EE.UU)",
        labels=["Todos los géneros"],
        colors=["black"], 
        image_path=f"img/{atr}",
    )

# %%
