"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using geopandas.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    # Chargement des données depuis les fichiers CSV
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Fusion des données sur les colonnes correspondantes.
    merged = pd.merge(
        regions.rename(columns={"code": "code_reg", "name": "name_reg"}),
        departments.rename(columns={"code": "code_dep", "name": "name_dep"}),
        left_on="code_reg",
        right_on="region_code",
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Suppression des DOM-TOM-COM et des étrangers.
    filtered = referendum[~referendum["Department code"].str.startswith("97")]
    merged = pd.merge(
        filtered,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )
    return merged

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum()
    grouped = grouped.rename(
        columns={
            "Registered": "Registered",
            "Abstentions": "Abstentions",
            "Null": "Null",
            "Choice A": "Choice A",
            "Choice B": "Choice B",
        }
    )
    return grouped.reset_index().set_index("code_reg")

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Chargement des données géographiques.
    geo_data = gpd.read_file("data/regions.geojson")

    # Calcul du ratio.
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (
            referendum_result_by_regions["Choice A"] +
            referendum_result_by_regions["Choice B"]
        )
    )

    # Fusion des données géographiques avec les résultats.
    merged = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
    )

    # Affichage de la carte.
    merged.plot(column="ratio", legend=True, cmap="coolwarm")
    return merged

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
