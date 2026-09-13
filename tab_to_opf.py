#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Converts a Stardict tabfile (<header>\t<definition> per line) into the
# HTML + OPF files needed to build a MobiPocket dictionary.
#
# Usage:
#   python3 tab2opf.py [-utf] DICTIONARY.tab
#
# Then convert the result with (wine) mobigen.exe DICTIONARY.opf
#
# Original Copyright (C) 2007 - Klokan Petr Pridal (www.klokan.cz)
# Licensed under the GNU Library General Public License v2 or later.

import argparse
import math
import os
import string
from unicodedata import combining, decomposition, normalize

VERSION = "0.2"
ENTRIES_PER_FILE = 10000


# ---------------------------------------------------------------------------
# Unicode -> ASCII normalization
#
# MobiPocket's non-UTF index needs plain ASCII sort keys, so any character
# outside ASCII has to be mapped down to its closest ASCII equivalent.
# ---------------------------------------------------------------------------

# Hand-made table from PloneTool.py
MAPPING_CUSTOM = {138: "s", 142: "z", 154: "s", 158: "z", 159: "Y"}

# UnicodeData.txt does not contain normalization of Greek letters.
MAPPING_GREEK = {
    912: "i", 913: "A", 914: "B", 915: "G", 916: "D", 917: "E", 918: "Z",
    919: "I", 920: "TH", 921: "I", 922: "K", 923: "L", 924: "M", 925: "N",
    926: "KS", 927: "O", 928: "P", 929: "R", 931: "S", 932: "T", 933: "Y",
    934: "F", 936: "PS", 937: "O", 938: "I", 939: "Y", 940: "a", 941: "e",
    943: "i", 944: "y", 945: "a", 946: "b", 947: "g", 948: "d", 949: "e",
    950: "z", 951: "i", 952: "th", 953: "i", 954: "k", 955: "l", 956: "m",
    957: "n", 958: "ks", 959: "o", 960: "p", 961: "r", 962: "s", 963: "s",
    964: "t", 965: "y", 966: "f", 968: "ps", 969: "o", 970: "i", 971: "y",
    972: "o", 973: "y",
}

# This may be specific to German...
MAPPING_TWO_CHARS = {
    140: "O", 156: "o", 196: "A", 246: "o", 252: "u", 214: "O",
    228: "a", 220: "U", 223: "s", 230: "e", 198: "E",
}

MAPPING_LATIN_CHARS = {
    192: "A", 193: "A", 194: "A", 195: "a", 197: "A", 199: "C", 200: "E",
    201: "E", 202: "E", 203: "E", 204: "I", 205: "I", 206: "I", 207: "I",
    208: "D", 209: "N", 210: "O", 211: "O", 212: "O", 213: "O", 215: "x",
    216: "O", 217: "U", 218: "U", 219: "U", 221: "Y", 224: "a", 225: "a",
    226: "a", 227: "a", 229: "a", 231: "c", 232: "e", 233: "e", 234: "e",
    235: "e", 236: "i", 237: "i", 238: "i", 239: "i", 240: "d", 241: "n",
    242: "o", 243: "o", 244: "o", 245: "o", 248: "o", 249: "u", 250: "u",
    251: "u", 253: "y", 255: "y",
}

# Feel free to add new user-defined mappings above; just fold them in here too.
UNICODE_TO_ASCII = {
    **MAPPING_CUSTOM,
    **MAPPING_GREEK,
    **MAPPING_TWO_CHARS,
    **MAPPING_LATIN_CHARS,
}

# On OpenBSD, string.whitespace has a non-standard implementation.
# See http://plone.org/collector/4704 for details.
WHITESPACE = "".join(c for c in string.whitespace if ord(c) < 128)
ALLOWED_CHARS = string.ascii_letters + string.digits + string.punctuation + WHITESPACE


def normalize_unicode(text: bytes, encoding: str = "humanascii") -> bytes:
    """
    Normalizes unicode characters down to plain ASCII letters, digits,
    punctuation, and whitespace. Case is preserved. Returns UTF-8 encoded
    bytes containing only characters valid in the target encoding.
    """
    target_encoding = "ascii" if encoding == "humanascii" else encoding

    result = []
    for char in text.decode("utf-8"):
        if encoding == "humanascii" and char in ALLOWED_CHARS:
            result.append(char)
            continue

        try:
            char.encode(target_encoding, "strict")
            result.append(char)
            continue
        except UnicodeEncodeError:
            pass

        ordinal = ord(char)
        if ordinal in UNICODE_TO_ASCII:
            result.append(UNICODE_TO_ASCII[ordinal])
        elif decomposition(char) or len(normalize("NFKD", char)) > 1:
            decomposed = normalize("NFKD", char)
            without_accents = "".join(c for c in decomposed if not combining(c))
            result.append("".join(c for c in without_accents if c in ALLOWED_CHARS))
        else:
            # Unknown character: fall back to its hex code point.
            result.append("%x" % ordinal)

    return "".join(result).encode("utf-8")


# ---------------------------------------------------------------------------
# OPF / HTML templates
# ---------------------------------------------------------------------------

HTML_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns:idx="www.mobipocket.com" xmlns:mbp="www.mobipocket.com" xmlns:xlink="http://www.w3.org/1999/xlink">
  <body>
    <mbp:pagebreak/>
"""

HTML_FOOTER = """
  </body>
</html>
"""

HTML_ENTRY = """      <idx:entry name="word" scriptable="yes">
          <idx:orth>{headword}</idx:orth><idx:key key="{sort_key}"> {definition}
      </idx:entry>
      <mbp:pagebreak/>
