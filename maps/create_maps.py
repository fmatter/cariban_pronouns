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

def sort_by(df, col, order):
    df[col] = pd.Categorical(df[col], order)
    df = df.sort_values(by=col)
    df[col] = t[col].astype(str)
    return df


def stack_lg_values(df, target_col):
    df = df[["Clade", target_col]]
    df.drop_duplicates(["Clade", target_col], inplace=True)
    df.sort_values(by=target_col, inplace=True)
    return df.groupby(["Clade"])[target_col].apply(' / '.join).reset_index()

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

# fam = pd.read_csv("family.csv")
# plot_map(fam, "family", legend_size=7)


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
plot_map(t, "2cog")

