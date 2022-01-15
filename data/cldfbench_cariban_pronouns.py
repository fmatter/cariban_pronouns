import pathlib
import pandas as pd
from cldfbench import Dataset as BaseDataset
from segments import Profile, Tokenizer
import re
import cldf_helpers as cldfh
import lingpy
from clldutils.misc import slug
import cariban_helpers as crh

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

        edictor_output = pd.DataFrame()
        args.writer.cldf.add_component("CognateTable")
        args.writer.cldf.add_component("CognatesetTable")
        args.writer.cldf.add_component("LanguageTable")
        args.writer.cldf.add_component("ParameterTable")
        args.writer.cldf.add_component("ContributionTable")
        # args.writer.cldf.add_component("ContributorTable")
        args.writer.cldf.add_columns(
            "FormTable",
            "Contribution_ID",
        )
        args.writer.cldf.add_foreign_key(
            "FormTable", "Contribution_ID", "ContributionTable", "ID"
        )
        args.writer.cldf.add_columns(
            "CognatesetTable",
            "Form",
        )
        args.writer.cldf.add_columns(
            "CognateTable",
            "Contribution_ID",
        )
        args.writer.cldf.add_foreign_key(
            "CognateTable", "Contribution_ID", "ContributionTable", "ID"
        )
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

        args.writer.objects["ContributionTable"].append(
            {
                "ID": "pronouns",
                "Name": "Cariban pronouns",
                "Description": "Pronominal and demonstrative forms",
                "Contributor": "fm",
            }
        )

        segments = open("etc/segments.txt").read()
        segment_list = [{"Grapheme": x, "mapping": x} for x in segments.split("\n")]
        t = Tokenizer(Profile(*segment_list))

        def segmentify(form):
            form = re.sub("[?()\[\]]", "", form)
            return t(form)

        lg_ids = []
        found_sources = []
        forms = pd.read_csv("raw/forms.csv", keep_default_na=False)
        forms = forms[forms["Cognates"] != ""]
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
            cog_df = cldfh.get_cognates(forms, row["ID"])
            cog_df["Segments"] = cog_df["Form"].apply(segmentify)
            cog_df = cog_df[cog_df["Segments"] != ""]
            seglist = lingpy.align.multiple.Multiple(list(cog_df["Segments"]))
            seglist.align(method="progressive")
            cog_df["Alignment"] = seglist.alm_matrix
            cog_df["Alignment"] = cog_df["Alignment"].apply(lambda x: " ".join(x))
            for j, row_i in cog_df.iterrows():
                alignments[f"""{j}-{row_i["Slice"]}"""] = row_i["Alignment"]

        for i, row in forms.iterrows():
            args.writer.objects["FormTable"].append(
                {
                    "ID": i,
                    "Language_ID": row["Language_ID"],
                    "Parameter_ID": [slug(par) for par in row["Parameter_ID"].split("; ")],
                    "Form": row["Form"].replace("+", ""),
                    "Segments": segmentify(row["Form"]).split(" "),
                    "Source": row["Source"].split("; "),
                    "Comment": row["Comments"],
                    "Contribution_ID": "pronouns",
                }
            )
            edictor_alignment = []
            for segment_slice, cog_id in enumerate(row["Cognates"].split("+")):
                if cog_id == "?":
                    edictor_alignment.append("-")
                    continue
                align_key = f"{i}-{segment_slice+1}"
                if align_key not in alignments:
                    alignment = ""
                else:
                    alignment = alignments[align_key],
                args.writer.objects["CognateTable"].append(
                    {
                        "ID": f"{i}_{segment_slice}",
                        "Form_ID": i,
                        "Cognateset_ID": slug(cog_id),
                        "Segment_Slice": str(segment_slice + 1),
                        "Alignment": alignment,
                        "Contribution_ID": "pronouns",
                    }
                )
                edictor_alignment.append(" ".join(alignment))
            for par in row["Parameter_ID"].split("; "):
                edictor_output = edictor_output.append(                {
                        "DOCULECT": row["Language_ID"],
                        "CONCEPT": slug(par),
                        "CONCEPTID": slug(par),
                        "IPA": row["Form"].replace("+", ""),
                        "SEGMENTS": segmentify(row["Form"]),
                        "COGIDS": str2numcog(row["Cognates"]),
                        "ALIGNMENT": " + ".join(edictor_alignment)
                    }, ignore_index=True)
            lg_ids.append(row["Language_ID"])
            for source in row["Source"].split("; "):
                found_sources.append(source.split("[")[0])

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
        # languages = pd.read_csv("raw/languages.csv")
        # for i, row in languages.iterrows():
        #     if row["ID"] in lg_ids:
        #         args.writer.objects["LanguageTable"].append(
        #             {
        #                 "ID": row["ID"],
        #                 "Name": row["Orthographic"],
        #                 "Glottocode": row["Glottocode"],
        #             }
        #         )

        meanings = pd.read_csv("raw/meanings.csv", keep_default_na=False)
        meanings["ID"] = meanings["ID"].apply(slug)
        for i, row in meanings.iterrows():
            args.writer.objects["ParameterTable"].append(row.to_dict())

        sources = self.etc_dir.read_bib("cariban_references_out.bib")
        sources = [x for x in sources if x.id in found_sources]
        args.writer.cldf.add_sources(*sources)
        edictor_output.index.name="ID"
        edictor_output.to_csv("etc/pronouns_edictor.tsv", sep="\t")