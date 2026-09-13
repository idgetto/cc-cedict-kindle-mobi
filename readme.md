# CC-CEDICT Chinese-English Dictionary for Kindle (mobi format)

## About

These scripts generate a `.mobi` file from the CC-CEDICT Chinese-English dictionary.

You can then load this `.mobi` file onto your Kindle to use it as a dictionary.

The generated dictionary includes pinyin and definitions for words.

This is a fork of [gkovacs/cc-cedict-kindle-mobi](https://github.com/gkovacs/cc-cedict-kindle-mobi) that replaces the original LiveScript/Node.js build with a small Python pipeline, so the only dependencies are Python 3 and kindlegen.

## Files

| File | Purpose |
| --- | --- |
| `cedict_1_0_ts_utf-8_mdbg.txt` | The CC-CEDICT source dictionary |
| `cedict_to_tab.py` | Converts the CC-CEDICT source into a Stardict-style tab file |
| `tab_to_opf.py` | Converts the tab file into the `.opf`/HTML files kindlegen expects |
| `build.sh` | Runs the full pipeline end to end |
| `output/` | Where the tab file, OPF, and HTML chunks are written |

## Requirements

- Python 3
- [kindlegen](#getting-kindlegen)

## Getting kindlegen

Amazon has discontinued the standalone kindlegen download, but it's still available two ways:

1. **Bundled with Kindle Previewer** (recommended): install [Kindle Previewer](https://www.amazon.com/Kindle-Previewer/b?ie=UTF8&node=21381691011) from Amazon, then find `kindlegen` inside the Previewer installation folder and copy it somewhere on your `PATH`.
2. **Archived standalone copies**: mirrors of the last standalone release (v2.9) are available on the [Internet Archive](https://archive.org/details/kindlegen2.9).

Once you have the `kindlegen` binary, make sure it's executable and on your `PATH` (e.g. `/usr/local/bin/kindlegen` on macOS/Linux) so `build.sh` can find it.

## Running

```bash
./build.sh
```

# Author

[Geza Kovacs](https://github.com/gkovacs)

# License

MIT

# Related

For version with zhuyin and jyutping (cantonese), see https://github.com/gkovacs/cantodict-kindle-mobi

