import pathlib
import pandas as pd
from cldfbench import Dataset as BaseDataset
from segments import Profile, Tokenizer
import re
from slugify import slugify
import lingpy
from clldutils.misc import slug
import cariban_helpers as crh
import cldf_helpers as cldfh


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "cariban_pronouns"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        from cldfbench import CLDFSpec

        return CLDFSpec(dir=self.cldf_dir, module="Wordlist")

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        pass

    def cmd_makecldf(self, args):

        args.writer.cldf.add_component("CognateTable")
        args.writer.cldf.add_component("CognatesetTable")
        args.writer.cldf.add_component("LanguageTable")
        args.writer.cldf.add_component("ParameterTable")
        args.writer.cldf.add_columns("CognatesetTable", "Form")
        args.writer.cldf.remove_columns("FormTable", "Parameter_ID")
        args.writer.cldf.add_columns(
            "FormTable",
            {
                "name": "Parameter_ID",
                "required": True,
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#parameterReference",
                "dc:description": "A reference to the meaning denoted by the form",
                "datatype": "string",
                "separator": "; ",
            },
        )

        segments = open("etc/segments.txt").read()
        segment_list = [{"Grapheme": x, "mapping": x} for x in segments.split("\n")]
        t = Tokenizer(Profile(*segment_list))

        def segmentify(form):
            form = re.sub("[?()\[\]]", "", form)
            form = form.strip("-")
            return t(
                form.replace("-", "+")
            )  # morpheme boundaries are replaced with cognate boundaries

        lg_ids = []
        contained_sources = ["meira2010origin"]
        forms = pd.read_csv("raw/forms.csv", keep_default_na=False)
        forms = forms[(forms["Cognates"] != "")]

        # set morpheme IDs to lg + index where not present
        forms["ID"] = forms.apply(
            lambda x: f"""{x["Language_ID"]}-{x.name}""" if x["ID"] == "" else x["ID"],
            axis=1,
        )
        forms.set_index("ID", inplace=True)
        # assign cognacy information to morphologically complex forms

        cogsets = pd.read_csv("raw/cognatesets.csv", keep_default_na=False)
        cogsets.index = cogsets.index + 1
        cognum = dict(zip(cogsets["ID"], cogsets.index.astype(str)))

        def str2numcog(cogsets):
            return " ".join([cognum[x] for x in cogsets.split("+")])

        def check_cognates(row):
            if row["Cognates"].count("+") != row["Form"].count("+"):
                print(row)
            for cogset in row["Cognates"].split("+"):
                if cogset != "?" and cogset not in list(cogsets["ID"]):
                    print(f"Missing cognate set {cogset}:", row, sep="\n")

        forms.apply(check_cognates, axis=1)
        forms["Segments"] = forms["Form"].apply(segmentify)

        alignments = {}

        for abs_cog, abs_id in [("1", "1abs"), ("2", "2abs"), ("3ANA.ANIM", "3aabs")]:
            cog_df = forms[((forms["Cognateset_ID"] == abs_cog) & ~(forms["Language_ID"].str.contains("P")))]
            cog_df.reset_index(inplace=True)
            seglist = lingpy.align.multiple.Multiple(list(cog_df["Segments"]))
            seglist.align(method="progressive")
            cog_df["Alignment"] = seglist.alm_matrix
            # cog_df["Alignment"] = cog_df["Alignment"].apply(lambda x: " ".join(x))
            for rec in cog_df.to_dict("records"):
                args.writer.objects["CognateTable"].append(
                    {
                        "ID": f"""{rec["ID"]}-abs""",
                        "Form_ID": rec["ID"],
                        "Cognateset_ID": abs_id,
                        "Alignment": rec["Alignment"],
                    }
                )

        modern_forms = forms[~(forms["Language_ID"].str.contains("P"))]

        for i, row in cogsets.iterrows():
            if row["ID"] == "?":
                continue
            args.writer.objects["CognatesetTable"].append(
                {
                    "ID": slug(row["ID"]),
                    "Form": "*" + row["Form"],
                    "Description": row["Description"],
                }
            )
            if "abs" in row["ID"]:
                continue
            cog_df = cldfh.get_cognates(modern_forms, row["ID"], form_col="Segments")
            cog_df["Segments"] = cog_df["Form"].str.strip(" ")
            cog_df = cog_df[cog_df["Segments"] != ""]
            seglist = lingpy.align.multiple.Multiple(list(cog_df["Segments"]))
            seglist.align(method="progressive")
            cog_df["Alignment"] = seglist.alm_matrix
            cog_df["Alignment"] = cog_df["Alignment"].apply(lambda x: " ".join(x))
            for j, row_i in cog_df.iterrows():
                alignments[f"""{j}-{row_i["Slice"]}"""] = row_i["Alignment"]
        edictor_output = pd.DataFrame()

        for i, row in forms.iterrows():
            row["Parameter_ID"] = [slug(par) for par in row["Meaning"].split("; ")]
            args.writer.objects["FormTable"].append(
                {
                    "ID": i,
                    "Language_ID": row["Language_ID"],
                    "Form": row["Form"].replace("+", ""),
                    "Segments": row["Segments"].split(" "),
                    "Source": row["Source"].split("; "),
                    "Comment": row["Comments"],
                    "Parameter_ID": row["Parameter_ID"],
                }
            )
            lg_ids.append(row["Language_ID"])
            for source in row["Source"].split("; "):
                contained_sources.append(source.split("[")[0])
            if "P" in row["Language_ID"]:
                continue
            edictor_alignment = []
            for segment_slice, cog_id in enumerate(row["Cognates"].split("+")):
                if cog_id == "?":
                    edictor_alignment.append("-")
                    continue
                align_key = f"{i}-{segment_slice+1}"
                if align_key not in alignments:
                    alignment = ""
                else:
                    alignment = (alignments[align_key],)
                args.writer.objects["CognateTable"].append(
                    {
                        "ID": f"{i}_{segment_slice}",
                        "Form_ID": i,
                        "Cognateset_ID": slug(cog_id),
                        "Segment_Slice": str(segment_slice + 1),
                        "Alignment": alignment,
                    }
                )
                edictor_alignment.append(" ".join(alignment))
            for par in row["Parameter_ID"]:
                edictor_output = edictor_output.append(
                    {
                        "DOCULECT": row["Language_ID"],
                        "CONCEPT": slug(par),
                        "CONCEPTID": slug(par),
                        "IPA": row["Form"].replace("+", ""),
                        "SEGMENTS": segmentify(row["Form"]),
                        "COGIDS": str2numcog(row["Cognates"]),
                        "ALIGNMENT": " + ".join(edictor_alignment),
                    },
                    ignore_index=True,
                )

        lg_ids = list(set(lg_ids))
        for lg in crh.lg_order().keys():
            if lg in lg_ids:
                args.writer.objects["LanguageTable"].append(
                    {
                        "ID": lg,
                        "Name": crh.get_name(lg),
                        "Glottocode": crh.get_glottocode(lg),
                    }
                )

        meanings = pd.read_csv("raw/meanings.csv", keep_default_na=False)
        meanings["ID"] = meanings["ID"].apply(slug)
        for i, row in meanings.iterrows():
            args.writer.objects["ParameterTable"].append(row.to_dict())

        sources = self.etc_dir.read_bib("etc/cariban_references_out.bib")
        sources = [x for x in sources if x.id in contained_sources]
        args.writer.cldf.add_sources(*sources)
        edictor_output.index.name = "ID"
        edictor_output.to_csv("etc/pronouns_edictor.tsv", sep="\t")
