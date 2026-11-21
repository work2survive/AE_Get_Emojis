# AE Get Emojis (`AE_Get_Emojis.jsx`)

**Quickly search, index, and add full-color vector emojis to Adobe After Effects as native Shape Layers.**

> **[🚀 Launch Interactive Live Demo in Browser (`AE_JS_builder`)](https://work2survive.github.io/AE_JS_builder/?jsx=AE_Get_Emojis.jsx&autobuild=true)**

---

## Why This Tool Exists

Adobe After Effects text layers do not support color emoji font tables (`COLR/CPAL`, `SBIX`, `CBDT/CBLC`), causing emojis pasted into text layers to render as monochrome outlines or missing-glyph boxes (`□`).

**AE Get Emojis (`AE_Get_Emojis.jsx`)** solves this by indexing full-color vector emojis from **[OpenMoji](https://github.com/hfg-gmuend/openmoji)** and **[Twemoji](https://github.com/jdecked/twemoji)** into `.JSON` files inside the [`emojis/`](./emojis) subfolder and constructing 100% native, infinitely scalable **After Effects Shape Layers** (`ADBE Vector Group` + cubic Bézier `Shape` paths + `Fill` + `Stroke`).

---

## Key Features

### 1. `.JSON` Emoji Storage & Index in [`emojis/`](./emojis)
All emoji metadata, text emoticon mappings, and normalized `72×72` cubic Bézier vector shapes are stored and indexed in `.JSON` inside the [`emojis/`](./emojis) subfolder:

| File | Description |
| :--- | :--- |
| [`emojis/emoji_index.json`](./emojis/emoji_index.json) | Master catalog of **291 indexed emojis** with 1-based slider `index`, `hexcode` (`1F603`), `unicode` (`U+1F603`), `unicodeInt` (`128515`), `emoji` (`😃`), `name`, `group`, `tags`, and `emoticons`. |
| [`emojis/wikipedia_emoticons.json`](./emojis/wikipedia_emoticons.json) | Comprehensive Western sideways (`:D`, `:)`, `;)`, `:P`, `<3`, `</3`, `XD`, `:'(`, `>:(`, `D:`, `:O`, `:3`, `B-)`, `O:)`) and Eastern / Kaomoji (`¯\_(ツ)_/¯`, `( ͡° ͜ʖ ͡°)`, `ಠ_ಠ`, `T_T`, `\o/`, `o7`, `uwu`) lookup table sourced from [Wikipedia's List of Emoticons](https://en.wikipedia.org/wiki/List_of_emoticons). |
| [`emojis/openmoji_color.json`](./emojis/openmoji_color.json) | Handcrafted full-color + outline vector shapes from [hfg-gmuend/openmoji](https://github.com/hfg-gmuend/openmoji) (`CC BY-SA 4.0`). |
| [`emojis/twemoji_color.json`](./emojis/twemoji_color.json) | Flat full-color vector shapes from [jdecked/twemoji](https://github.com/jdecked/twemoji) (`CC BY 4.0`). |
| [`emojis/openmoji_black.json`](./emojis/openmoji_black.json) | Black wireframe / line-art vector shapes from [hfg-gmuend/openmoji](https://github.com/hfg-gmuend/openmoji). |
| [`emojis/emoji_schema.json`](./emojis/emoji_schema.json) | Formal JSON Schema for the `emojis/*.json` database files. |

---

### 2. Multi-Source Pulldown
Pick between 4 vector styles right from the **Source** dropdown:
1. **OpenMoji Color (`hfg-gmuend/openmoji`)** — Full handcrafted color fills with crisp black line-art outlines.
2. **Twemoji Flat Color (`jdecked/twemoji`)** — Clean flat vector shapes without black outlines.
3. **OpenMoji Flat (`Color Only, No Outlines`)** — OpenMoji color fills with the `#line` outline layer stripped.
4. **OpenMoji Black (`Line Art / Wireframe`)** — Pure black stroke wireframe vectors.

---

### 3. Search by Name, Unicode, Integer, Emoji Glyph, or Wikipedia Emoticon
Type any of the following into the **Search** input:
- **Text Emoticon** (from [Wikipedia: List of emoticons](https://en.wikipedia.org/wiki/List_of_emoticons)): `:D`, `:-D`, `:)`, `:-)`, `;)`, `:P`, `XD`, `<3`, `</3`, `:'(`, `>:(`, `D:`, `:O`, `:3`, `B-)`, `O:)`, `:/`, `:|`, `T_T`, `\o/`, `o7`, `¯\_(ツ)_/¯`, `( ͡° ͜ʖ ͡°)`, `ಠ_ಠ`, `uwu`
- **Emoji Name / Keyword**: `grinning`, `laugh`, `heart`, `fire`, `rocket`, `thumbs up`, `shrug`, `cat`, `pizza`, `trophy`
- **Unicode Hexadecimal**: `1F603`, `U+1F603`, `0x1F603`, `2764`
- **Unicode Integer**: `128515`, `128578`, `10084`, `128293`
- **Emoji Glyph**: `😃`, `🙂`, `❤️`, `🔥`, `🚀`, `👍`

Or pick directly from the **Wikipedia Emoticon Shortcuts** pulldown!

---

### 4. Slider Indexing & Unicode ↔ Integer Conversion
Every emoji is indexed both sequentially (`1 .. 291`) and by its **32-bit Unicode Integer** (`unicodeInt = parseInt(hexcode, 16)`):

$$\text{Unicode Hex } \mathtt{U+1F603} \quad \Longleftrightarrow \quad \mathtt{0x1F603}_{16} = \mathbf{128515}_{10}$$

- **Interactive UI Sliders & Converter**:
  - Scrub the **Emoji Index Slider** (`1 .. 291`) or **Unicode Int Slider** (`9728 .. 129782`).
  - Type a hex value in **Unicode Hex** (`U+1F525`) or a decimal integer in **Unicode Int** (`128293`) to convert bidirectionally in real time.
- **Layer Effect Sliders**:
  Every generated Shape Layer includes native After Effects Effect Controls:
  - `Emoji Index` (`ADBE Slider Control`)
  - `Emoji Unicode Int` (`ADBE Slider Control` — e.g. `128515` for `U+1F603`)
  - `Emoji Source (1=OM,2=TW,3=Flat,4=Blk)` (`ADBE Slider Control`)
  - `Emoji Size (px)` (`ADBE Slider Control` — rigged via expression to scale the master vector group)
  - `Outline Width %` (`ADBE Slider Control` — rigged via expression to scale all outline strokes)
  - `Show Outlines` (`ADBE Checkbox Control` — rigged via expression to toggle outline visibility)

---

### 5. Smart `Add Emoji` / `Replace Emoji` Button
- When **no Emoji layer is selected**, the primary button reads **`➕ Add Emoji`** and creates a new full-color Shape Layer in the active composition.
- When an **Emoji layer is selected** in the composition, the primary button automatically switches to **`🔄 Replace Emoji`** and swaps the emoji vector shapes and metadata in-place on the selected layer (preserving the layer's position and transform).
- If selection detection is unavailable in a host environment, the button falls back to **`➕ Add / Replace Emoji`**, alongside dedicated **`➕ Add New Layer`** and **`🔄 Replace Active`** buttons.

---

## Installation & Usage in Adobe After Effects

1. Clone or download this repository, keeping `AE_Get_Emojis.jsx` and the `emojis/` subfolder in the same directory:
   ```text
   AE_Get_Emojis/
   ├── AE_Get_Emojis.jsx
   ├── emojis/
   │   ├── emoji_index.json
   │   ├── wikipedia_emoticons.json
   │   ├── openmoji_color.json
   │   ├── twemoji_color.json
   │   ├── openmoji_black.json
   │   └── emoji_schema.json
   └── scripts/
       ├── build_emoji_db.py
       └── generate_jsx.py
   ```
   *(Note: `AE_Get_Emojis.jsx` also embeds a 48-emoji core fallback dataset and will automatically regenerate the `emojis/` folder if run standalone.)*
2. In Adobe After Effects, go to **File → Scripts → Run Script File...** and choose `AE_Get_Emojis.jsx` (or copy `AE_Get_Emojis.jsx` and `emojis/` into your `Scripts/ScriptUI Panels/` folder to dock it as a panel).

---

## Credits & Licenses
- **OpenMoji**: Emoji graphics and metadata from [hfg-gmuend/openmoji](https://github.com/hfg-gmuend/openmoji) licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- **Twemoji**: Emoji graphics from [jdecked/twemoji](https://github.com/jdecked/twemoji) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Emoticon Mappings**: Sourced from [Wikipedia — List of emoticons](https://en.wikipedia.org/wiki/List_of_emoticons) (`CC BY-SA 4.0`).
