import re

INPUT_FILE = "cedict_1_0_ts_utf-8_mdbg.txt"
OUTPUT_FILE = "output/dictionary.txt"

# Each dictionary entry looks like:
#   伴侶 伴侣 [ban4 lu:3] /companion/mate/partner/
#   traditional simplified [pinyin] /def1/def2/.../
ENTRY_PATTERN = re.compile(r"^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.+)/\s*$")

# The output file has one line per word. Any line breaks *inside* a
# word's definitions are therefore written as the literal two-character
# sequence "\n" rather than a real newline - only the newlines between
# different words' lines are real.
LINE_BREAK = "\\n"


def parse_entry(line):
    if line.startswith("#"):
        return None

    match = ENTRY_PATTERN.match(line)
    if not match:
        return None

    traditional, simplified, pinyin, raw_definitions = match.groups()
    definitions = [d for d in raw_definitions.split("/") if d]

    return {
        "traditional": traditional,
        "simplified": simplified,
        "pinyin": pinyin.strip(),
        "definitions": definitions,
    }


def add_definitions(word_to_pinyin_to_defs, word, pinyin, definition_block):
    pinyin_to_defs = word_to_pinyin_to_defs.setdefault(word, {})
    pinyin_to_defs.setdefault(pinyin, []).append(definition_block)


def build_dictionary(lines):
    """
    Reads every entry and builds:
     - simplified_to_traditional / traditional_to_simplified: lookup maps
       for words that are written differently in the two scripts
     - word_to_pinyin_to_defs: for every word (simplified or traditional),
       its pronunciations and the definition blocks for each one
    """
    simplified_to_traditional = {}
    traditional_to_simplified = {}
    word_to_pinyin_to_defs = {}

    for line in lines:
        entry = parse_entry(line)
        if entry is None:
            continue

        traditional = entry["traditional"]
        simplified = entry["simplified"]
        pinyin = entry["pinyin"]
        definition_block = LINE_BREAK.join(entry["definitions"])
        has_distinct_forms = traditional != simplified

        if has_distinct_forms:
            traditional_to_simplified.setdefault(traditional, simplified)
            simplified_to_traditional.setdefault(simplified, traditional)
            add_definitions(word_to_pinyin_to_defs, simplified, pinyin, definition_block)
            add_definitions(word_to_pinyin_to_defs, traditional, pinyin, definition_block)
        else:
            add_definitions(word_to_pinyin_to_defs, simplified, pinyin, definition_block)

    return simplified_to_traditional, traditional_to_simplified, word_to_pinyin_to_defs


def find_variant_form(word, simplified_to_traditional, traditional_to_simplified):
    """
    A word written differently in simplified vs. traditional Chinese has a
    "variant form" - the other version of itself - shown in brackets before
    its first pronunciation, e.g. "[估量] (gu1 liang5)". When a word shows
    up as both a simplified and a traditional form elsewhere in the
    dictionary, the traditional-side mapping wins, matching the original
    script's behavior.
    """
    if word in traditional_to_simplified:
        return traditional_to_simplified[word]
    if word in simplified_to_traditional:
        return simplified_to_traditional[word]
    return None


def format_definition_block(pinyin_to_defs, variant_form):
    """
    Builds the definition block for one word, e.g.:
      [估量] (gu1 liang5)
      to estimate
      to assess
    """
    lines = []
    is_first_pinyin = True

    for pinyin, definition_blocks in pinyin_to_defs.items():
        prefix = f"[{variant_form}] " if is_first_pinyin and variant_form else ""
        lines.append(f"{prefix}({pinyin})")
        lines.extend(definition_blocks)
        is_first_pinyin = False

    return LINE_BREAK.join(lines)


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        lines = f.read().split("\n")

    simplified_to_traditional, traditional_to_simplified, word_to_pinyin_to_defs = (
        build_dictionary(lines)
    )

    output_lines = []
    for word, pinyin_to_defs in word_to_pinyin_to_defs.items():
        variant_form = find_variant_form(
            word, simplified_to_traditional, traditional_to_simplified
        )
        definition_block = format_definition_block(pinyin_to_defs, variant_form)
        output_lines.append(f"{word}\t{definition_block}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))


if __name__ == "__main__":
    main()