"""

OPF_HEAD = """<?xml version="1.0"?><!DOCTYPE package SYSTEM "oeb1.ent">

<!-- the command line instruction 'prcgen dictionary.opf' will produce the dictionary.prc file in the same folder-->
<!-- the command line instruction 'mobigen dictionary.opf' will produce the dictionary.mobi file in the same folder-->

<package unique-identifier="uid" xmlns:dc="Dublin Core">

<metadata>
\t<dc-metadata>
\t\t<dc:Identifier id="uid">{name}</dc:Identifier>
\t\t<!-- Title of the document -->
\t\t<dc:Title><h2>{title}</h2></dc:Title>
\t\t<dc:Language>EN</dc:Language>
\t</dc-metadata>
\t<x-metadata>
"""

OPF_NON_UTF_OUTPUT = """\t\t<output encoding="Windows-1252" flatten-dynamic-dir="yes"/>"""

OPF_MIDDLE = """
\t\t<DictionaryInLanguage>zh-cn</DictionaryInLanguage>
\t\t<DictionaryOutLanguage>en-us</DictionaryOutLanguage>
\t</x-metadata>
</metadata>

<!-- list of all the files needed to produce the .prc file -->
<manifest>
"""

OPF_MANIFEST_ITEM = ' <item id="dictionary{index}" href="{name}{index}.html" media-type="text/x-oeb1-document"/>\n'

OPF_SPINE_START = """</manifest>


<!-- list of the html files in the correct order  -->
<spine>
"""

OPF_SPINE_ITEM = "\t<itemref idref=\"dictionary{index}\"/>\n"

OPF_END = """</spine>

<tours/>
</package>
"""


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def format_entry(dt: bytes, dd: bytes, use_utf_index: bool) -> tuple[str, str]:
    """
    Prepares one dictionary entry for the HTML file. Returns
    (headword, entry_html). `dt` is the headword, `dd` is its definition;
    both come in as raw bytes straight from the tab file.
    """
    if not use_utf_index:
        dt = normalize_unicode(dt, "cp1252")
        dd = normalize_unicode(dd, "cp1252")

    sort_key = normalize_unicode(dt).decode("utf-8")
    headword = dt.decode("utf-8")

    definition = dd.decode("utf-8")
    # The tab file stores line breaks within a definition as the literal
    # two-character sequence "\n" (and literal backslashes as "\\"), so
    # unescape those into real HTML line breaks.
    definition = definition.replace("\\\\", "\\").replace("\\n", "<br/>\n")

    entry_html = HTML_ENTRY.format(headword=headword, sort_key=sort_key, definition=definition)
    return headword, entry_html


def generate_html_files(input_path: str, output_dir: str, output_name: str, use_utf_index: bool) -> int:
    """
    Reads the tab file and writes it out as a series of HTML files, each
    holding up to ENTRIES_PER_FILE entries. Returns the total number of
    entries written.
    """
    entry_count = 0
    current_file = None

    with open(input_path, "rb") as tab_file:
        for raw_line in tab_file:
            if entry_count % ENTRIES_PER_FILE == 0:
                if current_file:
                    current_file.write(HTML_FOOTER)
                    current_file.close()
                chunk_index = entry_count // ENTRIES_PER_FILE
                chunk_path = os.path.join(output_dir, f"{output_name}{chunk_index}.html")
                current_file = open(chunk_path, "w", encoding="utf-8")
                current_file.write(HTML_HEADER)

            headword, entry_html = format_entry(*raw_line.split(b"\t", 1), use_utf_index)
            current_file.write(entry_html)

            entry_count += 1

    if current_file:
        current_file.write(HTML_FOOTER)
        current_file.close()

    return entry_count


def write_opf_file(output_dir: str, output_name: str, entry_count: int, use_utf_index: bool) -> None:
    """Writes the .opf manifest tying together all the generated HTML files."""
    num_chunks = math.ceil(entry_count / ENTRIES_PER_FILE) if entry_count else 0
    opf_path = os.path.join(output_dir, f"{output_name}.opf")

    with open(opf_path, "w", encoding="utf-8") as opf_file:
        opf_file.write(OPF_HEAD.format(name=output_name, title="CEDICT Chinese-English"))
        if not use_utf_index:
            opf_file.write(OPF_NON_UTF_OUTPUT)
        opf_file.write(OPF_MIDDLE)

        for index in range(num_chunks):
            opf_file.write(OPF_MANIFEST_ITEM.format(index=index, name=output_name))

        opf_file.write(OPF_SPINE_START)
        for index in range(num_chunks):
            opf_file.write(OPF_SPINE_ITEM.format(index=index))
        opf_file.write(OPF_END)


def parse_args():
    parser = argparse.ArgumentParser(
        description="tab2opf (Stardict -> MobiPocket) v%s" % VERSION,
    )
    parser.add_argument("-utf", action="store_true", help="build a UTF-8 index instead of Windows-1252")
    parser.add_argument("tab_file", help="the Stardict .tab file to convert")
    return parser.parse_args()


def main():
    args = parse_args()
    output_name = os.path.splitext(os.path.basename(args.tab_file))[0]

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    entry_count = generate_html_files(args.tab_file, output_dir, output_name, args.utf)
    write_opf_file(output_dir, output_name, entry_count, args.utf)
    print(f"Wrote {entry_count:,} entries.")


if __name__ == "__main__":
    main()
