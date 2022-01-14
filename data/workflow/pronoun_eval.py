import pandas as pd
pd.set_option('display.max_rows', 500)
import re
import cariban_helpers as ch
import pyradigms as pyd
import numpy as np
import lingpy
from segments import Tokenizer, Profile
from sys import path
path.append("/home/florianm/Dropbox/Uni/Research/LiMiTS/musings/cariban_irregular_1/workflow/")
from lingpy_alignments import calculate_alignment

lg_list = list(ch.lg_order().keys())


segments = open("/home/florianm/Dropbox/Uni/Research/LiMiTS/musings/cariban_irregular_1/data/segments.txt").read()
segment_list = [{"Grapheme": x, "mapping": x} for x in segments.split("\n")]
t = Tokenizer(Profile(*segment_list))

def has_cognate(string, df):
    return df["Cognate_List"].apply(lambda x: string in x)

def segmentify(form):
    form = re.sub("[()\[\]]", "", form)
    form = form.replace("-", "+")
    form = form.strip("+")
    return t(form)

def sort_lg(df):
    df.Language_ID = df.Language_ID.astype("category")
    df.Language_ID.cat.set_categories(lg_list, ordered=True, inplace=True)
    df.sort_values(["Language_ID"], inplace=True)

def export4map(df, feature, col, param=None):
    if param:
        df = df[df["Parameter_ID"] == param]
    df = df[df.index.str[0] != "P"]
    df = df.rename(columns={"Language_ID": "ID", col: "value"})
    df.index.name = "ID"
    df.drop_duplicates(inplace=True)
    df = df[df.index != "tam"]
    df[["value"]].to_csv(f"/home/florianm/Dropbox/Uni/Research/LiMiTS/tools/cariban_maps/phylo_map/data/{feature}_data.csv", index=True)


cognatesets = pd.read_csv("cognatesets.csv")

cognatesets.index = cognatesets.index + 1

cognum = dict(zip(cognatesets["ID"], cognatesets.index.astype(str)))
numcog = dict(zip(cognatesets.index.astype(str), cognatesets["ID"]))

def str2numcog(cogsets):
    return " ".join([cognum[x] for x in cogsets.split("+")])


def glide1(form):
    if "w" in form:
        return "*əwɨ"
    elif "ju" in form:
        return "*ju"
    elif "u" in form:
        return "*u"
    else:
        return "???"

def aligned_table(df):
    df = df.copy()
    df["Cognateset_ID"] = df["Cognates"].map(str2numcog)
    df["Segments"] = df.apply(lambda x: segmentify(x["Form"]), axis=1)
    df.reset_index(inplace=True)
    df.index += 1
    table = calculate_alignment(df, fuzzy=True)
    sort_lg(table)
    print(table)
    # pyd.y =  ["Language_ID"]
    # pyd.x = ["Meaning_ID"]
    # pyd.z = []
    # pyd.filters = {"Meaning_ID": ["1"]}
    # pyd.y_sort = list(ch.lg_order().keys())
    # overview = pyd.compose_paradigm(df)
    # print(overview)

features = pd.DataFrame(index=lg_list)

df = pd.read_csv("../raw/forms.csv", index_col=0)
df.index = df.index.str.replace("ing", "kap")
df.index = df.index.str.replace("aka", "kap")
df["Cognate_List"] = df["Cognates"].apply(lambda x: x.split("+") if not pd.isnull(x) else [])
# df.drop_duplicates(subset="Form", inplace=True)
df['index'] = df.index
df.drop_duplicates(subset=["Form", "index"], inplace=True)
del df['index']

tempdf = df[df["Parameter_ID"] == "1"]

features["1phono"] = tempdf["Form"].map(glide1)
features["1cognates"] = tempdf["Cognates"]
features["1combo"] = features.apply(lambda row: row["1cognates"].replace("1", row["1phono"]) if not pd.isnull(row["1cognates"]) else np.nan, axis=1)


tempdf = df[df["Parameter_ID"] == "2"]
features["2cognates"] = tempdf["Cognates"]

tempdf = df[has_cognate("1a3", df)]

features["1a3cognates"] = tempdf["Cognates"]
aligned_table(tempdf)

# for col in features.columns:
#     export4map(features, col, col)