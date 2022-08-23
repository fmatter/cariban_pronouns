import pandas as pd
from pyradigms import Pyradigm
import cariban_helpers as crh
import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns
from shapely import wkt

pd.options.mode.chained_assignment = None  # default='warn'

forms = pd.read_csv("data/raw/forms.csv", keep_default_na=False)
forms = forms[forms["Cognateset_ID"] != ""]
forms["Cognateset_ID"] = forms["Cognateset_ID"].str.replace("3ANA", "3", regex=True)
forms["Meaning"] = forms["Meaning"].str.replace("3ANA", "3", regex=True)

# set morpheme IDs to lg + index where not present
forms["ID"] = forms.apply(
    lambda x: f"""{x["Language_ID"]}-{x.name}""" if x["ID"] == "" else x["ID"], axis=1
)

cogsets = pd.read_csv("data/raw/cognatesets.csv")
cogdic = dict(zip(cogsets["ID"], cogsets["Form"]))
cogdic["?"] = "?"


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
# pronoun_strings3 = ["3.ANIM", "3.ANIM.PL", "3.INAN", "3", "3.PL"]
# dem_strings = [
#     "PROX.ANIM",
#     "PROX.ANIM.PL",
#     "MED.ANIM",
#     "MED.ANIM.PL",
#     "DIST.ANIM",
#     "DIST.ANIM.PL",
#     "PROX.INAN-1",
#     "PROX.INAN-2",
#     # "PROX.INAN.PL",
#     "MED.INAN",
#     # "MED.INAN.PL",
#     "DIST.INAN",
#     # "DIST.INAN.PL",
# ]


def comparative_paradigm(
    lg_list,
    meanings,
    name,
    decorate_x=lambda x: f"[lg]({x})",
    decorate=lambda x: f"[wf]({x}?nt&no_language)" if x != "" else "",
):
    pyd = Pyradigm(forms, x="Language_ID", y="Cognateset_ID", print_column="ID")
    pyd.compose_paradigm(
        filters={"Language_ID": lg_list, "Meaning": meanings},
        csv_output=f"docs/pld-slides/tables/{name}.csv",
        decorate_x=decorate_x,
        decorate=decorate
    )


pek = ["PPek", "bak", "ara", "ikp"]
tar = ["PTar", "car", "tri", "aku"]
par = ["PPar", "kax", "hix", "wai"]
ppp = ["PPP", "pan", "PPem", "aka", "ing", "pem", "mac"]
pc = ["PC", "PPek", "PTar", "PPar", "PPP", "kar", "way", "apa", "yuk", "uxc"]
ven = ["PPem", "pan", "tam", "mak", "PMan"]
comparative_paradigm(pek, pronoun_strings, "pek_pro")
comparative_paradigm(tar, pronoun_strings, "tar_pro")
comparative_paradigm(par, pronoun_strings, "par_pro")
comparative_paradigm(ppp, pronoun_strings, "ppp_pro")
comparative_paradigm(pc, pronoun_strings, "pc_pro", decorate_x= lambda x: x)
comparative_paradigm(ven, pronoun_strings, "ven_pro")


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