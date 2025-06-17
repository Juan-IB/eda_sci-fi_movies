# -*-coding:utf-8 -*-
"""
@File    :   main.py
@Time    :   2025/06/01 14:47:36
@Author  :   Juan-IB
@Version :   1.0
@Desc    :   Main file of EDA (Exploratory Data Analysis) about sci-fi movies.
"""
# %%
import pandas as pd

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

movies_scifi = pd.read_csv(
    r"datasets\post\movies_scifi.csv",
)

# %%
# Filter datasets under certain criteria
# movie_matched = movies[movies["original_title"].isin(movies_scifi["title"])]
moviesnoUS = movies[
    movies["production_countries"].apply(
        lambda m: not hasCountryTarget(m, {"US": "United States of America"})
    )
].copy()
# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Graphs                                                                      ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

data: list[pd.DataFrame] = [movies, movies_scifi]
labels: list[str] = ["Todos los géneros", "Sci-fi"]
colors: list[str] = ["black", "blue"]
atributes: list[str] = ['budget', 'budget_now']

# movies_scifi['budget'].apply(lambda x: isinstance(x, int)).all()

# %%
for atr in atributes:
    statsbyDecade(data, atr, 40, 70, "Promedio", labels=labels, colors=colors, image_path=f"img/{atr}")
    statsbyDecade(data, atr, 40, 70, "Mediana", labels=labels, colors=colors, image_path=f"img/{atr}")

    # Without the US
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
