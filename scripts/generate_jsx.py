#!/usr/bin/env python3
"""
Generates AE_Get_Emojis.jsx with an embedded fallback subset of emojis
and full support for loading emojis/*.json in both Adobe After Effects
and the AE_JS_builder web environment.
"""

import json
import os

REPO_DIR = "/home/antigravity/work2survive/AE_Get_Emojis"
EMOJIS_DIR = os.path.join(REPO_DIR, "emojis")
OUT_JSX = os.path.join(REPO_DIR, "AE_Get_Emojis.jsx")

# Core fallback subset of 28 emojis embedded directly inside AE_Get_Emojis.jsx
# so the script works 100% standalone even if emojis/*.json are not yet on disk.
FALLBACK_HEXCODES = [
    "1F642", "1F603", "1F606", "1F604", "1F601", "1F602", "1F923", "1F60A",
    "1F607", "1F608", "1F609", "1F60D", "1F60E", "1F60F", "1F610", "1F612",
    "1F615", "1F618", "1F61B", "1F61C", "1F620", "1F621", "1F622", "1F62D",
    "1F62E", "1F633", "1F634", "1F635", "1F641", "1F63A", "1F914", "1F929",
    "1F937", "1F64C", "1FAE1", "2764", "1F494", "1F44D", "1F44E", "1F525",
    "1F4AF", "1F4A9", "2728", "1F680", "1F480", "1F389", "2705", "26A0",
]


