import pandas as pd
import pyradigms as pyd
import cariban_helpers as crh
import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns
from shapely import wkt

pd.options.mode.chained_assignment = None  # default='warn'

forms = pd.read_csv("raw/forms.csv", keep_default_na=False)
forms = forms[forms["Cognateset_ID"] != ""]
forms["Cognateset_ID"] = forms["Cognateset_ID"].str.replace("3ANA", "3", regex=True)
forms["Parameter_ID"] = forms["Parameter_ID"].str.replace("3ANA", "3", regex=True)

cogsets = pd.read_csv("raw/cognatesets.csv")
cogdic = dict(zip(cogsets["ID"], cogsets["Form"]))
cogdic["?"] = "?"

def get_cog_list(row):
    return list(zip(row["Form"].split("+"), row["Cognates"].split("+")))

def get_cog_dic(row):
    out = {}
    for form, cog in zip(row["Form"].split("+"), row["Cognates"].split("+")):
        if cog not in out:
            out[cog] = []
        out[cog].append(form)
    return out

def get_proto_form(str, prefix="", sep="-"):
    if str == "":
        return ""
    proto_string = []
    for x in str.split("+"):
        if x in cogdic:
            proto_string.append(cogdic[x])
        else:
            proto_string.append(x)
    return "*"+prefix+sep.join(proto_string)


forms["Proto_Form"] = forms["Cognates"].map(get_proto_form)

forms["Cognateset_ID"] = forms["Cognateset_ID"].apply(lambda x: x.split("; "))
forms = forms.explode("Cognateset_ID")
readme_overview = """"""

pronoun_strings = ["1", "2", "1+2", "1+2PL", "1+3", "2PL"]
pronoun_strings3 = ["3.ANIM", "3.ANIM.PL", "3.INAN", "3", "3.PL"]
dem_strings = [
    "PROX.ANIM",
    "PROX.ANIM.PL",
    "MED.ANIM",
    "MED.ANIM.PL",
    "DIST.ANIM",
    "DIST.ANIM.PL",
    "PROX.INAN-1",
    "PROX.INAN-2",
    # "PROX.INAN.PL",
    "MED.INAN",
    # "MED.INAN.PL",
    "DIST.INAN",
    # "DIST.INAN.PL",
]
all_pronouns = pd.DataFrame()
for lg in sorted([
    "kax",
    "PWai",
    "hix",
    "wai",
    "PC",
    "PPar",
    "PPP",
    "PTar",
    "PXin",
    "tri",
    "pem",
    "PTir",
    "mac",
    "aka",
    "ing",
    "aku",
    "car",
    "PPek",
    "ara",
    "ikp",
    "bak",
    "way",
    "kar",
    "apa",
    "PMan",
    "yab",
    "pno",
    "map",
    "uxc",
    "mak",
    "yuk",
    "wmr",
    "tam",
    "PPem",
    "pan",
], key=lambda x: crh.lg_order()[x]):

    temp = forms[forms["Language_ID"] == lg].copy()

    parlist = ["Person", "Number"]
    pronouns = temp[temp["Cognateset_ID"].isin(pronoun_strings)]
    pronouns["Parsed"] = pronouns["Cognateset_ID"].apply(
        lambda x: pyd.get_parameter_values(x, parlist)
    )
    pars = pd.DataFrame(pronouns["Parsed"].tolist())
    pars.columns = parlist
    pronouns = pronouns.reset_index(drop=True).join(pars)

    parlist = ["Person", "Animacy", "Number"]
    if lg in ["yuk"]:
        parlist = ["Person", "Number"]
    pronouns3 = temp[temp["Cognateset_ID"].isin(pronoun_strings3)]

    if len(pronouns3) > 0:
        pronouns3["Parsed"] = pronouns3["Cognateset_ID"].apply(
            lambda x: pyd.get_parameter_values(x, parlist)
        )
        pars = pd.DataFrame(pronouns3["Parsed"].tolist())
        pars.columns = parlist
        pronouns3 = pronouns3.reset_index(drop=True).join(pars)

    pronouns = pronouns.append(pronouns3)

    pronouns["Number"] = pronouns["Number"].map({None: "SG", "PL": "PL"})
    # individual paradigms
    # pyd.content_string = "Cognates"
    pyd.y = ["Person", "Animacy"]
    if lg in (["PC", "PPek", "car", "aku", "ing", "aka", "ara", "PMan", "PTir", "yab", "PPP", "map", "pno", "pem", "mac", "tam", "PPem", "pan", "yuk", "ikp", "PXin"]):
        pyd.y = ["Person"]
    pyd.y_sort = ["1", "1+2", "1+3", "2", "3ANIM", "3INAN"]
    pyd.x = ["Number"]
    pyd.x_sort = ["SG", "PL"]
    df = pyd.compose_paradigm(pronouns)
    df = df.applymap(lambda x: f"*{x}*")
    df.replace({"**":""}, inplace=True)
    if lg in crh.proto_languages:
        readme_overview += "**"+crh.get_name(lg)+"**\n"
        readme_overview += df.to_markdown() + "\n\n"

    parlist = ["Distance", "Animacy", "Number"]
    dems = temp[temp["Cognateset_ID"].isin(dem_strings)]
    if len(dems) > 0:
        dems["Parsed"] = dems["Cognateset_ID"].apply(
            lambda x: pyd.get_parameter_values(x, parlist)
        )
        pars = pd.DataFrame(dems["Parsed"].tolist())
        pars.columns = parlist
        dems = dems.reset_index(drop=True).join(pars)

    pronouns = pronouns.append(dems)
    pronouns["Number"] = pronouns["Number"].map({None: "SG", "PL": "PL"})

    all_pronouns = all_pronouns.append(pronouns)

