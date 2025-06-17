# eda_sci-fi_movies

A -little- work of EDA (Exploratory Data Analysis) over sci-fi movies of the early space age, between 40' and 70'.

Results are located in the **res** folder, so you <ins>don't</ins> need to run the code to get them.

# Usage

First, you need to install the required libraries. You can:
* Run `install-lib.bat` to install:
    ```powershell
    .\install-lib.bat
    ```
* Install libraries from requirements file:
    ```powershell
    pip install -r requirements.txt
    ```
Next, run main.py. This may take a while, as it needs to download the dataset from Kaggle (if you haven't already run it).
```powershell
py .\src\main.py
```


# License

## Dataset

This project uses the following dataset:

- **Name:** Movie data (100K+ titles with budget, credits)
- **Source:** [[Link to dataset](https://www.kaggle.com/datasets/kakarlaramcharan/tmdb-data-0920)]
- **License:** CC0 - Public Domain
- **Description:** This data contains information on 119K movies & TV shows released internationally scraped from TMBD (TMDB : https://www.themoviedb.org/). TMDB is a community built movie and TV database. We have the following information in the dataset. This dataset is in form of csv which is pipe delimited. This dataset has rich information on title, synposis, year of release, budget, revenue , popularity, original language in which movie/tv show was produced, production companies, production countries, user vote averages, runtime, release date, tagline, actors & directors

This dataset is in the public domain and can be used without restrictions under the CC0 license.