def main():
    with open(os.path.join(EMOJIS_DIR, "emoji_index.json"), "r", encoding="utf-8") as f:
        idx_data = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "wikipedia_emoticons.json"), "r", encoding="utf-8") as f:
        wiki_data = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "openmoji_color.json"), "r", encoding="utf-8") as f:
        om_color = json.load(f)

    fallback_emojis = []
    fallback_shapes = {}
    seen = set()
    for e in idx_data["emojis"]:
        hc = e["hexcode"]
        if hc in FALLBACK_HEXCODES and hc not in seen:
            seen.add(hc)
            rec = dict(e)
            rec["index"] = len(fallback_emojis) + 1
            fallback_emojis.append(rec)
            if hc in om_color:
                fallback_shapes[hc] = om_color[hc]

    fallback_index_json = json.dumps({"version": "1.0.0", "totalCount": len(fallback_emojis), "emojis": fallback_emojis}, ensure_ascii=False, separators=(",", ":"))
    fallback_wiki_json = json.dumps(wiki_data, ensure_ascii=False, separators=(",", ":"))
    fallback_shapes_json = json.dumps(fallback_shapes, ensure_ascii=False, separators=(",", ":"))

    jsx_code = r'''/**
 * ============================================================================
 * AE Get Emojis v1.0 — Full-Color Vector Emojis for Adobe After Effects
 * ============================================================================
 * Purpose:
 *   Quickly search, index, and add or replace full-color vector emojis as native
 *   After Effects Shape Layers (since After Effects does not natively render
 *   color emoji fonts like Apple Color Emoji / Noto Color Emoji / Segoe UI Emoji).
 *
 * Features:
 *   1. JSON Database in /emojis/ Subfolder:
 *      - emojis/emoji_index.json         (291 indexed emojis with metadata & tags)
 *      - emojis/wikipedia_emoticons.json (Wikipedia List of Emoticons mappings)
 *      - emojis/openmoji_color.json      (OpenMoji handcrafted color + outlines)
 *      - emojis/twemoji_color.json       (Twemoji flat full-color vector shapes)
 *      - emojis/openmoji_black.json      (OpenMoji black line-art vector shapes)
 *   2. Multi-Source Pulldown:
 *      - OpenMoji Color (https://github.com/hfg-gmuend/openmoji)
 *      - Twemoji Flat Color (https://github.com/jdecked/twemoji)
 *      - OpenMoji Flat Color (Color layer only, no black outlines)
 *      - OpenMoji Black Line Art (Wireframe / line art)
 *   3. Smart Search & Lookup:
 *      - Search by Emoji Name ("grinning", "heart", "fire", "rocket", "shrug")
 *      - Search by Unicode Hex ("1F603", "U+1F603", "0x1F603", "2764")
 *      - Search by Unicode Integer ("128515", "128578", "10084")
 *      - Search by Emoji Glyph ("😃", "❤️", "🔥", "🚀")
 *      - Search by Wikipedia Emoticon (":D", ":)", ";)", ":P", "<3", "</3",
 *        "XD", ":'(", ">:(", "D:", ":O", ":3", "B-)", "O:)", "¯\_(ツ)_/¯", etc.)
 *        sourced from https://en.wikipedia.org/wiki/List_of_emoticons
 *   4. Unicode <-> Integer Conversion & Slider Indexing:
 *      - Bidirectional conversion between Unicode Hex (e.g. U+1F603) and
 *        32-bit Integer (e.g. 128515 = parseInt("1F603", 16)).
 *      - Interactive Catalog Index Slider & Unicode Integer Slider in the UI,
 *        plus Effect Slider Controls ("Emoji Index", "Emoji Unicode Int",
 *        "Emoji Source", "Emoji Size (px)", "Outline Width %", "Show Outlines")
 *        on every generated After Effects Shape Layer.
 *   5. Smart "Add Emoji" / "Replace Emoji" Button:
 *      - Places the located emoji into a new native Shape Layer.
 *      - Automatically detects if an Emoji Shape Layer is selected in the active
 *        composition and switches the button label to "Replace Emoji" (or
 *        "Add / Replace Emoji" when selection detection is unavailable).
 *
 * Repository: https://github.com/work2survive/AE_Get_Emojis
 * Live Demo:  https://work2survive.github.io/AE_JS_builder/?jsx=AE_Get_Emojis.jsx&autobuild=true
 * ============================================================================
 */

(function (thisObj) {
    var SCRIPT_TITLE = "AE Get Emojis v1.0";

    // =========================================================================
    // 1. ES3 / EXTENDSCRIPT SAFE JSON POLYFILL & STRING UTILITIES
    // =========================================================================
    var JSONPolyfill = (typeof JSON !== "undefined" && JSON.parse && JSON.stringify) ? JSON : {
        parse: function (str) {
            return eval("(" + str + ")");
        },
        stringify: function (obj) {
            if (obj === null || typeof obj === "undefined") return "null";
            if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
            if (typeof obj === "string") {
                return '"' + obj.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n").replace(/\r/g, "\\r") + '"';
            }
            if (obj instanceof Array) {
                var arr = [];
                for (var i = 0; i < obj.length; i++) arr.push(JSONPolyfill.stringify(obj[i]));
                return "[" + arr.join(",") + "]";
            }
            if (typeof obj === "object") {
                var pairs = [];
                for (var k in obj) {
                    if (obj.hasOwnProperty(k)) {
                        pairs.push(JSONPolyfill.stringify(String(k)) + ":" + JSONPolyfill.stringify(obj[k]));
                    }
                }
                return "{" + pairs.join(",") + "}";
            }
            return "null";
        }
    };

    function trimStr(s) {
        if (s === null || typeof s === "undefined") return "";
        return String(s).replace(/^\s+|\s+$/g, "");
    }

    function padHex(hexStr, minLen) {
        var s = String(hexStr || "").toUpperCase();
        while (s.length < (minLen || 4)) s = "0" + s;
        return s;
    }

    function unicodeHexToInt(hexStr) {
        if (!hexStr) return 0;
        var clean = trimStr(hexStr).toUpperCase()
            .replace(/^U\+/i, "")
            .replace(/^0X/i, "")
            .split("-")[0];
        var val = parseInt(clean, 16);
        return isNaN(val) ? 0 : val;
    }

    function unicodeIntToHex(intVal) {
        var n = Math.max(0, Math.round(Number(intVal) || 0));
        return padHex(n.toString(16).toUpperCase(), 4);
    }

    function codePointToGlyph(codePoint) {
        var cp = Number(codePoint) || 0;
        if (cp <= 0) return "";
        try {
            if (typeof String.fromCodePoint === "function") {
                return String.fromCodePoint(cp);
            }
            if (cp <= 0xFFFF) {
                return String.fromCharCode(cp);
            }
            cp -= 0x10000;
            var high = 0xD800 + (cp >> 10);
            var low = 0xDC00 + (cp & 0x3FF);
            return String.fromCharCode(high, low);
        } catch (e) {
            return "";
        }
    }

    function glyphToCodePointInt(str) {
        var s = trimStr(str);
        if (!s) return 0;
        if (typeof s.codePointAt === "function") {
            return s.codePointAt(0) || 0;
        }
        var c0 = s.charCodeAt(0);
        if (c0 >= 0xD800 && c0 <= 0xDBFF && s.length > 1) {
            var c1 = s.charCodeAt(1);
            if (c1 >= 0xDC00 && c1 <= 0xDFFF) {
                return ((c0 - 0xD800) << 10) + (c1 - 0xDC00) + 0x10000;
            }
        }
        return c0;
    }

    function isBrowserSim() {
        return (typeof window !== "undefined" && typeof document !== "undefined");
    }

    // =========================================================================
    // 2. EMBEDDED FALLBACK DATABASE (Used if /emojis/*.json is offline/missing)
    // =========================================================================
    var FALLBACK_INDEX_DATA = __FALLBACK_INDEX_JSON__;
    var FALLBACK_WIKI_DATA = __FALLBACK_WIKI_JSON__;
    var FALLBACK_SHAPES_DATA = __FALLBACK_SHAPES_JSON__;

    // =========================================================================
    // 3. EMOJI SOURCES & SUBFOLDER (/emojis/*.json) LOADER
    // =========================================================================
    var EMOJI_SOURCES = [
        {
            id: "openmoji_color",
            index: 1,
            label: "OpenMoji Color (hfg-gmuend/openmoji)",
            shortName: "OpenMoji Color",
            file: "openmoji_color.json",
            repo: "https://github.com/hfg-gmuend/openmoji"
        },
        {
            id: "twemoji_color",
            index: 2,
            label: "Twemoji Flat Color (jdecked/twemoji)",
            shortName: "Twemoji Flat",
            file: "twemoji_color.json",
            repo: "https://github.com/jdecked/twemoji"
        },
        {
            id: "openmoji_flat",
            index: 3,
            label: "OpenMoji Flat (Color Only, No Outlines)",
            shortName: "OpenMoji Flat",
            file: "openmoji_color.json",
            repo: "https://github.com/hfg-gmuend/openmoji"
        },
        {
            id: "openmoji_black",
            index: 4,
            label: "OpenMoji Black (Line Art / Wireframe)",
            shortName: "OpenMoji Black",
            file: "openmoji_black.json",
            repo: "https://github.com/hfg-gmuend/openmoji"
        }
    ];

    var CATEGORY_FILTERS = [
        { id: "all", label: "All Categories" },
        { id: "emoticons", label: "Wikipedia Emoticons (:D, :), <3, XD...)" },
        { id: "smileys-emotion", label: "Smileys & Emotion" },
        { id: "people-body", label: "People & Gestures" },
        { id: "symbols", label: "Hearts & Symbols" },
        { id: "animals-nature", label: "Animals & Nature" },
        { id: "food-drink", label: "Food & Drink" },
        { id: "activities-objects", label: "Activities, Travel & Objects" }
    ];

    var customEmojisFolderPath = null;
    var emojiCatalog = [];
    var emojiByHex = {};
    var emojiByInt = {};
    var emojiByIndex = {};
    var wikiEmoticonMap = {};
    var wikiEntries = [];
    var shapeDatabases = {
        openmoji_color: {},
        twemoji_color: {},
        openmoji_black: {}
    };

    function getEmojisFolder() {
        if (typeof Folder === "undefined") return null;
        try {
            if (customEmojisFolderPath) {
                var customFolder = new Folder(customEmojisFolderPath);
                if (customFolder.exists) return customFolder;
            }
            if (typeof $ !== "undefined" && $.fileName) {
                var scriptFile = new File($.fileName);
                if (scriptFile && scriptFile.parent && scriptFile.parent.exists) {
                    var sub = new Folder(scriptFile.parent.fsName + "/emojis");
                    if (!sub.exists) {
                        try { sub.create(); } catch (eCreate) {}
                    }
                    return sub;
                }
            }
        } catch (e) {}
        return null;
    }

    function ensureDiskJSONFiles() {
        var folder = getEmojisFolder();
        if (!folder || typeof File === "undefined") return;
        try {
            var idxFile = new File(folder.fsName + "/emoji_index.json");
            if (!idxFile.exists) {
                idxFile.encoding = "UTF-8";
                if (idxFile.open("w")) {
                    idxFile.write(JSONPolyfill.stringify(FALLBACK_INDEX_DATA));
                    idxFile.close();
                }
            }
            var wikiFile = new File(folder.fsName + "/wikipedia_emoticons.json");
            if (!wikiFile.exists) {
                wikiFile.encoding = "UTF-8";
                if (wikiFile.open("w")) {
                    wikiFile.write(JSONPolyfill.stringify(FALLBACK_WIKI_DATA));
                    wikiFile.close();
                }
            }
            var omFile = new File(folder.fsName + "/openmoji_color.json");
            if (!omFile.exists) {
                omFile.encoding = "UTF-8";
                if (omFile.open("w")) {
                    omFile.write(JSONPolyfill.stringify(FALLBACK_SHAPES_DATA));
                    omFile.close();
                }
            }
        } catch (e) {}
    }

    function loadJSONFromEmojisSubfolder(filename) {
        // 1. Browser / AE_JS_builder environment: synchronous XHR from jsx/emojis/ or emojis/
        if (typeof XMLHttpRequest !== "undefined") {
            var candidateUrls = [
                "jsx/emojis/" + filename,
                "emojis/" + filename,
                "https://raw.githubusercontent.com/work2survive/AE_Get_Emojis/main/emojis/" + filename
            ];
            for (var u = 0; u < candidateUrls.length; u++) {
                try {
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", candidateUrls[u], false);
                    xhr.send(null);
                    if (xhr.status >= 200 && xhr.status < 300 && xhr.responseText) {
                        var txt = trimStr(xhr.responseText);
                        if (txt.charAt(0) === "{" || txt.charAt(0) === "[") {
                            return JSONPolyfill.parse(txt);
                        }
                    }
                } catch (eXhr) {}
            }
        }

        // 2. Desktop Adobe After Effects ExtendScript: read from /emojis/ subfolder
        if (typeof File !== "undefined") {
            try {
                ensureDiskJSONFiles();
                var folder = getEmojisFolder();
                if (folder && folder.exists) {
                    var f = new File(folder.fsName + "/" + filename);
                    if (f.exists) {
                        f.encoding = "UTF-8";
                        if (f.open("r")) {
                            var content = f.read();
                            f.close();
                            if (content && content.length > 2) {
                                return JSONPolyfill.parse(content);
                            }
                        }
                    }
                }
            } catch (eFile) {}
        }

        return null;
    }

    function rebuildLookupTables(idxData, wikiData) {
        emojiCatalog = (idxData && idxData.emojis && idxData.emojis.length) ? idxData.emojis : FALLBACK_INDEX_DATA.emojis;
        emojiByHex = {};
        emojiByInt = {};
        emojiByIndex = {};

        for (var i = 0; i < emojiCatalog.length; i++) {
            var item = emojiCatalog[i];
            item.index = i + 1;
            var hc = String(item.hexcode || "").toUpperCase();
            if (!item.unicodeInt) {
                item.unicodeInt = unicodeHexToInt(hc);
            }
            if (!item.unicode) {
                item.unicode = "U+" + hc;
            }
            if (!item.emoji) {
                item.emoji = codePointToGlyph(item.unicodeInt);
            }
            emojiByHex[hc] = item;
            emojiByInt[item.unicodeInt] = item;
            emojiByIndex[item.index] = item;
        }

        var wData = wikiData || FALLBACK_WIKI_DATA;
        wikiEmoticonMap = {};
        wikiEntries = (wData && wData.entries) ? wData.entries : [];

        if (wData && wData.lookup) {
            for (var k in wData.lookup) {
                if (wData.lookup.hasOwnProperty(k)) {
                    wikiEmoticonMap[k] = String(wData.lookup[k]).toUpperCase();
                    wikiEmoticonMap[k.toLowerCase()] = String(wData.lookup[k]).toUpperCase();
                }
            }
        }
        for (var w = 0; w < wikiEntries.length; w++) {
            var we = wikiEntries[w];
            var whc = String(we.hexcode || "").toUpperCase();
            var emos = we.emoticons || [];
            for (var ei = 0; ei < emos.length; ei++) {
                wikiEmoticonMap[emos[ei]] = whc;
                wikiEmoticonMap[emos[ei].toLowerCase()] = whc;
            }
        }
    }

    function loadAllEmojiDatabases() {
        var idxData = loadJSONFromEmojisSubfolder("emoji_index.json") || FALLBACK_INDEX_DATA;
        var wikiData = loadJSONFromEmojisSubfolder("wikipedia_emoticons.json") || FALLBACK_WIKI_DATA;
        rebuildLookupTables(idxData, wikiData);

        var omColor = loadJSONFromEmojisSubfolder("openmoji_color.json");
        shapeDatabases.openmoji_color = omColor || FALLBACK_SHAPES_DATA;

        var twColor = loadJSONFromEmojisSubfolder("twemoji_color.json");
        shapeDatabases.twemoji_color = twColor || shapeDatabases.openmoji_color;

        var omBlack = loadJSONFromEmojisSubfolder("openmoji_black.json");
        shapeDatabases.openmoji_black = omBlack || shapeDatabases.openmoji_color;
    }

    loadAllEmojiDatabases();

    // =========================================================================
    // 4. BUILT-IN LIVE SVG PARSER (For Custom Codepoints / On-the-Fly SVG Load)
    // =========================================================================
    var KAPPA = 0.55228474983;

    function parseSvgColor(val) {
        if (!val) return null;
        var v = trimStr(val).toLowerCase();
        if (v === "none" || v === "transparent") return null;
        if (v === "black") return [0, 0, 0];
        if (v === "white") return [1, 1, 1];
        if (v.charAt(0) === "#") {
            var h = v.substring(1);
            if (h.length === 3) {
                h = h.charAt(0) + h.charAt(0) + h.charAt(1) + h.charAt(1) + h.charAt(2) + h.charAt(2);
            }
            if (h.length >= 6) {
                return [
                    Math.round((parseInt(h.substring(0, 2), 16) / 255) * 1000) / 1000,
                    Math.round((parseInt(h.substring(2, 4), 16) / 255) * 1000) / 1000,
                    Math.round((parseInt(h.substring(4, 6), 16) / 255) * 1000) / 1000
                ];
            }
        }
        return null;
    }

    function getShapesForEmoji(hexcode, sourceId) {
        var hc = String(hexcode || "1F603").toUpperCase();
        var src = sourceId || "openmoji_color";

        if (src === "twemoji_color") {
            if (shapeDatabases.twemoji_color && shapeDatabases.twemoji_color[hc]) {
                return shapeDatabases.twemoji_color[hc];
            }
        } else if (src === "openmoji_black") {
            if (shapeDatabases.openmoji_black && shapeDatabases.openmoji_black[hc]) {
                return shapeDatabases.openmoji_black[hc];
            }
        } else if (src === "openmoji_flat") {
            var baseShapes = (shapeDatabases.openmoji_color && shapeDatabases.openmoji_color[hc]) || FALLBACK_SHAPES_DATA[hc];
            if (baseShapes && baseShapes.length) {
                var flatFiltered = [];
                for (var i = 0; i < baseShapes.length; i++) {
                    if (!baseShapes[i].l) {
                        flatFiltered.push(baseShapes[i]);
                    }
                }
                return flatFiltered.length > 0 ? flatFiltered : baseShapes;
            }
        }

        if (shapeDatabases.openmoji_color && shapeDatabases.openmoji_color[hc]) {
            return shapeDatabases.openmoji_color[hc];
        }
        if (FALLBACK_SHAPES_DATA[hc]) {
            return FALLBACK_SHAPES_DATA[hc];
        }
        return FALLBACK_SHAPES_DATA["1F603"];
    }

    // =========================================================================
    // 5. SEARCH & RESOLUTION ENGINE (Name, Unicode, Integer, Glyph, Emoticon)
    // =========================================================================
    function matchesCategoryFilter(entry, categoryId) {
        if (!categoryId || categoryId === "all") return true;
        if (categoryId === "emoticons") {
            return (entry.emoticons && entry.emoticons.length > 0);
        }
        var grp = String(entry.group || "").toLowerCase();
        if (categoryId === "smileys-emotion") {
            return grp.indexOf("smiley") >= 0 || grp.indexOf("emotion") >= 0;
        }
        if (categoryId === "people-body") {
            return grp.indexOf("people") >= 0 || grp.indexOf("body") >= 0;
        }
        if (categoryId === "symbols") {
            return grp.indexOf("symbol") >= 0 || (entry.name && entry.name.toLowerCase().indexOf("heart") >= 0);
        }
        if (categoryId === "animals-nature") {
            return grp.indexOf("animal") >= 0 || grp.indexOf("nature") >= 0;
        }
        if (categoryId === "food-drink") {
            return grp.indexOf("food") >= 0 || grp.indexOf("drink") >= 0;
        }
        if (categoryId === "activities-objects") {
            return grp.indexOf("activit") >= 0 || grp.indexOf("object") >= 0 || grp.indexOf("travel") >= 0;
        }
        return true;
    }

    function searchEmojis(rawQuery, categoryId) {
        var q = trimStr(rawQuery);
        var qLower = q.toLowerCase();
        var results = [];
        var exactMatches = [];

        // 1. Check exact Wikipedia Emoticon match first (e.g. ":D", ":)", "<3", "XD", "¯\_(ツ)_/¯")
        if (q && wikiEmoticonMap.hasOwnProperty(q)) {
            var emoHex = wikiEmoticonMap[q];
            if (emojiByHex[emoHex]) {
                exactMatches.push(emojiByHex[emoHex]);
            }
        } else if (q && wikiEmoticonMap.hasOwnProperty(qLower)) {
            var emoHexLower = wikiEmoticonMap[qLower];
            if (emojiByHex[emoHexLower]) {
                exactMatches.push(emojiByHex[emoHexLower]);
            }
        }

        // 2. Check direct Emoji Glyph character input (e.g. "😃", "🔥", "❤️")
        if (q && q.length <= 4) {
            var cpInt = glyphToCodePointInt(q);
            if (cpInt > 127 && emojiByInt[cpInt]) {
                var glyphEntry = emojiByInt[cpInt];
                if (exactMatches.indexOf(glyphEntry) < 0) {
                    exactMatches.push(glyphEntry);
                }
            }
        }

        // 3. Check Unicode Hex ("U+1F603", "0x1F603", "1F603") or Integer ("128515")
        if (q) {
            if (/^(U\+|0X)[0-9A-F\-]+$/i.test(q)) {
                var cleanHex = q.replace(/^(U\+|0X)/i, "").toUpperCase();
                if (emojiByHex[cleanHex] && exactMatches.indexOf(emojiByHex[cleanHex]) < 0) {
                    exactMatches.push(emojiByHex[cleanHex]);
                }
            } else if (/^\d{4,6}$/.test(q)) {
                var asDecInt = parseInt(q, 10);
                if (emojiByInt[asDecInt] && exactMatches.indexOf(emojiByInt[asDecInt]) < 0) {
                    exactMatches.push(emojiByInt[asDecInt]);
                }
                var asHexUpper = q.toUpperCase();
                if (emojiByHex[asHexUpper] && exactMatches.indexOf(emojiByHex[asHexUpper]) < 0) {
                    exactMatches.push(emojiByHex[asHexUpper]);
                }
            } else if (/^[0-9A-F]{4,5}$/i.test(q)) {
                var hexCandidate = q.toUpperCase();
                if (emojiByHex[hexCandidate] && exactMatches.indexOf(emojiByHex[hexCandidate]) < 0) {
                    exactMatches.push(emojiByHex[hexCandidate]);
                }
            }
        }

        // 4. Filter catalog by query & category
        for (var i = 0; i < emojiCatalog.length; i++) {
            var entry = emojiCatalog[i];
            if (!matchesCategoryFilter(entry, categoryId)) continue;

            if (!q) {
                results.push(entry);
                continue;
            }

            if (exactMatches.indexOf(entry) >= 0) continue;

            var matched = false;
            var nameLower = String(entry.name || "").toLowerCase();
            var hexLower = String(entry.hexcode || "").toLowerCase();
            var intStr = String(entry.unicodeInt || "");

            if (nameLower.indexOf(qLower) >= 0 || hexLower.indexOf(qLower.replace(/^u\+/i, "")) >= 0 || intStr.indexOf(q) >= 0) {
                matched = true;
            }
            if (!matched && entry.emoji === q) {
                matched = true;
            }
            if (!matched && entry.emoticons) {
                for (var em = 0; em < entry.emoticons.length; em++) {
                    var emoToken = String(entry.emoticons[em]);
                    if (emoToken === q || emoToken.toLowerCase().indexOf(qLower) >= 0) {
                        matched = true;
                        break;
                    }
                }
            }
            if (!matched && entry.tags) {
                for (var tg = 0; tg < entry.tags.length; tg++) {
                    if (String(entry.tags[tg]).toLowerCase().indexOf(qLower) >= 0) {
                        matched = true;
                        break;
                    }
                }
            }

            if (matched) {
                results.push(entry);
            }
        }

        return exactMatches.concat(results);
    }

    function findNearestEmojiByUnicodeInt(targetInt) {
        var n = Math.round(Number(targetInt) || 128515);
        if (emojiByInt[n]) return emojiByInt[n];
        var best = emojiCatalog[0];
        var bestDist = Math.abs((best ? best.unicodeInt : 128515) - n);
        for (var i = 1; i < emojiCatalog.length; i++) {
            var d = Math.abs(emojiCatalog[i].unicodeInt - n);
            if (d < bestDist) {
                bestDist = d;
                best = emojiCatalog[i];
            }
        }
        return best;
    }

    // =========================================================================
    // 6. AFTER EFFECTS SHAPE LAYER BUILDER & REPLACER
    // =========================================================================
    function isEmojiLayer(layer) {
        if (!layer) return false;
        try {
            var nm = String(layer.name || "");
            if (nm.indexOf("Emoji ") === 0 || nm.indexOf("Emoji_") === 0) return true;
            var fx = layer.property("ADBE Effect Parade") || layer.effects;
            if (fx && fx.property("Emoji Unicode Int")) return true;
        } catch (e) {}
        return false;
    }

    function getSelectedEmojiLayer(comp) {
        if (!comp) return null;
        try {
            var sel = comp.selectedLayers;
            if (sel && sel.length > 0) {
                for (var i = 0; i < sel.length; i++) {
                    if (isEmojiLayer(sel[i])) return sel[i];
                }
                // Also allow replacing if any ShapeLayer is explicitly selected
                if (sel[0] && sel[0].property && sel[0].property("ADBE Root Vectors Group")) {
                    if (isEmojiLayer(sel[0])) return sel[0];
                }
            }
        } catch (e) {}
        return null;
    }

    function getAnyExistingEmojiLayer(comp) {
        var sel = getSelectedEmojiLayer(comp);
        if (sel) return sel;
        if (!comp) return null;
        try {
            var count = (typeof comp.numLayers === "number") ? comp.numLayers : (comp.layers ? comp.layers.length : 0);
            for (var i = 1; i <= count; i++) {
                var lyr = comp.layer ? comp.layer(i) : comp.layers[i - 1];
                if (isEmojiLayer(lyr)) return lyr;
            }
        } catch (e) {}
        return null;
    }

    function countEmojiLayersInComp(comp) {
        if (!comp) return 0;
        var total = 0;
        try {
            var count = (typeof comp.numLayers === "number") ? comp.numLayers : (comp.layers ? comp.layers.length : 0);
            for (var i = 1; i <= count; i++) {
                var lyr = comp.layer ? comp.layer(i) : comp.layers[i - 1];
                if (isEmojiLayer(lyr)) total++;
            }
        } catch (e) {}
        return total;
    }

    function ensureEffectSlider(fxGroup, name, defaultVal) {
        var eff = fxGroup.property(name);
        if (!eff) {
            eff = fxGroup.addProperty("ADBE Slider Control");
            eff.name = name;
        }
        try {
            eff.property("ADBE Slider Control-0001").setValue(defaultVal);
        } catch (e) {
            try { eff.property("Slider").setValue(defaultVal); } catch (e2) {}
        }
        return eff;
    }

    function ensureEffectCheckbox(fxGroup, name, defaultVal) {
        var eff = fxGroup.property(name);
        if (!eff) {
            eff = fxGroup.addProperty("ADBE Checkbox Control");
            eff.name = name;
        }
        try {
            eff.property("ADBE Checkbox Control-0001").setValue(defaultVal ? 1 : 0);
        } catch (e) {
            try { eff.property("Checkbox").setValue(defaultVal ? 1 : 0); } catch (e2) {}
        }
        return eff;
    }

    function clearRootVectorContents(rootVectors) {
        if (!rootVectors) return;
        try {
            if (typeof rootVectors.numProperties === "number") {
                for (var i = rootVectors.numProperties; i >= 1; i--) {
                    try { rootVectors.property(i).remove(); } catch (eRem) {}
                }
            }
            if (rootVectors.properties && rootVectors.properties.length > 0) {
                rootVectors.properties.length = 0;
            }
        } catch (e) {}
    }

    function populateEmojiVectorShapes(shapeLayer, entry, sourceId, sizePx, outlinePct, showOutlines) {
        var rootVectors = shapeLayer.property("ADBE Root Vectors Group");
        if (!rootVectors) return;

        clearRootVectorContents(rootVectors);

        var masterGrp = rootVectors.addProperty("ADBE Vector Group");
        masterGrp.name = "Emoji_Master (" + entry.unicode + " = " + entry.unicodeInt + ")";
        var masterContents = masterGrp.property("ADBE Vectors Group");

        var shapes = getShapesForEmoji(entry.hexcode, sourceId);
        var inBrowser = isBrowserSim();

        // In browser SVG renderer, index 0 is rendered first (back-to-front).
        // In desktop After Effects Shape Layer stack, index 1 is rendered on top (front-to-back).
        var startIdx = inBrowser ? 0 : (shapes.length - 1);
        var endIdx = inBrowser ? shapes.length : -1;
        var step = inBrowser ? 1 : -1;

        for (var idx = startIdx; idx !== endIdx; idx += step) {
            var item = shapes[idx];
            var isLine = Boolean(item.l) && (sourceId !== "openmoji_black");
            if (isLine && !showOutlines && inBrowser) {
                // Still create the group so toggling Show Outlines works dynamically
            }

            var partGrp = masterContents.addProperty("ADBE Vector Group");
            partGrp.name = (item.l ? "Outline_" : "Color_") + (idx + 1);
            var partVecs = partGrp.property("ADBE Vectors Group");

            var subpaths = item.p ? item.p : [item];
            for (var spIdx = 0; spIdx < subpaths.length; spIdx++) {
                var sp = subpaths[spIdx];
                if (!sp.v || sp.v.length < 2) continue;
                var pathGrp = partVecs.addProperty("ADBE Vector Shape - Group");
                pathGrp.name = "Path_" + (spIdx + 1);
                var myShape = new Shape();
                myShape.vertices = sp.v;
                myShape.inTangents = sp.i || [];
                myShape.outTangents = sp.o || [];
                myShape.closed = Boolean(sp.c);
                pathGrp.property("ADBE Vector Shape").setValue(myShape);
            }

            if (item.f) {
                var fillProp = partVecs.addProperty("ADBE Vector Graphic - Fill");
                fillProp.name = "Fill";
                fillProp.property("ADBE Vector Fill Color").setValue(item.f);
                var fOp = (typeof item.fo === "number") ? item.fo : 100;
                fillProp.property("ADBE Vector Fill Opacity").setValue(fOp);
            }

            if (item.s && item.sw > 0) {
                var strokeProp = partVecs.addProperty("ADBE Vector Graphic - Stroke");
                strokeProp.name = "Stroke";
                strokeProp.property("ADBE Vector Stroke Color").setValue(item.s);
                var baseSw = item.sw;
                var effectiveSw = isLine ? (baseSw * (outlinePct / 100.0)) : baseSw;
                strokeProp.property("ADBE Vector Stroke Width").setValue(effectiveSw);
                var sOp = (typeof item.so === "number") ? item.so : 100;
                strokeProp.property("ADBE Vector Stroke Opacity").setValue(sOp);
                if (item.lc) {
                    try { strokeProp.property("ADBE Vector Stroke Line Cap").setValue(item.lc); } catch (eLc) {}
                }
                if (item.lj) {
                    try { strokeProp.property("ADBE Vector Stroke Line Join").setValue(item.lj); } catch (eLj) {}
                }
                if (isLine) {
                    try {
                        strokeProp.property("ADBE Vector Stroke Width").expression =
                            "try { value * (effect('Outline Width %')('Slider') / 100); } catch(e) { value; }";
                    } catch (eSwExpr) {}
                }
            }

            if (isLine) {
                var partTr = partGrp.property("ADBE Vector Transform Group");
                if (partTr && partTr.property("ADBE Vector Opacity")) {
                    partTr.property("ADBE Vector Opacity").setValue(showOutlines ? 100 : 0);
                    try {
                        partTr.property("ADBE Vector Opacity").expression =
                            "try { (effect('Show Outlines')('Checkbox') > 0) ? 100 : 0; } catch(e) { value; }";
                    } catch (eOpExpr) {}
                }
            }
        }

        // Rig Master Vector Group Scale to "Emoji Size (px)" (base coordinate space is 72x72)
        var masterTr = masterGrp.property("ADBE Vector Transform Group");
        if (masterTr) {
            masterTr.property("ADBE Vector Anchor").setValue([0, 0]);
            masterTr.property("ADBE Vector Position").setValue([0, 0]);
            var scalePct = Math.round((sizePx / 72.0) * 10000) / 100;
            masterTr.property("ADBE Vector Scale").setValue([scalePct, scalePct]);
            try {
                masterTr.property("ADBE Vector Scale").expression = [
                    "try {",
                    "  var sz = effect('Emoji Size (px)')('Slider');",
                    "  var s = (sz / 72.0) * 100.0;",
                    "  [s, s];",
                    "} catch(e) { value; }"
                ].join("\n");
            } catch (eScExpr) {}
        }
    }

    function applyEmojiToLayer(comp, targetLayer, entry, sourceObj, sizePx, outlinePct, showOutlines, isReplacing) {
        var shapeLayer = targetLayer;
        var existingCount = countEmojiLayersInComp(comp);

        if (!shapeLayer) {
            shapeLayer = comp.layers.addShape();
            var tr = shapeLayer.property("ADBE Transform Group");
            if (tr) {
                tr.property("ADBE Anchor Point").setValue([0, 0, 0]);
                // Place first emoji at comp center; offset subsequent added emojis neatly in a grid
                var cx = comp.width / 2;
                var cy = comp.height / 2;
                if (existingCount > 0) {
                    var col = existingCount % 5;
                    var row = Math.floor(existingCount / 5);
                    cx = (comp.width * 0.2) + col * (comp.width * 0.15);
                    cy = (comp.height * 0.3) + (row % 3) * (comp.height * 0.2);
                }
                tr.property("ADBE Position").setValue([Math.round(cx), Math.round(cy), 0]);
            }
        }

        var emoLabel = (entry.emoticons && entry.emoticons.length > 0) ? (" " + entry.emoticons[0]) : "";
        shapeLayer.name = "Emoji " + entry.emoji + " " + entry.name + " [" + entry.unicode + " | " + entry.unicodeInt + "]" + emoLabel;
        shapeLayer.label = 9;

        // Add/Update Effect Slider Controls on the layer
        var fxGroup = shapeLayer.property("ADBE Effect Parade") || shapeLayer.effects;
        if (fxGroup) {
            ensureEffectSlider(fxGroup, "Emoji Index", entry.index);
            ensureEffectSlider(fxGroup, "Emoji Unicode Int", entry.unicodeInt);
            ensureEffectSlider(fxGroup, "Emoji Source (1=OM,2=TW,3=Flat,4=Blk)", sourceObj.index);
            ensureEffectSlider(fxGroup, "Emoji Size (px)", sizePx);
            ensureEffectSlider(fxGroup, "Outline Width %", outlinePct);
            ensureEffectCheckbox(fxGroup, "Show Outlines", showOutlines);
        }

        populateEmojiVectorShapes(shapeLayer, entry, sourceObj.id, sizePx, outlinePct, showOutlines);

        // Select the created/updated layer so "Replace Emoji" is immediately active
        try {
            if (comp.layers && comp.layers._layers) {
                for (var li = 0; li < comp.layers._layers.length; li++) {
                    comp.layers._layers[li].selected = (comp.layers._layers[li] === shapeLayer);
                }
            }
            shapeLayer.selected = true;
        } catch (eSel) {}

        if (comp._onChanged) {
            try { comp._onChanged(); } catch (eChg) {}
        }

        return shapeLayer;
    }

    // Expose live-sync hook for AE_JS_builder timeline scrubbing
    if (typeof window !== "undefined") {
        window.__syncEmojiLayerFromEffect = function (layer, effectName) {
            if (!layer || !isEmojiLayer(layer)) return;
            try {
                var fx = layer.property("ADBE Effect Parade") || layer.effects;
                if (!fx) return;
                var idxVal = Math.round(fx.property("Emoji Index").property("Slider").value || 1);
                var intVal = Math.round(fx.property("Emoji Unicode Int").property("Slider").value || 128515);
                var srcIdx = Math.max(1, Math.min(4, Math.round(fx.property("Emoji Source (1=OM,2=TW,3=Flat,4=Blk)").property("Slider").value || 1)));
                var szVal = Math.max(16, fx.property("Emoji Size (px)").property("Slider").value || 280);
                var outPct = Math.max(0, fx.property("Outline Width %").property("Slider").value || 100);
                var showOut = Boolean(fx.property("Show Outlines").property("Checkbox").value);

                var srcObj = EMOJI_SOURCES[srcIdx - 1] || EMOJI_SOURCES[0];
                var targetEntry = null;

                if (effectName === "Emoji Index") {
                    idxVal = Math.max(1, Math.min(emojiCatalog.length, idxVal));
                    targetEntry = emojiByIndex[idxVal] || emojiCatalog[0];
                    fx.property("Emoji Unicode Int").property("Slider").setValue(targetEntry.unicodeInt);
                } else if (effectName === "Emoji Unicode Int") {
                    targetEntry = findNearestEmojiByUnicodeInt(intVal);
                    fx.property("Emoji Index").property("Slider").setValue(targetEntry.index);
                } else {
                    targetEntry = emojiByIndex[idxVal] || findNearestEmojiByUnicodeInt(intVal) || emojiCatalog[0];
                }

                if (targetEntry) {
                    var emoLabel = (targetEntry.emoticons && targetEntry.emoticons.length > 0) ? (" " + targetEntry.emoticons[0]) : "";
                    layer.name = "Emoji " + targetEntry.emoji + " " + targetEntry.name + " [" + targetEntry.unicode + " | " + targetEntry.unicodeInt + "]" + emoLabel;
                    populateEmojiVectorShapes(layer, targetEntry, srcObj.id, szVal, outPct, showOut);
                }
            } catch (eSync) {}
        };
    }

    // =========================================================================
    // 7. SCRIPTUI INTERFACE CONSTRUCTION
    // =========================================================================
    function buildUI(thisObj) {
        var win = (thisObj instanceof Panel)
            ? thisObj
            : new Window("palette", SCRIPT_TITLE, undefined, { resizeable: true });

        win.orientation = "column";
        win.alignChildren = ["fill", "top"];
        win.spacing = 6;
        win.margins = 10;

        var currentMatches = emojiCatalog.slice();
        // Default initial selection: 😃 U+1F603 (:D)
        var currentEntry = emojiByHex["1F603"] || emojiCatalog[0];
        var currentSourceObj = EMOJI_SOURCES[0];
        var isSyncingUI = false;

        // ---------------------------------------------------------------------
        // PANEL 1: SOURCE (.JSON IN /emojis/) & CATEGORY FILTER
        // ---------------------------------------------------------------------
        var pnlSource = win.add("panel", undefined, "1. Emoji Vector Source & Category (/emojis/*.json)");
        pnlSource.orientation = "column";
        pnlSource.alignChildren = ["fill", "top"];
        pnlSource.spacing = 5;
        pnlSource.margins = [10, 14, 10, 8];

        var grpSrcRow = pnlSource.add("group");
        grpSrcRow.orientation = "row";
        grpSrcRow.alignChildren = ["left", "center"];
        grpSrcRow.spacing = 6;

        var lblSrc = grpSrcRow.add("statictext", undefined, "Source:");
        lblSrc.preferredSize.width = 58;

        var srcNames = [];
        for (var si = 0; si < EMOJI_SOURCES.length; si++) {
            srcNames.push(EMOJI_SOURCES[si].label);
        }
        var ddSource = grpSrcRow.add("dropdownlist", undefined, srcNames);
        ddSource.selection = 0;
        ddSource.alignment = ["fill", "center"];
        ddSource.helpTip = "Choose the vector emoji style from the /emojis/ JSON database.";

        var btnReloadJSON = grpSrcRow.add("button", undefined, "↻");
        btnReloadJSON.preferredSize = [28, 24];
        btnReloadJSON.helpTip = "Reload .JSON emoji files from the /emojis/ subfolder.";

        var btnChooseFolder = grpSrcRow.add("button", undefined, "📂");
        btnChooseFolder.preferredSize = [28, 24];
        btnChooseFolder.helpTip = "Select a custom /emojis/ JSON folder on disk.";

        var grpCatRow = pnlSource.add("group");
        grpCatRow.orientation = "row";
        grpCatRow.alignChildren = ["left", "center"];
        grpCatRow.spacing = 6;

        var lblCat = grpCatRow.add("statictext", undefined, "Category:");
        lblCat.preferredSize.width = 58;

        var catNames = [];
        for (var ci = 0; ci < CATEGORY_FILTERS.length; ci++) {
            catNames.push(CATEGORY_FILTERS[ci].label);
        }
        var ddCategory = grpCatRow.add("dropdownlist", undefined, catNames);
        ddCategory.selection = 0;
        ddCategory.alignment = ["fill", "center"];

        // ---------------------------------------------------------------------
        // PANEL 2: SEARCH BY NAME, UNICODE, INTEGER, EMOJI OR WIKIPEDIA EMOTICON
        // ---------------------------------------------------------------------
        var pnlSearch = win.add("panel", undefined, "2. Find Emoji (Name, Unicode, Integer, Glyph, or Emoticon)");
        pnlSearch.orientation = "column";
        pnlSearch.alignChildren = ["fill", "top"];
        pnlSearch.spacing = 5;
        pnlSearch.margins = [10, 14, 10, 8];

        var grpQueryRow = pnlSearch.add("group");
        grpQueryRow.orientation = "row";
        grpQueryRow.alignChildren = ["left", "center"];
        grpQueryRow.spacing = 6;

        var lblQuery = grpQueryRow.add("statictext", undefined, "Search:");
        lblQuery.preferredSize.width = 58;

        var etSearch = grpQueryRow.add("edittext", undefined, ":D");
        etSearch.alignment = ["fill", "center"];
        etSearch.preferredSize.width = 150;
        etSearch.helpTip = "Type emoji name ('grinning', 'fire'), Unicode ('1F603', 'U+1F603'), integer ('128515'), glyph ('😃'), or Wikipedia emoticon (':D', ':)', '<3', 'XD', '¯\\_(ツ)_/¯').";

        var btnFind = grpQueryRow.add("button", undefined, "Find");
        btnFind.preferredSize = [48, 24];

        var btnClearSearch = grpQueryRow.add("button", undefined, "All");
        btnClearSearch.preferredSize = [38, 24];
        btnClearSearch.helpTip = "Clear search box and list all emojis in the current category.";

        // Wikipedia Emoticon Quick-Pick Pulldown (from https://en.wikipedia.org/wiki/List_of_emoticons)
        var grpWikiRow = pnlSearch.add("group");
        grpWikiRow.orientation = "row";
        grpWikiRow.alignChildren = ["left", "center"];
        grpWikiRow.spacing = 6;

        var lblWiki = grpWikiRow.add("statictext", undefined, "Emoticon:");
        lblWiki.preferredSize.width = 58;

        var wikiItems = ["-- Wikipedia Emoticon Shortcuts (e.g. :D, :), <3) --"];
        for (var wi = 0; wi < wikiEntries.length; wi++) {
            var weItem = wikiEntries[wi];
            var sampleEmos = (weItem.emoticons || []).slice(0, 4).join("  ");
            wikiItems.push(sampleEmos + "   \u2192   " + weItem.emoji + "  " + weItem.meaning + " (" + weItem.unicode + " = " + weItem.unicodeInt + ")");
        }
        var ddWikiEmoticon = grpWikiRow.add("dropdownlist", undefined, wikiItems);
        ddWikiEmoticon.selection = 0;
        ddWikiEmoticon.alignment = ["fill", "center"];
        ddWikiEmoticon.helpTip = "Select a Western or Eastern text emoticon from Wikipedia's List of Emoticons.";

        // Matching Emoji Results Pulldown
        var grpResRow = pnlSearch.add("group");
        grpResRow.orientation = "row";
        grpResRow.alignChildren = ["left", "center"];
        grpResRow.spacing = 6;

        var lblRes = grpResRow.add("statictext", undefined, "Located:");
        lblRes.preferredSize.width = 58;

        var ddResults = grpResRow.add("dropdownlist", undefined, []);
        ddResults.alignment = ["fill", "center"];
        ddResults.helpTip = "Matching emojis from /emojis/emoji_index.json.";

        // ---------------------------------------------------------------------
        // PANEL 3: SLIDER INDEXING & UNICODE <-> INTEGER CONVERSION
        // ---------------------------------------------------------------------
        var pnlConv = win.add("panel", undefined, "3. Slider Index & Unicode \u2194 Integer Conversion");
        pnlConv.orientation = "column";
        pnlConv.alignChildren = ["fill", "top"];
        pnlConv.spacing = 5;
        pnlConv.margins = [10, 14, 10, 8];

        // Big Preview + Conversion Banner
        var stBanner = pnlConv.add("statictext", undefined, "😃  grinning face with big eyes   |   U+1F603  \u21C4  128515");
        try {
            stBanner.graphics.font = ScriptUI.newFont("Arial", "BOLD", 12);
        } catch (eFont) {}

        var stEmoticonsLine = pnlConv.add("statictext", undefined, "Wikipedia Emoticons: :-D, :D, 8-D, 8D, =D, =3, B^D, c:, C:");

        // Catalog Index Slider (1 .. N)
        var grpIdxSlider = pnlConv.add("group");
        grpIdxSlider.orientation = "row";
        grpIdxSlider.alignChildren = ["left", "center"];
        grpIdxSlider.spacing = 6;

        var lblIdxSlider = grpIdxSlider.add("statictext", undefined, "Emoji Index:");
        lblIdxSlider.preferredSize.width = 82;

        var slIndex = grpIdxSlider.add("slider", undefined, currentEntry.index, 1, Math.max(2, emojiCatalog.length));
        slIndex.alignment = ["fill", "center"];
        slIndex.preferredSize.width = 140;
        slIndex.helpTip = "Scrub through all indexed emojis in /emojis/emoji_index.json.";

        var etIndex = grpIdxSlider.add("edittext", undefined, String(currentEntry.index));
        etIndex.preferredSize.width = 48;

        // Unicode Integer Slider (converts integer <-> Unicode hex live)
        var grpIntSlider = pnlConv.add("group");
        grpIntSlider.orientation = "row";
        grpIntSlider.alignChildren = ["left", "center"];
        grpIntSlider.spacing = 6;

        var lblIntSlider = grpIntSlider.add("statictext", undefined, "Unicode Int:");
        lblIntSlider.preferredSize.width = 82;

        var slUnicodeInt = grpIntSlider.add("slider", undefined, currentEntry.unicodeInt, 9728, 129782);
        slUnicodeInt.alignment = ["fill", "center"];
        slUnicodeInt.preferredSize.width = 140;
        slUnicodeInt.helpTip = "Reference emojis by their converted 32-bit Unicode integer codepoint.";

        var etUnicodeInt = grpIntSlider.add("edittext", undefined, String(currentEntry.unicodeInt));
        etUnicodeInt.preferredSize.width = 62;
        etUnicodeInt.helpTip = "Decimal Integer conversion of Unicode Hex (parseInt(hex, 16)). Edit to convert Integer -> Unicode.";

        // Explicit Hex <-> Integer Conversion Row
        var grpHexConv = pnlConv.add("group");
        grpHexConv.orientation = "row";
        grpHexConv.alignChildren = ["left", "center"];
        grpHexConv.spacing = 6;

        var lblHex = grpHexConv.add("statictext", undefined, "Unicode Hex:");
        lblHex.preferredSize.width = 82;

        var etUnicodeHex = grpHexConv.add("edittext", undefined, currentEntry.unicode);
        etUnicodeHex.preferredSize.width = 82;
        etUnicodeHex.helpTip = "Unicode Hexadecimal codepoint (e.g. U+1F603). Edit to convert Unicode -> Integer.";

        var stArrow = grpHexConv.add("statictext", undefined, "\u21C4  Int =");

        var stFormula = grpHexConv.add("statictext", undefined, "128515  (0x1F603)");
        stFormula.alignment = ["fill", "center"];

        // ---------------------------------------------------------------------
        // PANEL 4: LAYER SIZE, OUTLINES & LIVE RIG CONTROLS
        // ---------------------------------------------------------------------
        var pnlStyle = win.add("panel", undefined, "4. Shape Layer Size & Outline Controls");
        pnlStyle.orientation = "column";
        pnlStyle.alignChildren = ["fill", "top"];
        pnlStyle.spacing = 5;
        pnlStyle.margins = [10, 14, 10, 8];

        var grpSize = pnlStyle.add("group");
        grpSize.orientation = "row";
        grpSize.alignChildren = ["left", "center"];
        grpSize.spacing = 6;

        var lblSize = grpSize.add("statictext", undefined, "Emoji Size:");
        lblSize.preferredSize.width = 82;

        var slSize = grpSize.add("slider", undefined, 280, 32, 800);
        slSize.alignment = ["fill", "center"];
        slSize.preferredSize.width = 140;

        var etSize = grpSize.add("edittext", undefined, "280");
        etSize.preferredSize.width = 48;

        var grpOutline = pnlStyle.add("group");
        grpOutline.orientation = "row";
        grpOutline.alignChildren = ["left", "center"];
        grpOutline.spacing = 6;

        var lblOutline = grpOutline.add("statictext", undefined, "Outline %:");
        lblOutline.preferredSize.width = 82;

        var slOutline = grpOutline.add("slider", undefined, 100, 0, 300);
        slOutline.alignment = ["fill", "center"];
        slOutline.preferredSize.width = 140;

        var etOutline = grpOutline.add("edittext", undefined, "100");
        etOutline.preferredSize.width = 48;

        var grpChecks = pnlStyle.add("group");
        grpChecks.orientation = "row";
        grpChecks.alignChildren = ["left", "center"];
        grpChecks.spacing = 12;

        var chkOutlines = grpChecks.add("checkbox", undefined, "Show Outlines");
        chkOutlines.value = true;

        var chkLiveScrub = grpChecks.add("checkbox", undefined, "Live-Update Active Emoji on Slider Scrub");
        chkLiveScrub.value = true;

        // ---------------------------------------------------------------------
        // ACTION BUTTONS: SMART "ADD EMOJI" / "REPLACE EMOJI"
        // ---------------------------------------------------------------------
        var pnlActions = win.add("panel", undefined, "5. Place in Composition");
        pnlActions.orientation = "column";
        pnlActions.alignChildren = ["fill", "top"];
        pnlActions.spacing = 5;
        pnlActions.margins = [10, 12, 10, 8];

        var grpSelToggle = pnlActions.add("group");
        grpSelToggle.orientation = "row";
        grpSelToggle.alignChildren = ["left", "center"];
        grpSelToggle.spacing = 8;

        var chkSelectEmojiLayer = grpSelToggle.add("checkbox", undefined, "Emoji Layer Selected (Replace Mode)");
        chkSelectEmojiLayer.value = false;
        chkSelectEmojiLayer.helpTip = "Automatically turns ON when an Emoji layer is selected in the timeline. Uncheck to place in a new layer.";

        var stLayerTarget = pnlActions.add("statictext", undefined, "Target: New Shape Layer (Click 'Add Emoji' below)");

        var grpSubBtns = pnlActions.add("group");
        grpSubBtns.orientation = "row";
        grpSubBtns.alignChildren = ["fill", "center"];
        grpSubBtns.spacing = 6;

        var btnForceAddNew = grpSubBtns.add("button", undefined, "\u2795 Add New Layer");
        btnForceAddNew.helpTip = "Always create a new Emoji Shape Layer in the composition.";

        var btnForceReplace = grpSubBtns.add("button", undefined, "\uD83D\uDD04 Replace Active");
        btnForceReplace.helpTip = "Replace the selected (or most recent) Emoji Shape Layer in the composition.";

        var grpMainBtns = pnlActions.add("group");
        grpMainBtns.orientation = "row";
        grpMainBtns.alignChildren = ["fill", "center"];
        grpMainBtns.spacing = 6;

        var btnAddOrReplace = grpMainBtns.add("button", undefined, "\u2795 Add Emoji");
        btnAddOrReplace.preferredSize.height = 34;
        btnAddOrReplace.helpTip = "Places the located emoji in a new Shape Layer, or replaces the emoji if an Emoji layer is selected.";

        // =====================================================================
        // UI HELPER FUNCTIONS & EVENT HANDLERS
        // =====================================================================
        function updateButtonStateFromSelection() {
            var comp = (app && app.project) ? app.project.activeItem : null;
            if (!comp || !(comp instanceof CompItem)) {
                btnAddOrReplace.text = "\u2795 Add Emoji";
                chkSelectEmojiLayer.value = false;
                stLayerTarget.text = "Target: New Shape Layer (Will create comp if needed)";
                return;
            }
            var canDetectSelection = (typeof comp.selectedLayers !== "undefined");
            if (!canDetectSelection) {
                btnAddOrReplace.text = "\u2795 Add / Replace Emoji";
                stLayerTarget.text = "Target: Add or Replace Emoji Layer";
                return;
            }
            var selEmojiLayer = getSelectedEmojiLayer(comp);
            if (selEmojiLayer) {
                btnAddOrReplace.text = "\uD83D\uDD04 Replace Emoji";
                chkSelectEmojiLayer.value = true;
                stLayerTarget.text = "Selected: \"" + selEmojiLayer.name.substring(0, 36) + "\"";
            } else {
                btnAddOrReplace.text = "\u2795 Add Emoji";
                chkSelectEmojiLayer.value = false;
                stLayerTarget.text = "No Emoji Layer Selected \u2192 Places in New Layer";
            }
        }

        function refreshConversionReadout(entry) {
            if (!entry) return;
            isSyncingUI = true;
            try {
                var hc = entry.hexcode;
                var uInt = entry.unicodeInt;
                stBanner.text = entry.emoji + "  " + entry.name + "   |   " + entry.unicode + "  \u21C4  " + uInt;
                if (entry.emoticons && entry.emoticons.length > 0) {
                    stEmoticonsLine.text = "Wikipedia Emoticons: " + entry.emoticons.join("  ");
                } else {
                    stEmoticonsLine.text = "Tags: " + ((entry.tags && entry.tags.length > 0) ? entry.tags.slice(0, 6).join(", ") : entry.group);
                }

                slIndex.maxvalue = Math.max(2, emojiCatalog.length);
                slIndex.value = entry.index;
                etIndex.text = String(entry.index);

                slUnicodeInt.value = Math.max(slUnicodeInt.minvalue, Math.min(slUnicodeInt.maxvalue, uInt));
                etUnicodeInt.text = String(uInt);

                etUnicodeHex.text = entry.unicode;
                stFormula.text = uInt + "  (0x" + hc + " | #" + entry.index + "/" + emojiCatalog.length + ")";
            } finally {
                isSyncingUI = false;
            }
            updateButtonStateFromSelection();
        }

        function populateResultsDropdown(matches, selectEntry) {
            isSyncingUI = true;
            try {
                ddResults.removeAll();
                currentMatches = matches || [];
                if (currentMatches.length === 0) {
                    ddResults.add("item", "(No matching emojis found)");
                    ddResults.selection = 0;
                    return;
                }
                var targetIdx = 0;
                for (var i = 0; i < currentMatches.length; i++) {
                    var m = currentMatches[i];
                    var emoHint = (m.emoticons && m.emoticons.length > 0) ? ("  (" + m.emoticons.slice(0, 2).join(", ") + ")") : "";
                    var label = "#" + m.index + "  " + m.emoji + "  " + m.name + "  [" + m.unicode + " = " + m.unicodeInt + "]" + emoHint;
                    ddResults.add("item", label);
                    if (selectEntry && m.hexcode === selectEntry.hexcode) {
                        targetIdx = i;
                    }
                }
                ddResults.selection = targetIdx;
                currentEntry = currentMatches[targetIdx];
            } finally {
                isSyncingUI = false;
            }
            if (currentEntry) {
                refreshConversionReadout(currentEntry);
            }
        }

        function runSearch(preserveEntry) {
            var catIdx = ddCategory.selection ? ddCategory.selection.index : 0;
            var catId = CATEGORY_FILTERS[catIdx] ? CATEGORY_FILTERS[catIdx].id : "all";
            var q = trimStr(etSearch.text);
            var matches = searchEmojis(q, catId);
            populateResultsDropdown(matches, preserveEntry ? currentEntry : (matches[0] || currentEntry));
        }

        function executePlaceEmoji(mode) {
            if (!currentEntry) {
                alert("Please locate or select an emoji first.");
                return;
            }

            var comp = (app && app.project) ? app.project.activeItem : null;
            if (!comp || !(comp instanceof CompItem)) {
                comp = app.project.items.addComp("Emoji_Comp", 1920, 1080, 1.0, 10, 30);
                comp.openInViewer();
            }

            var sizePx = Math.max(16, parseFloat(etSize.text) || 280);
            var outlinePct = Math.max(0, parseFloat(etOutline.text) || 100);
            var showOutlines = Boolean(chkOutlines.value);

            var targetLayer = null;
            var isReplacing = false;

            if (mode === "replace") {
                targetLayer = getAnyExistingEmojiLayer(comp);
                isReplacing = Boolean(targetLayer);
            } else if (mode === "auto") {
                targetLayer = getSelectedEmojiLayer(comp);
                isReplacing = Boolean(targetLayer);
            } else {
                // mode === "add": explicitly create a new layer
                targetLayer = null;
                isReplacing = false;
            }

            app.beginUndoGroup(isReplacing ? ("Replace Emoji -> " + currentEntry.emoji) : ("Add Emoji " + currentEntry.emoji));
            try {
                applyEmojiToLayer(comp, targetLayer, currentEntry, currentSourceObj, sizePx, outlinePct, showOutlines, isReplacing);
            } finally {
                app.endUndoGroup();
            }

            updateButtonStateFromSelection();
        }

        function maybeLiveUpdateActiveEmoji() {
            if (!chkLiveScrub.value || !currentEntry) return;
            var comp = (app && app.project) ? app.project.activeItem : null;
            if (!comp || !(comp instanceof CompItem)) return;
            var targetLayer = getAnyExistingEmojiLayer(comp);
            if (!targetLayer) return;

            var sizePx = Math.max(16, parseFloat(etSize.text) || 280);
            var outlinePct = Math.max(0, parseFloat(etOutline.text) || 100);
            var showOutlines = Boolean(chkOutlines.value);
            applyEmojiToLayer(comp, targetLayer, currentEntry, currentSourceObj, sizePx, outlinePct, showOutlines, true);
            updateButtonStateFromSelection();
        }

        // ---------------------------------------------------------------------
        // WIRE UP UI EVENTS
        // ---------------------------------------------------------------------
        ddSource.onChange = function () {
            var idx = ddSource.selection ? ddSource.selection.index : 0;
            currentSourceObj = EMOJI_SOURCES[idx] || EMOJI_SOURCES[0];
            maybeLiveUpdateActiveEmoji();
        };

        btnReloadJSON.onClick = function () {
            loadAllEmojiDatabases();
            runSearch(true);
            maybeLiveUpdateActiveEmoji();
        };

        btnChooseFolder.onClick = function () {
            if (typeof Folder === "undefined" || !Folder.selectDialog) {
                alert("In the web preview, /emojis/*.json files are loaded automatically from jsx/emojis/.");
                return;
            }
            var picked = Folder.selectDialog("Select the 'emojis' folder containing emoji_index.json and openmoji_color.json");
            if (picked && picked.exists) {
                customEmojisFolderPath = picked.fsName;
                loadAllEmojiDatabases();
                runSearch(false);
            }
        };

        ddCategory.onChange = function () {
            runSearch(false);
        };

        etSearch.onChanging = function () {
            runSearch(false);
        };
        etSearch.onChange = function () {
            runSearch(false);
        };
        btnFind.onClick = function () {
            runSearch(false);
        };
        btnClearSearch.onClick = function () {
            etSearch.text = "";
            ddWikiEmoticon.selection = 0;
            runSearch(false);
        };

        ddWikiEmoticon.onChange = function () {
            if (isSyncingUI) return;
            var selIdx = ddWikiEmoticon.selection ? ddWikiEmoticon.selection.index : 0;
            if (selIdx <= 0) return;
            var we = wikiEntries[selIdx - 1];
            if (we && we.emoticons && we.emoticons.length > 0) {
                etSearch.text = we.emoticons[0];
                runSearch(false);
                maybeLiveUpdateActiveEmoji();
            }
        };

        ddResults.onChange = function () {
            if (isSyncingUI) return;
            var selIdx = ddResults.selection ? ddResults.selection.index : 0;
            if (currentMatches[selIdx]) {
                currentEntry = currentMatches[selIdx];
                refreshConversionReadout(currentEntry);
                maybeLiveUpdateActiveEmoji();
            }
        };

        // Catalog Index Slider & EditBox
        slIndex.onChanging = function () {
            if (isSyncingUI) return;
            var idx = Math.max(1, Math.min(emojiCatalog.length, Math.round(this.value)));
            var entry = emojiByIndex[idx];
            if (entry) {
                currentEntry = entry;
                refreshConversionReadout(entry);
            }
        };
        slIndex.onChange = function () {
            if (isSyncingUI) return;
            var idx = Math.max(1, Math.min(emojiCatalog.length, Math.round(this.value)));
            var entry = emojiByIndex[idx];
            if (entry) {
                currentEntry = entry;
                refreshConversionReadout(entry);
                maybeLiveUpdateActiveEmoji();
            }
        };
        etIndex.onChange = function () {
            if (isSyncingUI) return;
            var idx = parseInt(this.text, 10);
            if (isNaN(idx)) idx = currentEntry ? currentEntry.index : 1;
            idx = Math.max(1, Math.min(emojiCatalog.length, idx));
            var entry = emojiByIndex[idx];
            if (entry) {
                currentEntry = entry;
                refreshConversionReadout(entry);
                maybeLiveUpdateActiveEmoji();
            }
        };

        // Unicode Integer Slider & EditBox (Integer <-> Unicode Hex conversion)
        slUnicodeInt.onChanging = function () {
            if (isSyncingUI) return;
            var targetInt = Math.round(this.value);
            var nearest = findNearestEmojiByUnicodeInt(targetInt);
            if (nearest) {
                currentEntry = nearest;
                refreshConversionReadout(nearest);
            }
        };
        slUnicodeInt.onChange = function () {
            if (isSyncingUI) return;
            var targetInt = Math.round(this.value);
            var nearest = findNearestEmojiByUnicodeInt(targetInt);
            if (nearest) {
                currentEntry = nearest;
                refreshConversionReadout(nearest);
                maybeLiveUpdateActiveEmoji();
            }
        };
        etUnicodeInt.onChange = function () {
            if (isSyncingUI) return;
            var rawInt = parseInt(trimStr(this.text), 10);
            if (isNaN(rawInt) || rawInt <= 0) {
                if (currentEntry) refreshConversionReadout(currentEntry);
                return;
            }
            var hexConverted = unicodeIntToHex(rawInt);
            if (emojiByInt[rawInt]) {
                currentEntry = emojiByInt[rawInt];
                refreshConversionReadout(currentEntry);
                maybeLiveUpdateActiveEmoji();
            } else {
                var nearest = findNearestEmojiByUnicodeInt(rawInt);
                if (nearest) {
                    currentEntry = nearest;
                    refreshConversionReadout(nearest);
                }
                etUnicodeInt.text = String(rawInt);
                etUnicodeHex.text = "U+" + hexConverted;
                stFormula.text = rawInt + "  (0x" + hexConverted + " -> nearest: " + (nearest ? nearest.emoji : "") + ")";
            }
        };

        // Unicode Hex EditBox (Hex <-> Integer conversion)
        etUnicodeHex.onChange = function () {
            if (isSyncingUI) return;
            var rawHex = trimStr(this.text).toUpperCase().replace(/^U\+/i, "").replace(/^0X/i, "");
            var convertedInt = unicodeHexToInt(rawHex);
            if (convertedInt <= 0) {
                if (currentEntry) refreshConversionReadout(currentEntry);
                return;
            }
            if (emojiByHex[rawHex]) {
                currentEntry = emojiByHex[rawHex];
                refreshConversionReadout(currentEntry);
                maybeLiveUpdateActiveEmoji();
            } else if (emojiByInt[convertedInt]) {
                currentEntry = emojiByInt[convertedInt];
                refreshConversionReadout(currentEntry);
                maybeLiveUpdateActiveEmoji();
            } else {
                etUnicodeHex.text = "U+" + rawHex;
                etUnicodeInt.text = String(convertedInt);
                stFormula.text = convertedInt + "  (0x" + rawHex + ")";
            }
        };

        // Size & Outline Sliders
        slSize.onChanging = function () {
            etSize.text = String(Math.round(this.value));
        };
        slSize.onChange = function () {
            etSize.text = String(Math.round(this.value));
            maybeLiveUpdateActiveEmoji();
        };
        etSize.onChange = function () {
            var v = Math.max(16, Math.min(2000, parseFloat(this.text) || 280));
            slSize.value = Math.min(800, v);
            this.text = String(Math.round(v));
            maybeLiveUpdateActiveEmoji();
        };

        slOutline.onChanging = function () {
            etOutline.text = String(Math.round(this.value));
        };
        slOutline.onChange = function () {
            etOutline.text = String(Math.round(this.value));
            maybeLiveUpdateActiveEmoji();
        };
        etOutline.onChange = function () {
            var v = Math.max(0, Math.min(500, parseFloat(this.text) || 100));
            slOutline.value = Math.min(300, v);
            this.text = String(Math.round(v));
            maybeLiveUpdateActiveEmoji();
        };

        chkOutlines.onClick = function () {
            maybeLiveUpdateActiveEmoji();
        };

        chkSelectEmojiLayer.onClick = function () {
            var comp = (app && app.project) ? app.project.activeItem : null;
            if (!comp || !(comp instanceof CompItem)) return;
            if (this.value) {
                var lyr = getAnyExistingEmojiLayer(comp);
                if (lyr) {
                    try { lyr.selected = true; } catch (e) {}
                } else {
                    this.value = false;
                }
            } else {
                try {
                    if (comp.layers && comp.layers._layers) {
                        for (var i = 0; i < comp.layers._layers.length; i++) {
                            comp.layers._layers[i].selected = false;
                        }
                    }
                    var sel = comp.selectedLayers;
                    if (sel) {
                        for (var j = 0; j < sel.length; j++) {
                            try { sel[j].selected = false; } catch (e2) {}
                        }
                    }
                } catch (e3) {}
            }
            updateButtonStateFromSelection();
        };

        // Action Buttons
        btnAddOrReplace.onClick = function () {
            executePlaceEmoji("auto");
        };
        btnForceAddNew.onClick = function () {
            executePlaceEmoji("add");
        };
        btnForceReplace.onClick = function () {
            executePlaceEmoji("replace");
        };

        // Listen for timeline layer selection changes in AE_JS_builder
        if (typeof window !== "undefined" && window.addEventListener) {
            window.addEventListener("ae-layer-selection-changed", function () {
                updateButtonStateFromSelection();
            });
        }

        // Initial search for ":D" -> locates 😃 (U+1F603 = 128515)
        runSearch(false);

        win.onResizing = win.onResize = function () {
            this.layout.resize();
        };

        if (win instanceof Window) {
            win.center();
            win.show();
        } else {
            win.layout.layout(true);
            win.layout.resize();
        }

        return win;
    }

    buildUI(thisObj);

})(this);
'''

    jsx_code = jsx_code.replace("__FALLBACK_INDEX_JSON__", fallback_index_json)
    jsx_code = jsx_code.replace("__FALLBACK_WIKI_JSON__", fallback_wiki_json)
    jsx_code = jsx_code.replace("__FALLBACK_SHAPES_JSON__", fallback_shapes_json)

    with open(OUT_JSX, "w", encoding="utf-8") as f:
        f.write(jsx_code)

    print(f"Generated {OUT_JSX} ({len(jsx_code)} bytes) with {len(fallback_emojis)} embedded fallback emojis.")


if __name__ == "__main__":
    main()
