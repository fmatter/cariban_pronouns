import pandas as pd
from pyradigms import Pyradigm
import cariban_helpers as crh

pd.options.mode.chained_assignment = None  # default='warn'

forms = pd.read_csv("data/raw/forms.csv", keep_default_na=False)
forms["Cognateset_ID"] = forms["Cognateset_ID"].str.replace("3ANA", "3", regex=True)
forms["Meaning"] = forms["Meaning"].str.replace("3ANA", "3", regex=True)

# set morpheme IDs to lg + index where not present
forms["ID"] = forms.apply(
    lambda x: f"""{x["Language_ID"]}-f-{x.name}""" if x["ID"] == "" else x["ID"], axis=1
)

forms = forms[forms["Cognateset_ID"] != ""]

cogsets = pd.read_csv("data/raw/cognatesets.csv")
cogdic = dict(zip(cogsets["ID"], cogsets["Form"]))
cogdic["?"] = "?"

gloss = lambda x: f"[gl]({x.lower()})"

# def get_cog_list(row):
#     return list(zip(row["Form"].split("+"), row["Cognates"].split("+")))


# def get_cog_dic(row):
#     out = {}
#     for form, cog in zip(row["Form"].split("+"), row["Cognates"].split("+")):
#         if cog not in out:
#             out[cog] = []
#         out[cog].append(form)
#     return out


# def get_proto_form(str, prefix="", sep="-"):
#     if str == "":
#         return ""
#     proto_string = []
#     for x in str.split("+"):
#         if x in cogdic:
#             proto_string.append(cogdic[x])
#         else:
#             proto_string.append(x)
#     return "*" + prefix + sep.join(proto_string)


# forms["Proto_Form"] = forms["Cognates"].map(get_proto_form)

pronoun_strings = ["1", "2", "1+2", "1+2PL", "1+3", "2PL"]
pronoun_strings3 = ["3.ANIM", "3.ANIM.PL", "3.INAN", "3", "3.PL"]
dem_a = [
    "PROX.ANIM",
    "PROX.ANIM.PL",
    "MED.ANIM",
    "MED.ANIM.PL",
    "DIST.ANIM",
    "DIST.ANIM.PL",
]

dem_i = ["PROX.INAN-1", "PROX.INAN-2", "MED.INAN", "DIST.INAN"]

dem_strings = dem_a + dem_i


rename_dict = {
    "PROX.ANIM": "p;a",
    "PROX.ANIM.PL": "p;a;pl",
    "MED.ANIM": "m;a",
    "MED.ANIM.PL": "m;a;pl",
    "DIST.ANIM": "d;a",
    "DIST.ANIM.PL": "d;a;pl",
    "PROX.INAN-1": "p;i-1",
    "PROX.INAN-2": "p;i-2",
    "PROX.INAN.PL": "p;i;pl",
    "MED.INAN": "m;i",
    "MED.INAN.PL": "m;i;pl",
    "DIST.INAN": "d;i",
    "DIST.INAN.PL": "d;i;pl",
}


def comparative_paradigm(
    lg_list,
    meanings,
    name,
    decorate_x=lambda x: f"[lg]({x})",
    decorate=lambda x: f"[wf]({x}?nt&no_language)" if x != "" else "",
):
    pyd = Pyradigm(forms, x="Language_ID", y="Cognateset_ID", print_column="ID")
    pyd.compose_paradigm(
        filters={"Language_ID": lg_list, "Cognateset_ID": meanings},
        csv_output=f"docs/pld-slides/tables/{name}.csv",
        decorate_x=decorate_x,
        decorate=decorate,
    )


pek = ["PPek", "bak", "ara", "ikp"]
tar = ["PTar", "car", "tri", "aku"]
par = ["PPar", "kax", "hix", "wai"]

pem = ["PPem", "aka", "ing", "pem", "mac"]
man = ["PMan", "yab", "map", "pno"]

ppp = ["PPP", "pan", "PPem"]

ven = ["PPem", "pan", "tam", "mak", "PMan"]


pc1 = [
    "PC",
    "PPek",
    "PTar",
    "PPar",
    "PMan",
    "pan",
    "PPem",
    "mak",
    "tam",
    "kar",
    "way",
    "apa",
    "yuk",
    "uxc",
]

pc2 = [
    "PC",
    "PPek",
    "PTar",
    "PPar",
    "yab",
    "pan",
    "PPem",
    "mak",
    "tam",
    "kar",
    "way",
    "apa",
    "yuk",
    "uxc",
]

pyd = Pyradigm(forms, y="Language_ID", x="Cognateset_ID", print_column="ID")
pyd.compose_paradigm(
    filters={"Language_ID": pc1, "Cognateset_ID": pronoun_strings + pronoun_strings3},
    csv_output=f"docs/pld-slides/tables/pc_pro.csv",
    decorate=lambda x: f"[wf]({x}?nt&no_language)" if x != "" else "",
    decorate_y=lambda x: f"[lg]({x})",
)

pyd = Pyradigm(forms, y="Language_ID", x="Cognateset_ID", print_column="ID")

pyd.compose_paradigm(
    filters={"Language_ID": pc2, "Cognateset_ID": dem_a},
    decorate=lambda x: f"[wf]({x}?nt&no_language)" if x != "" else "",
    decorate_y=lambda x: f"[lg]({x})",
    category_joiner="<br>",
    csv_output=f"docs/pld-slides/tables/pc_dem_a.csv",
)

