from namedtuples import *
import re

hex_to_int = lambda e: int(e, 16)


def cheung_bauer(e):
    rs, cj, jp = e.split(";")
    r, s = rs.split("/")
    return CheungBauer(int(r), int(s), cj, tuple(jp.split(",")))


def cihai_t(e):
    page, row_position = e.split(".")
    row = row_position[0]
    position = row_position[1:]
    return CihaiT(*map(int, [page, row, position]))


cns = lambda e: hex_to_int(e.replace("-", ""))

codepoint = lambda e: chr(hex_to_int(e[2:]))


def dae_jaweon(e):
    page, pos = e.split(".")
    virtual = bool(pos[-1])
    position = pos[:-1]
    return DaeJaweon(int(page), int(position), virtual)

dictionary_index = lambda e: DictionaryIndex(*map(int, e.split(".")))


# the phonetic could be an int, if we figure out what the "a" is for
fenn = lambda e: Fenn(e[:-1], e[1])

ku_ten = lambda e: (int(e[:2]), int(e[2:]))


def hangul(e):
    pronunciation, sources = e.split(":")
    return Hangul(pronunciation, tuple(sources))


def hanyu(e):
    volume_page, pos = e.split(".")
    volume = int(volume_page[0])
    page = int(volume_page[1:])
    position = int(pos[:-1])
    virtual_position = int(pos[-1])
    return HanYu(volume, page, position, virtual_position)


def hanyu_pinlu(e):
    pronunciation, frequency = re.search(r"(.+)\((\d+)\)", e).groups()
    return HanyuPinlu(pronunciation, int(frequency))


def hanyu_pinyin(e):
    locations, pronunciations = e.split(":")
    return HanyuPinyin(
        tuple(map(hanyu, locations.split(","))), tuple(pronunciations.split(","))
    )


def hdz_rad_break(e):
    radical, location = e.split(":")
    return HDZRadBreak(radical[0], hanyu(location))


def irg_dae_jaweon(e):
    page, pos = e.split(".")
    return IRGDaeJaweon(int(page), int(pos[:-1]), bool(int(pos[-1])))


def irg_hanyu_da_zidian(e):
    location = hanyu(e)
    return IRGHanyuDaZidian(
        location.volume,
        location.page,
        location.position,
        bool(location.virtual_position),
    )

def kangxi(e):
    page, pos = e.split(".")
    return KangXi(int(page), int(pos[:-1]), bool(int(pos[-1])))

def irg_source(e):
    try:
        source, location = e.split("-")
    except ValueError:
        source = e
        location = ""
    if source == "GZA":
        source = source + "-" + location[0]
        location = location[1:]
    return IRGSource(source, location)

def jinmeiyo_kanji(e):
    try:
        year, cp = e.split(":")
        standard_form = chr(hex_to_int(cp[2:]))
    except ValueError:
        year = e
        standard_form = ""
    return JinmeiyoKanji(year, standard_form)

def karlgren(e):
    interpolated = e[-1] == "*"
    if interpolated:
        index = e[:-1]
    else:
        index = e
    return Karlgren(index, interpolated)

def meyer_wempe(e):
    index, subentry = re.search(r"(\d+)([a-t\*]?)", e).groups()
    return MeyerWempe(int(index), subentry)

def phonetic(e):
    phonetic_class, subclass = re.search(r"(\d+)(.*)", e).groups()
    unlisted = False
    error = False
    if "*" in subclass:
        unlisted = True
        subclass = subclass.replace("*", "")
    if "x" in subclass:
        error = True
        subclass = subclass.replace("x", "")
    return Phonetic(phonetic_class, subclass, unlisted, error)

def rs_adobe_japan1_6(e):
    variant_mark, cid, rs = e.split("+")
    variant = variant_mark == "V"
    radical, radical_strokes, residual_strokes = rs.split(".")
    return RSAdobe_Japan1_6(variant, int(cid), int(radical), int(radical_strokes), int(residual_strokes)) 

def rs_kangxi(e):
    radical, strokes = e.split(".")
    return RSKangXi(int(radical), int(strokes))

def rs_unicode(e):
    radical, strokes = e.split(".")
    simplified_radical = False
    if radical.endswith("'"):
        simplified_radical = True
        radical = radical[:-1]
    return RSUnicode(int(radical), simplified_radical, int(strokes))

def variant(e):
    try:
        character, source_line = e.split("<")
    except ValueError:
        return Variant(codepoint(e), ())
    sources = []
    for source_entry in source_line.split(","):
        same = improper = preferred = traditional = simplified = False
        try:
            source, field_tags = source_entry.split(":")
            same = "T" in field_tags
            improper = "B" in field_tags
            preferred = "Z" in field_tags
            traditional = "F" in field_tags
            simplified = "J" in field_tags
        except ValueError:
            source = source_entry
        sources.append(VariantSource(source, same, improper, preferred, traditional, simplified))
    return Variant(codepoint(character), tuple(sources))

def strange(e):
    try:
        category, refline = e.split(":", 1)
    except ValueError:
        return Strange(e, (), 0)
    if category == "S":
        return Strange(e, (), int(refline))
    reference_characters = tuple(map(codepoint, refline.split(":")))
    return Strange(category, reference_characters, 0)

def tang(e):
    if e.startswith("*"):
        return Tang(e[1:], True)
    else:
        return Tang(e, False)

def tghz2013(e):
    location_data, pronunciation = e.split(":")
    locations = []
    for location_entry in location_data.split(","):
        page, pos = location_entry.split(".")
        position = pos[:-1]
        variant = pos[-1]
        locations.append(TGHZ2013Location(int(page), int(position), int(variant)))
    return TGHZ2013(tuple(locations), pronunciation)

def xhc1983(e):
    location_data, pronunciation = e.split(":")
    locations = []
    for location_entry in location_data.split(","):
        page, pos = location_entry.split(".")
        substitute = pos.endswith("*")
        if substitute:
            pos = pos[:-1]
        position = pos[:-1]
        variant = pos[-1]
        locations.append(XHC1983Location(int(page), int(position), int(variant), substitute))
    return XHC1983(tuple(locations), pronunciation)
