import urllib.request
import os
from pathlib import Path
import zipfile
from glob import glob
import pickle
import lzma

from bs4 import BeautifulSoup

import parsers as p
from namedtuples import *

VERSION = "15.0.0"
UCD_BASE_URL = f"https://www.unicode.org/Public/{VERSION}/ucd/"
ZIP_FILENAME = "Unihan.zip"
TR38_BASE_URL = f"https://www.unicode.org/reports/tr38/"
TR38_VERSION = "33"
TR38_FILENAME = f"tr38-{TR38_VERSION}.html"
DATA_DIR = Path("Unihan_data")

os.makedirs(DATA_DIR, exist_ok=True)
urllib.request.urlretrieve(
    UCD_BASE_URL + ZIP_FILENAME, filename=DATA_DIR / ZIP_FILENAME
)
with zipfile.ZipFile(DATA_DIR / ZIP_FILENAME) as zip_file:
    zip_file.extractall(DATA_DIR)

multiple_entries = set()

urllib.request.urlretrieve(
    TR38_BASE_URL + TR38_FILENAME, filename=DATA_DIR / TR38_FILENAME
)
with open(DATA_DIR / TR38_FILENAME) as file:
    soup = BeautifulSoup(file, "lxml")
    for a in soup.find_all("a", id=True):
        if not a["id"].startswith("k"):
            raise ValueError("tr38.html may have changed format")
        delimiter = (
            a.find_parent("table")
            .find(text="Delimiter")
            .parent.find_next_sibling("td")
            .text
        )
        if delimiter == "space":
            multiple_entries.add(a["id"])
        elif delimiter == "N/A":
            continue
        else:
            raise ValueError("tr38.html may have changed format")


property_parsers = {
    "kAccountingNumeric": int,
    "kBigFive": p.hex_to_int,
    "kCCCII": p.hex_to_int,
    "kCheungBauer": p.cheung_bauer,
    "kCheungBauerIndex": p.dictionary_index,
    "kCihaiT": p.cihai_t,
    "kCNS1986": p.cns,
    "kCNS1992": p.cns,
    "kCompatibilityVariant": p.codepoint,
    "kCowles": float,
    "kDaeJaweon": p.dae_jaweon,
    "kEACC": p.hex_to_int,
    "kFenn": p.fenn,
    "kFennIndex": p.dictionary_index,
    "kFrequency": int,
    "kGradeLevel": int,
    "kHangul": p.hangul,
    "kHanYu": p.hanyu,
    "kHanyuPinlu": p.hanyu_pinlu,
    "kHanyuPinyin": p.hanyu_pinyin,
    "kHDZRadBreak": p.hdz_rad_break,
    "kHKGlyph": int,
    "kHKSCS": p.hex_to_int,
    "kIBMJapan": p.hex_to_int,
    "kIICore": lambda e: IICore(e[0], tuple(e[1:])),
    "kIRGDaeJaweon": p.irg_dae_jaweon,
    "kIRGHanyuDaZidian": p.irg_hanyu_da_zidian,
    "kIRGKangXi": p.kangxi,
    "kJinmeiyoKanji": p.jinmeiyo_kanji,
    "kJis0": p.ku_ten,
    "kJIS0213": lambda e: tuple(map(int, e.split(","))),
    "kJis1": p.ku_ten,
    "kKangXi": p.kangxi,
    "kKarlgren": p.karlgren,
    "kKoreanEducationHanja": int,
    "kKoreanName": int,
    "kKPS0": p.hex_to_int,
    "kKPS1": p.hex_to_int,
    "kKSC0": p.hex_to_int,
    "kKSC1": p.hex_to_int,
    "kLau": int,
    "kMainlandTelegraph": int,
    "kMeyerWempe": p.meyer_wempe,
    "kNelson": int,
    "kOtherNumeric": int,
    "kPhonetic": p.phonetic,
    "kPrimaryNumeric": int,
    "kPseudoGB1": p.ku_ten,
    "kRSAdobe_Japan1_6": p.rs_adobe_japan1_6,
    "kRSKangXi": p.rs_kangxi,
    "kRSUnicode": p.rs_unicode,
    "kSBGY": p.dictionary_index,
    "kSemanticVariant": p.variant,
    "kSimplifiedVariant": p.codepoint,
    "kSepcializedSemanticVariant": p.variant,
    "kSpoofingVariant": p.codepoint,
    "kStrange": p.strange,
    "kTaiwanTelegraph": int,
    "kTang": p.tang,
    "kTGH": lambda e: TGH(int(e.split(":")[0]), int(e.split(":")[1])),
    "kTGHZ2013": p.tghz2013,
    "kTraditionalVariant": p.codepoint,
    "kUnihanCore2020": tuple,
    "kXHC1983": p.xhc1983,
    "kZVariant": p.variant,
}

for n in [0, 1, 3, 5, 7, 8]:
    property_parsers[f"kGB{n}"] = p.ku_ten

sources = ["G", "H", "J", "KP", "K", "M", "S", "T", "UK", "U", "V"]
source_map = {code: code for code in sources}
source_map["UK"] = "B"
source_map["KP"] = "P"

for s in ["G", "H", "J", "KP", "K", "M", "S", "T", "UK", "U", "V"]:
    property_parsers[f"kIRG_{s}Source"] = p.irg_source


def parse_cp(cp):
    cp = cp[2:]
    return chr(int(cp, base=16))


def parse_datafile(datafile, data_destination):
    for i, line in enumerate(datafile.readlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            cp, prop, entry = line.split("\t")
        except ValueError:
            raise ValueError(f"Data file syntax error on line {i}")
        char = parse_cp(cp)
        if prop in multiple_entries:
            entries = entry.split(" ")
            try:
                entry = tuple(map(property_parsers[prop], entries))
            except KeyError:
                entry = tuple(entries)
        else:
            try:
                entry = property_parsers[prop](entry)
            except KeyError:
                pass
        if char not in data_destination:
            data_destination[char] = {}
        data_destination[char][prop] = entry


unihan_data = {}
for datafile_path in glob(str(DATA_DIR / "Unihan_*.txt")):
    with open(datafile_path) as datafile:
        parse_datafile(datafile, unihan_data)

for char in unihan_data:
    try:
        total_strokes = unihan_data[char]["kTotalStrokes"]
        if len(total_strokes) == 1:
            unihan_data[char]["kTotalStrokes"] = (
                TotalStrokes("G", int(total_strokes[0])),
                TotalStrokes("T", int(total_strokes[0])),
            )
        else:
            unihan_data[char]["kTotalStrokes"] = (
                TotalStrokes("G", int(total_strokes[0])),
                TotalStrokes("T", int(total_strokes[1])),
            )
    except KeyError:
        pass
    try:
        alternate_total_stroke_entries = unihan_data[char]["kAlternateTotalStrokes"]
    except KeyError:
        continue
    ats_data = {}
    for source in sources:
        if source in {"G", "T"}:
            continue
        if f"kIRG_{source}Source" in unihan_data[char]:
            ats_data[source_map[source]] = unihan_data[char]["kTotalStrokes"][0].strokes
    for entry in alternate_total_stroke_entries:
        if entry == "-":
            continue
        else:
            strokes, source_list = entry.split(":")
            for source in source_list:
                ats_data[source] = strokes
    alternate_total_strokes = sorted(
        (TotalStrokes(source, int(strokes)) for source, strokes in ats_data.items()),
        key=lambda e: e.strokes
    )
    unihan_data[char]["kAlternateTotalStrokes"] = alternate_total_strokes

with lzma.open("unihan_data.pickle.xz", "wb") as f:
    pickle.dump(unihan_data, f)
