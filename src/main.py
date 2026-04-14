import csv
import re

from tqdm import tqdm

import cccedict

dict = cccedict.CcCedict("data/cedict_1_0_ts_utf-8_mdbg.txt.gz")

with open("data/tofcl.csv") as f:
    words = list(csv.DictReader(f))

with open("data/tatoeba.tsv", encoding="utf-8-sig") as f:
    sentences = list(csv.reader(f, delimiter="\t"))

with open("dist/tofcl-definitions.csv", mode="w") as f:
    writer = csv.writer(f)
    missing = {
        "definition": 0,
        "simplified": 0,
        "example": 0,
    }
    for word in tqdm(words, dynamic_ncols=True):
        trad_stripped = re.sub(r"\(.*?\)|（.*?）|/.*$", "", word["traditional"]).strip()
        simp = dict.get_simplified(trad_stripped) or ""

        # get definitions of word
        definitions = [d.strip() for d in dict.get_definitions(trad_stripped) or []]
        if not definitions:
            simp2 = ""
            for c in trad_stripped:
                if s := dict.get_simplified(c):
                    simp2 += s
            definitions = [d.strip() for d in dict.get_definitions(simp2) or []]
            if definitions:
                simp = simp2

        # find example sentence
        example_sentence: tuple[str, str] = ("", "")
        for _, chn, _, eng in sentences:
            if trad_stripped in chn:
                example_sentence = (chn, eng)
                break

        missing["simplified"] += not simp
        missing["definition"] += not definitions
        missing["example"] += not example_sentence[0]

        writer.writerow([
            "level",
            "traditional",
            "simplified",
            "pinyin",
            "pos",
            "definition",
            "example_chn",
            "example_eng",
        ])
        entry = [
            word["level"],
            word["traditional"],
            simp,
            word["pinyin"],
            word["pos"],
            ", ".join(definitions),
            example_sentence[0],
            example_sentence[1],
        ]
        writer.writerow(entry)

    print("Missing:")
    print(f"{missing['definition']} definitions")
    print(f"{missing['simplified']} simplified")
    print(f"{missing['example']} examples")