pyd = Pyradigm(forms, y="Language_ID", x="Cognateset_ID", print_column="ID")

pyd.compose_paradigm(
    filters={"Language_ID": pc2, "Cognateset_ID": dem_i},
    decorate=lambda x: f"[wf]({x}?nt&no_language)" if x != "" else "",
    decorate_y=lambda x: f"[lg]({x})",
    category_joiner="<br>",
    csv_output=f"docs/pld-slides/tables/pc_dem_i.csv",
)


l_dict = {
    "pek": pek,
    "tar": tar,
    "par": par,
    "pem": pem,
    "man": man,
    "ppp": ppp,
    "ven": ven,
}

for x, y in l_dict.items():
    comparative_paradigm(y, pronoun_strings + pronoun_strings3, f"{x}_pro")
    if x == "ven":
        comparative_paradigm(
            ["PPem", "pan", "tam", "mak", "yab"], dem_strings, f"{x}_dem"
        )
    else:
        comparative_paradigm(y, dem_strings, f"{x}_dem")


# synchronic paradigms
pyd = Pyradigm(forms, y="Language_ID", x="Meaning")
print(
    pyd.compose_paradigm(
        filters={
            "Meaning": ["3", "3.PL"],
            "Language_ID": ["PMan", "yab", "map", "pno", "mak"],
        }
    )
)

tri = forms[forms["Language_ID"] == "tri"]
tri["Form"] = tri["Form"].apply(lambda x: x.replace("+", ""))
pyd = Pyradigm(tri, x="Meaning", y="Language_ID", filters={"Meaning": pronoun_strings})
para = pyd.compose_paradigm()
tdf = pyd.decompose_paradigm(para, x=["Person", "Number"], y=["Language_ID"])
pyd = Pyradigm(tri, x="Meaning", y="Language_ID", filters={"Meaning": pronoun_strings3})
para = pyd.compose_paradigm()
tdf2 = pyd.decompose_paradigm(
    para, x=["Person", "Animacy", "Number"], y=["Language_ID"]
)
tdf = pd.concat([tdf, tdf2]).fillna("")
tdf["Number"] = tdf["Number"].replace("", "SG")
pyd = Pyradigm(tdf)
print(
    pyd.compose_paradigm(
        x="Number",
        y=["Person", "Animacy"],
        decorate=lambda x: "*" + x + "*",
        decorate_x=gloss,
        decorate_y=gloss,
        csv_output=f"docs/pld-slides/tables/tripro.csv",
    )
)

demt = dem_strings + ["INVIS.ANIM", "INVIS.INAN", "INVIS.ANIM.PL", "PROX.INAN"]
pyd = Pyradigm(tri, x="Meaning", y="Language_ID", filters={"Meaning": demt})
para = pyd.compose_paradigm()
tdf = pyd.decompose_paradigm(
    para, x=["Distance", "Animacy", "Number"], y=["Language_ID"]
)
tdf["Number"] = tdf["Number"].replace("", "SG")
pyd = Pyradigm(tdf)
print(
    pyd.compose_paradigm(
        sort_orders={"Animacy": ["ANIM", "INAN"], "Distance": ["PROX", "MED", "INVIS"]},
        y=["Distance", "Animacy"],
        x=["Number"],
        decorate=lambda x: "*" + x + "*",
        decorate_x=gloss,
        decorate_y=gloss,
        csv_output=f"docs/pld-slides/tables/tridem.csv",
    )
)


# forms["Cognateset_ID"] = forms["Cognateset_ID"].apply(lambda x: x.split("; "))
# forms = forms.explode("Cognateset_ID")
# readme_overview = """"""

# # # GRAMMATICALIZATION OF EMPHATIC PARTICLE
# # emp = all_pronouns.copy()
# # # find out whether EMP is optional
# # emp["COG"] = emp.apply(lambda x: get_cog_dic(x), axis=1)
# # emp["EMP"] = emp["COG"].apply(lambda x: "EMP" in x and ")" not in "".join(x["EMP"]))
# # tempemp = emp[emp["EMP"]]

# # emp_pars = list(set(tempemp["Cognateset_ID"]))
# # emp_pars.remove("1+3")
# # emp = emp[
# #     (
# #         emp["Cognateset_ID"].isin(emp_pars)
# #         & emp["Language_ID"].isin(crh.extant_languages)
# #     )
# # ]

# # emp_ratios = []
# # for par in emp_pars:
# #     temp = emp[emp["Cognateset_ID"] == par]
# #     if "1+2" in par:
# #         temp = temp[~(temp["Cognates"].str.contains("1\+"))]
# #     emp_ratios.append(
# #         {
# #             "Pronoun": par,
# #             "With \\gl{emp}": temp["EMP"].sum(),
# #             "Total": len(temp),
# #             "Ratio": temp["EMP"].sum() / len(temp),
# #         }
# #     )
# # emp_ratios = pd.DataFrame.from_dict(emp_ratios)
# # emp_ratios.sort_values(by="Ratio", inplace=True, ascending=False)
# # emp_ratios["Pronoun"] = emp_ratios["Pronoun"].map(lambda x: pynt.get_expex_code(x))
# # save_float(
# #     print_latex(
# #         emp_ratios,
# #         formatters={
# #             "Ratio": "{:,.2%}".format,
# #         },
# #     ),
# #     "empstats",
# #     "Distribution of grammaticalized emphatic markers"
# # )
