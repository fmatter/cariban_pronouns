from lingtreemaps import plot
import pandas as pd

from Bio import Phylo
import matplotlib.pyplot as plt
from cariban_helpers import lg_order

pd.options.mode.chained_assignment = None  # default='warn'

tree = Phylo.read("../maps/cariban.newick", "newick")

lgs = pd.read_csv("../data/raw/languages.csv")
f = """apa
tri
hix
pan
mac
wmr
mak
wai
way
kar
ikp
uxc
ara
pem
kap
yuk
car
bak
tam
kax
aku
jap
map
yab
pno""".split(
    "\n"
)

lgs = lgs[lgs["ID"].isin(f)]
lgs.rename(columns={"lat": "Latitude", "long": "Longitude"}, inplace=True)

text_df = pd.read_csv("countries.csv")


forms = pd.read_csv("../data/raw/forms.csv", dtype=str)
forms = forms[~(pd.isnull(forms["Cognates"]))]
forms.rename(columns={"Language_ID": "Clade"}, inplace=True)
forms.drop(columns=["ID"], inplace=True)
forms["Clade"] = forms["Clade"].replace("aka", "kap")
forms["Clade"] = forms["Clade"].replace("ing", "kap")
forms = forms[~(forms["Clade"].str.contains("P"))]


def sort_by(df, col, order):
    df[col] = pd.Categorical(df[col], order)
    df = df.sort_values(by=col)
    df[col] = df[col].astype(str)
    return df


def stack_lg_values(df, target_col):
    df = df[["Clade", target_col]]
    df.drop_duplicates(["Clade", target_col], inplace=True)
    df.sort_values(by=target_col, inplace=True)
    return df.groupby(["Clade"])[target_col].apply(" / ".join).reset_index()


def plot_map(feature_df, name, **kwargs):
    plot(
        lgs,
        tree,
        feature_df=feature_df,
        text_df=text_df,
        tree_depth=6,
        marker_size=0.17,
        tree_map_padding=2.7,
        print_col="Orthographic",
        map_marker_size=25,
        font_size=6.5,
        text_x_offset=0.3,
        text_y_offset=0.135,
        leaf_lw=0.5,
        **kwargs,
    )
    plt.savefig(
        f"../docs/pld-slides/images/{name}.svg", bbox_inches="tight", pad_inches=0
    )


fam = pd.read_csv("family.csv")
fam = sort_by(fam, "Value", ["Yukpan", "Venezuelan", "Taranoan", "Parukotoan", "Pekodian", "Isolate"])
plot_map(fam, "family", legend_size=7)


# FIRST PERSON
cogmap1 = {"1": "*əwɨ", "1+EMP": "*əwɨ+rə", "1+hform": "*əwɨ+hɨ"}
t = forms[forms["Cognateset_ID"] == "1"]
t["Value"] = t["Cognates"].map(cogmap1)
t = sort_by(t, "Value", cogmap1.values())
# plot_map(t, "1cog")


def val1(row):
    if "ju" in row["Form"]:
        return "ju"
    elif "w" in row["Form"]:
        return "wV"
    elif "u" in row["Form"]:
        return "u"
    else:
        return "NONE"


t["Value"] = t.apply(val1, axis=1)
t = sort_by(t, "Value", ["wV", "u", "ju"])
# plot_map(t, "1form")

# SECOND PERSON
cogmap2 = {"2": "*əmə", "2+EMP": "*əmə+rə", "2 / 2+EMP": "*əmə(+rə)"}
t = forms[forms["Cognateset_ID"] == "2"]
t = stack_lg_values(t, "Cognates")
t["Value"] = t["Cognates"].map(cogmap2)
t = sort_by(t, "Value", cogmap2.values())
# plot_map(t, "2cog")


