import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, shape, GeometryCollection
import shapely
import geopandas as gpd
import json
from shapely.ops import cascaded_union
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from geovoronoi import voronoi_regions_from_coords, points_to_coords

area = gpd.read_file("etc/shape1.geojson")
area.crs = "EPSG:4326"
area = area.to_crs(epsg=3395)  # convert to World Mercator CRS
area_shape = area.iloc[0].geometry  # get the Polygon

lg_df = pd.read_csv("/home/florianm/Dropbox/Uni/Research/LiMiTS/tools/cariban_meta/cldf/languages.csv")
lg_df = lg_df[~(pd.isnull(lg_df["Longitude"]))]
lg_df = lg_df[lg_df["Alive"] == True]
lg_df = lg_df[pd.isnull(lg_df["Dialect_Of"])]

lg_df.reset_index(inplace=True)

gdf = gpd.GeoDataFrame(lg_df)
gdf.geometry = gdf.apply(lambda x: Point(x["Longitude"], x["Latitude"]), axis=1)
gdf.crs = "EPSG:4326"
gdf = gdf[["ID","geometry"]]
gdf = gdf.to_crs(area.crs)
coords = points_to_coords(gdf.geometry)


region_polys, region_pts = voronoi_regions_from_coords(coords, area_shape)

poly_dic = {}
for region, pts in region_pts.items():
    poly_dic[lg_df.iloc[pts[0]]["ID"]] = region_polys[region]

gdf_poly = gdf.copy()
gdf_poly["geometry"] = gdf_poly["ID"].map(poly_dic)

gdf_poly.crs = area.crs
gdf_poly = gdf_poly.to_crs("EPSG:4326")

gdf_poly.to_file("polytest.json", driver="GeoJSON")

gdf_poly.to_csv("etc/polygons.csv", index=False)


# fig, ax = subplot_for_map()
# plot_voronoi_polys_with_points_in_area(ax, area_shape, region_polys, coords, region_pts)

plt.savefig("test.pdf")