f = open("../README.md", "w")
f.write(readme_overview)
f.close()

# comparative paradigms
pyd.x = ["Cognateset_ID"]
pyd.x_sort = dem_strings
# pronoun_strings + pronoun_strings3
pyd.y = ["Language_ID"]
pyd.y_sort = list(crh.lg_order().keys())
# pyd.content_string = "Cognates"
# pyd.content_string = "Proto_Form"
pyd.filters = {
"Cognateset_ID": dem_strings#["PROX.ANIM", "MED.ANIM", "DIST.ANIM", "PROX.INAN-1", "PROX.INAN-2", "MED.INAN", "DIST.INAN"],
# "Language_ID": ["ara", "ikp","PXin"]
# "Language_ID": crh.top_languages
}
df = pyd.compose_paradigm(all_pronouns)

print(df)

# GRAMMATICALIZATION OF EMPHATIC PARTICLE
# emp = all_pronouns.copy()
# # find out whether EMP is optional
# emp["COG"] = emp.apply(lambda x: get_cog_dic(x), axis=1)
# emp["EMP"] = emp["COG"].apply(lambda x: "EMP" in x and ")" not in "".join(x["EMP"]))
# tempemp = emp[emp["EMP"]]
# emp_pars = list(set(tempemp["Cognateset_ID"]))

# # emp = all_pronouns.copy()
# emp = emp[(emp["Cognateset_ID"].isin(emp_pars) & emp["Language_ID"].isin(crh.extant_languages))]

# emp_ratios = []
# for par in emp_pars:
#     temp = emp[emp["Cognateset_ID"] == par]
#     if temp["EMP"].sum() == 3:
#         print(temp)
#     emp_ratios.append({"Pronoun": par, "+EMP": temp["EMP"].sum(), "Total": len(temp), "Ratio": temp["EMP"].sum()/ len(temp)})
# emp_ratios = pd.DataFrame.from_dict(emp_ratios)
# emp_ratios.sort_values(by="Ratio", inplace=True, ascending=False)

# MAPS
# poly_df = pd.read_csv("etc/polygons.csv")

# def export_geojson(df, feature):
#     out = pd.merge(df, poly_df, left_on="ID", right_on="ID")
#     out['geometry'] = out['geometry'].apply(wkt.loads)
#     out = gpd.GeoDataFrame(out, crs='epsg:4326')
#     out = gpd.GeoDataFrame(out)
#     values = set(out["value"])
#     pal = sns.color_palette("tab10", len(values)).as_hex()
#     coldic = dict(zip(values, pal))
#     out["fill"] = out["value"].map(coldic)
#     out.to_file(f"etc/{feature}_data.json",driver="GeoJSON")

maps = []
def export4map(df, feature, col, param=None):
    if param:
        df = df[df["Cognateset_ID"] == param]
    df = df[df["Language_ID"].str[0] != "P"]
    df["Language_ID"] = df["Language_ID"].apply(crh.dedialectify)
    df = df.rename(columns={"Language_ID": "ID", col: "value"})
    out = df[["ID", "value"]]
    out.drop_duplicates(subset=["ID", "value"], inplace=True)
    out = (
        out.groupby(["ID"])["value"]
        .apply(lambda x: ", ".join(x.astype(str)))
        .reset_index()
    )
    # export_geojson(out, feature)
    out.set_index("ID", inplace=True)
    out.to_csv(
        f"/home/florianm/Dropbox/Uni/Research/LiMiTS/tools/cariban_maps/phylo_map/data/{feature}_data.csv",
        index=True,
    )
    maps.append(feature)


# export4map(all_pronouns, "2proto", "Proto_Form", param="2")

# plurals = []
# for i in range(1, 5):
#     plurals.append(f"PL-{i}")

# pl2 = all_pronouns[all_pronouns["Cognateset_ID"] == "2PL"]
# pl2["pl"] = pl2["Cognates"].str.split("+")
# pl2["pl"] = pl2["pl"].apply(lambda x: [c for c in x if c in plurals])
# pl2["Plural"] = pl2["pl"].str.join("+").apply(lambda x: get_proto_form(x, prefix="-"))
# export4map(pl2, "2plproto", "Plural", param="2PL")

first = all_pronouns[all_pronouns["Cognateset_ID"] == "1"]
first["EMP"] = first["Cognates"].apply(lambda x: "*əwɨ+rə" if "EMP" in x else "*əwɨ")

def first_form(str):
    for s in ["ju", "u"]:
        if str.startswith(s):
            return s
    else:
        return "əwɨ"

first["ju"] = first["Form"].apply(lambda x: first_form(x))
export4map(first, "1emp", "EMP")
export4map(first.sort_values(by="ju"), "1form", "ju")

# def incl_formative(cogs):
#     out = []
#     if "1a2" in cogs:
#         out.append("1a2")
#     elif "uku" in cogs:
#         out.append("uku")
#     elif "1" in cogs:
#         return "ju-PL"
#     elif "1a2ep" in cogs:
#         return "1a2ep"
#     else:
#         return "other"
#     if "wform" in cogs:
#         out.append("wform")
#     elif "mform" in cogs:
#         out.append("mform")
#     return "+".join(out)

# incl = all_pronouns[all_pronouns["Cognateset_ID"] == "1+2"]
# incl["form"] = incl["Cognates"].str.split("+")
# incl["form"] = incl["form"].apply(lambda x: incl_formative(x))
# incl["form"] = incl["form"].apply(lambda x: get_proto_form(x))
# print(incl)
# export4map(incl, "1+2", "form")


f = open(f"/home/florianm/Dropbox/Uni/Research/LiMiTS/tools/cariban_maps/phylo_map/pronoun_maps.txt", "w")
f.write("\n".join(maps)+"\n")
f.close()