# 1+2
cogmap12 = {
    "1a2+mform+EMP": "*kɨ-mə",
    "1a2+mform": "*kɨ-mə",
    "1a2+?+mform": "*kɨ-mə",
    "1a2+karform / 1a2+mform+EMP": "*kɨ-mə / kɨ-ʔko",
    "1a2+wform+EMP": "*kɨ-wɨ",
    "1a2+wform": "*kɨ-wɨ",
    "uku": "*(k)uku",
    "uku+EMP": "*(k)uku",
    "1a2cop": "*eti-nə",
    "1a2ep": "epɨ",
    "1+PL-3": "*ju-to",
    "1+EMP+PL-3": "*ju-to",
    "1+EMP+PL-3+PL-1": "*ju-to",
    "1+EMP+pempl+PL-1": "(u+rə+ʔno+kon)",
}
color_dict = {
    "*kɨ-mə": "red",
    "*kɨ-mə / kɨ-ʔko": "firebrick",
    "*kɨ-wɨ": "orange",
    "*(k)uku": "green",
    "*ju-to": "blue",
    "*eti-nə": "darkviolet",
    "epɨ": "darkslategray",
    "(u+rə+ʔno+kon)": "gray"
}
t = forms[forms["Cognateset_ID"] == "1+2"]
t = stack_lg_values(t, "Cognates")
t["Value"] = t["Cognates"].map(cogmap12)
t = sort_by(t, "Value", list(dict.fromkeys(cogmap12.values())))
# plot_map(t, "12cog", legend_size=5.5, color_dict=color_dict)


def val13(row):
    if row["Cognates"] == "ti+1a3":
        return "*t͡ʃimna"
    elif row["Form"] == "amna":
        return "*amna"
    elif row["Form"] in ["anja", "aɲa"]:
        return "*anja"
    elif row["Form"][0:2] in ["in", "ɨn"]:
        return "*i(n)na"
    elif row["Form"][0:2] == "an":
        return "*a(n)na"
    elif row["Form"][0:2] == "n+":
        return "*na(ʔ)na"
    elif row["Form"] == "tis+u+ɣe":
        return "tis-u-ɣe"
    else:
        return "other"
# 1+3
t = forms[forms["Cognateset_ID"] == "1+3"]
t["Value"] = t.apply(val13, axis=1)
t = sort_by(t, "Value", ["*amna", "*anja", "*t͡ʃimna", "*a(n)na", "*i(n)na", "*na(ʔ)na", "tis-u-ɣe", "other"])
# plot_map(t, "13form", legend_size=7)


# 3ana
t = forms[forms["Cognateset_ID"] == "3ANA.ANIM"]
t["Value"] = "*inərə"
# plot_map(t, "3aana")

def check_3i(rec):
    if "ɲ" in rec["Form"] or "i" in rec["Form"] or rec["Form"][0] == "ɨ":
        return "*i"
    else:
        return "no *i"

t["Value"] = t.apply(check_3i, axis=1)
t = sort_by(t, "Value", ["*i", "no *i"])
plot_map(t, "3aanai")

t = forms[forms["Cognateset_ID"] == "3ANA.INAN"]
t["Value"] = "*irə"
# plot_map(t, "3iana")

# anim dem
t = forms[forms["Cognateset_ID"] == "PROX.ANIM"]
t["Value"] = t.apply(lambda x: "m-initial" if x["Form"].startswith("m") else "m-loss", axis=1)
# plot_map(t, "prox-m")

t = forms[forms["Cognateset_ID"] == "DIST.ANIM"]
t["Value"] = t.apply(lambda x: "m-initial" if x["Form"].startswith("m") else "m-loss", axis=1)
# plot_map(t, "dist-m")

t = forms[forms["Cognateset_ID"] == "MED.ANIM"]
t["Value"] = t.apply(lambda x: "m-initial" if x["Form"].startswith("m") else "m-loss", axis=1)
# plot_map(t, "med-m")


# inan dem
def mobile_s(rec):
    if rec["Form"][0] in ["ʃ", "t", "s", "h"]:
        return "*tj"
    else:
        return "no *tj"

t = forms[forms["Cognateset_ID"] == "PROX.INAN-1"]
t["Value"] = t.apply(mobile_s, axis=1)
plot_map(t, "1-s")

t = forms[forms["Cognateset_ID"] == "PROX.INAN-2"]
t["Value"] = t.apply(mobile_s, axis=1)
t = stack_lg_values(t, "Value")
plot_map(t, "2-s")
