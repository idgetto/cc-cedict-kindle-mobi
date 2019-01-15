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

This runs the full pipeline:

1. `cedict_to_tab.py` converts the CC-CEDICT source into a tab file.
2. `tab_to_opf.py` converts the tab file into OPF/HTML.
3. `kindlegen` compiles those into `output/dictionary.mobi`, which is then copied to the repo root as `dictionary.mobi`.

If your CC-CEDICT source file has a different name or location, pass it as an argument:

```bash
./build.sh path/to/cedict-source.txt
```

## Adding the dictionary to your Kindle

1. Connect your Kindle to your computer via USB. It should show up as a removable drive.
2. Drag `dictionary.mobi` into the Kindle's `documents/dictionaries` folder (this is a regular file transfer, distinct from Amazon's "Download & Transfer via USB" feature for purchased books, and still works for sideloading your own files).
3. Safely eject the Kindle and disconnect it.
4. On the Kindle, go to **Settings → Device Options → Language & Dictionaries → Dictionaries**, find the entry for Chinese, and set this dictionary as the default.
5. Open a Chinese-language book and long-press a word to confirm the lookup works.

## Author

[Geza Kovacs](https://github.com/gkovacs)

Python pipeline rewrite by [idgetto](https://github.com/idgetto/cc-cedict-kindle-mobi)

## License

MIT

## Related

For a version with zhuyin and jyutping (Cantonese), see https://github.com/gkovacs/cantodict-kindle-mobi