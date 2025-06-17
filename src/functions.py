# -*-coding:utf-8 -*-
"""
@File    :   functions.py
@Time    :   2025/06/07 12:44:32
@Author  :   Juan-IB
@Version :   1.0
@Desc    :   Contains reusable functions
"""

# %%
import os.path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import pandas as pd
import ast
# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Utilities                                                                   ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""
def checkFiles(files: list[str]) -> bool:
    """
    Checks if all listed files are found.
    """
    return all(os.path.exists(os.path.join('src/datasets', file)) for file in files)

# Recursive version.
# Due to Python's int optimization,
# it is more efficient up to 100,000 files #files = 100k (by empirical testing)
# def checkFiles(files: list[str]) -> bool:
#    """
#    Checks if all listed files are found.
#    """
#     if (len(files) != 1):
#         return os.path.isfile(files[0]) and checkFiles(files[1:])
#     else:
#         return os.path.isfile(files[0])

def hasCountryTarget(movie: str, countries: dict[str, str]) -> bool:
    """"
    Confirms whether an entry contains any of the countries of interest.
    """
    movie_countries = ast.literal_eval(movie)
    for iso_3166_1, country_name in countries.items():
        if any(
            country['iso_3166_1'] == iso_3166_1 or country['name'] == country_name
            for country in movie_countries
        ):
            return True
    
    return False

# %%
"""
╔═════════════════════════════════════════════════════════════════════════════╗
║ Graphs                                                                      ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

# %%
def statsbyDecade(
        dfs: list[pd.DataFrame], df_atr: str,
        start: int, end: int,
        stat: str, xlabel: str = "Decada",
        colors: list[str] = None, 
        labels: list[str] = None,
        image_path: str = "img",
        ) -> None:
    """
    Generates a line chart showing the evolution of a statistic (such as average, median, minimum, or maximum)
    for a numeric attribute in several DataFrames, grouped by decades.
    The chart is saved as an image in a specified folder.
    """
    

    stats: dict[str, str] = {
        "Promedio": 'mean',
        "Mediana": '50%',
        "Mínimo": 'min',
        "Máximo": 'max',
    }

    century: int = 1900
    
    fig, ax = plt.subplots(figsize=(8,8), layout='constrained')

    for df, label, color in zip(dfs, labels, colors):
        info_decadas: dict[str, float] = {}
        for i in range(start, end + 10, 10):
            by_decade = df[(df['year'] >= century + i) & (df['year'] <= century + i + 9)].copy()
            info_decadas[f"{i}'"] = by_decade[df_atr].describe()[stats[stat]]

        plotLine(list(info_decadas.keys()), y=list(info_decadas.values()), ax=ax, xlabel=xlabel, ylabel= stat + "(USD)", 
                label=label, color=color)
        
    # fig.legend(loc="upper left")
    fig.legend()
    if not os.path.isdir(image_path):
        os.makedirs(image_path)
    fig.savefig(f"{image_path}/{stat}-{xlabel}.png")

def plotLine(
    x, y,
    *,
    ax: Axes = None,
    xlabel: str = "",
    ylabel: str = "",
    yformat: str = ',.0f',
    **kwargs,
) -> Figure | None:
    """Function to plot a line chart."""

    standalone: bool = False
    if ax is None:
        standalone = True
        fig, ax = plt.subplots(figsize=(8,8), layout='constrained')

    ax.plot(
        x, y,
        **kwargs,
    )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # ax.set_xticks([])
    # ax.set_yticks([])
    if yformat is not None:
        # ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(f"{yformat}"))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x: ,.0f} USD"))
        # ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x/1000)}K"))

    else:
        ax.ticklabel_format(axis='y', style='plain')

    if standalone:
        plt.close(fig)
        return fig
    else:
        return None