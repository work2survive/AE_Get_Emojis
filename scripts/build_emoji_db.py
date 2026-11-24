#!/usr/bin/env python3
"""
Compiles OpenMoji (color & black) and Twemoji SVG assets + Wikipedia Emoticons
into centered 72x72 After Effects cubic Bezier JSON databases in emojis/.
"""

import json
import math
import os
import re
import xml.etree.ElementTree as ET

OPENMOJI_DIR = "/tmp/openmoji"
TWEMOJI_DIR = "/tmp/twemoji"
OUT_DIR = "/home/antigravity/work2survive/AE_Get_Emojis/emojis"

KAPPA = 0.5522847498307936

# Named CSS colors fallback
NAMED_COLORS = {
    "black": [0.0, 0.0, 0.0],
    "white": [1.0, 1.0, 1.0],
    "red": [1.0, 0.0, 0.0],
    "green": [0.0, 0.5, 0.0],
    "blue": [0.0, 0.0, 1.0],
    "yellow": [1.0, 1.0, 0.0],
    "cyan": [0.0, 1.0, 1.0],
    "magenta": [1.0, 0.0, 1.0],
    "gray": [0.5, 0.5, 0.5],
    "grey": [0.5, 0.5, 0.5],
    "orange": [1.0, 0.647, 0.0],
    "purple": [0.5, 0.0, 0.5],
    "pink": [1.0, 0.753, 0.796],
    "brown": [0.647, 0.165, 0.165],
}

# Comprehensive Wikipedia List of Emoticons mapping -> Primary Unicode Hexcode
# Source: https://en.wikipedia.org/wiki/List_of_emoticons
WIKIPEDIA_EMOTICONS_LIST = [
    {
        "hexcode": "1F642",
        "meaning": "Smiley, happy face",
        "section": "Western (Sideways)",
        "emoticons": [":-)", ":)", ":-]", ":]", ":->", ":>", "8-)", "8)", ":-}", ":}", ":o)", ":c)", ":^)", "=]", "=)"],
    },
    {
        "hexcode": "1F603",
        "meaning": "Laughing, big grin, grinning with big eyes",
        "section": "Western (Sideways)",
        "emoticons": [":-D", ":D", "8-D", "8D", "=D", "=3", "B^D", "c:", "C:"],
    },
    {
        "hexcode": "1F606",
        "meaning": "Laughing, big grin with squinting eyes",
        "section": "Western (Sideways)",
        "emoticons": ["x-D", "xD", "X-D", "XD"],
    },
    {
        "hexcode": "1F604",
        "meaning": "Very happy, double chin grin",
        "section": "Western (Sideways)",
        "emoticons": [":-))", ":))"],
    },
    {
        "hexcode": "1F601",
        "meaning": "Beaming face with smiling eyes",
        "section": "Eastern / Kaomoji",
        "emoticons": ["^_^", "^-^", "^.^", "(^_^)", "(^-^)"],
    },
    {
        "hexcode": "1F602",
        "meaning": "Face with tears of joy",
        "section": "Western (Sideways)",
        "emoticons": [":'-)", ":')", ":'D", ":'-D", ":\"D"],
    },
    {
        "hexcode": "1F923",
        "meaning": "Rolling on the floor laughing (ROFL)",
        "section": "Western (Sideways)",
        "emoticons": ["ROFL", "LMAO", "XD!"],
    },
    {
        "hexcode": "1F60A",
        "meaning": "Smiling face with smiling eyes / blush",
        "section": "Eastern / Kaomoji",
        "emoticons": ["(◕‿◕)", "(｡◕‿◕｡)", "^^", "^o^"],
    },
    {
        "hexcode": "1F607",
        "meaning": "Angel, saint, innocent halo",
        "section": "Western (Sideways)",
        "emoticons": ["O:-)", "O:)", "0:-3", "0:3", "0:-)", "0:)", "0;^)"],
    },
    {
        "hexcode": "1F608",
        "meaning": "Evil, devilish grin with horns",
        "section": "Western (Sideways)",
        "emoticons": [">:-)", ">:)", "}:-)", "}:)", "3:-)", "3:)", ">;-)", ">;)"],
    },
    {
        "hexcode": "1F609",
        "meaning": "Wink, smirk",
        "section": "Western (Sideways)",
        "emoticons": [";-)", ";)", "*-)", "*)", ";-]", ";]", ";^)", ";>", ":-,", ";D", ";3"],
    },
    {
        "hexcode": "1F60B",
        "meaning": "Face savoring food, yummy",
        "section": "Western (Sideways)",
        "emoticons": [":-9", ":9"],
    },
    {
        "hexcode": "1F60D",
        "meaning": "Smiling face with heart-eyes, infatuation",
        "section": "Eastern / Kaomoji",
        "emoticons": ["(♥_♥)", "♥_♥", "<3_<3", "*❤️*"],
    },
    {
        "hexcode": "1F60E",
        "meaning": "Cool, sunglasses, shades",
        "section": "Western (Sideways)",
        "emoticons": ["B-)", "B)", "|;-)", "8-)"],
    },
    {
        "hexcode": "1F60F",
        "meaning": "Smirking, sly, Lenny face",
        "section": "Western / Kaomoji",
        "emoticons": [":-J", "( ͡° ͜ʖ ͡°)", ";->"],
    },
    {
        "hexcode": "1F610",
        "meaning": "Straight face, no expression, indecision",
        "section": "Western (Sideways)",
        "emoticons": [":-|", ":|", "._.", "-_-"],
    },
    {
        "hexcode": "1F611",
        "meaning": "Expressionless, tired, unimpressed",
        "section": "Eastern / Kaomoji",
        "emoticons": ["=_=", "-_-;", "u_u", "~_~"],
    },
    {
        "hexcode": "1F612",
        "meaning": "Unamused, skeptical, side-eye, look of disapproval",
        "section": "Eastern / Kaomoji",
        "emoticons": ["ಠ_ಠ", ">_>", "<_<", "¬_¬"],
    },
    {
        "hexcode": "1F615",
        "meaning": "Skeptical, annoyed, undecided, uneasy, hesitant",
        "section": "Western (Sideways)",
        "emoticons": [":-/", ":/", ":-.", ">:\\", ">:/", ":\\", "=/", "=\\", ":L", "=L"],
    },
    {
        "hexcode": "1F616",
        "meaning": "Confounded, scrunched face, cringed",
        "section": "Western / Kaomoji",
        "emoticons": [":S", ":-S", ">_<", ">.<"],
    },
    {
        "hexcode": "1F618",
        "meaning": "Face blowing a kiss",
        "section": "Western (Sideways)",
        "emoticons": [":-*", ":*", ":x", "^3^", "( ˘ ³˘)♥"],
    },
    {
        "hexcode": "1F61B",
        "meaning": "Tongue sticking out, cheeky, playful",
        "section": "Western (Sideways)",
        "emoticons": [":-P", ":P", ":-p", ":p", ":-Þ", ":Þ", ":-þ", ":þ", ":-b", ":b", "d:", "=p", ">:P"],
    },
    {
        "hexcode": "1F61C",
        "meaning": "Winking face with tongue",
        "section": "Western (Sideways)",
        "emoticons": [";P", ";-P", ";p", ";-p"],
    },
    {
        "hexcode": "1F61D",
        "meaning": "Squinting face with tongue, playful",
        "section": "Western (Sideways)",
        "emoticons": ["X-P", "XP", "x-p", "xp"],
    },
    {
        "hexcode": "1F61E",
        "meaning": "Disappointed, sad, dejected",
        "section": "Eastern / Kaomoji",
        "emoticons": ["v.v", "v_v", "._.;"],
    },
    {
        "hexcode": "1F620",
        "meaning": "Angry face",
        "section": "Western (Sideways)",
        "emoticons": [">:(", ">:-(", ":@"],
    },
    {
        "hexcode": "1F621",
        "meaning": "Pouting, very angry, rage, table flip",
        "section": "Western / Kaomoji",
        "emoticons": ["D:<", "(╯°□°）╯︵ ┻━┻", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻"],
    },
    {
        "hexcode": "1F622",
        "meaning": "Crying face, single tear",
        "section": "Western (Sideways)",
        "emoticons": [":'-(", ":'(", ":=(", ";("],
    },
    {
        "hexcode": "1F62D",
        "meaning": "Loudly crying face, bawling",
        "section": "Eastern / Kaomoji",
        "emoticons": ["T_T", "ToT", "T-T", ";_;", "Q_Q", "QQ", "😭"],
    },
    {
        "hexcode": "1F626",
        "meaning": "Frowning with open mouth, dismay",
        "section": "Western (Sideways)",
        "emoticons": ["D:", "D=", "D;"],
    },
    {
        "hexcode": "1F628",
        "meaning": "Fearful, horror, shock",
        "section": "Western (Sideways)",
        "emoticons": ["D-':", "D8", "DX"],
    },
    {
        "hexcode": "1F62E",
        "meaning": "Surprise, shock, open mouth",
        "section": "Western (Sideways)",
        "emoticons": [":-O", ":O", ":-o", ":o", ":-0", ":0", "8-0", ">:O", "=O", "=o", "=0", "O_O", "o_o"],
    },
    {
        "hexcode": "1F632",
        "meaning": "Astonished, gasping in shock",
        "section": "Eastern / Kaomoji",
        "emoticons": ["0_0", "O.O", "o_O", "O_o"],
    },
    {
        "hexcode": "1F633",
        "meaning": "Flushed, embarrassed, blushing",
        "section": "Western (Sideways)",
        "emoticons": [":$", ":-$", "😳"],
    },
    {
        "hexcode": "1F634",
        "meaning": "Sleeping, bored, yawn",
        "section": "Western / Kaomoji",
        "emoticons": ["|-O", "z_z", "Z_Z", "(-_-)zzz"],
    },
    {
        "hexcode": "1F635",
        "meaning": "Dizzy, knocked out, dead eyes",
        "section": "Western / Kaomoji",
        "emoticons": ["%-)", "%)", "#-)", "x_x", "X_X", "+_+"],
    },
    {
        "hexcode": "1F636",
        "meaning": "Face without mouth, speechless",
        "section": "Western (Sideways)",
        "emoticons": [":-X", ":X", ":-#", ":#", ":-&", ":&"],
    },
    {
        "hexcode": "1F910",
        "meaning": "Zipper-mouth face, sealed lips",
        "section": "Western (Sideways)",
        "emoticons": [":-Z", ":Z"],
    },
    {
        "hexcode": "1F641",
        "meaning": "Frowning, sad, pouting",
        "section": "Western (Sideways)",
        "emoticons": [":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":-||", ":{"],
    },
    {
        "hexcode": "1F63A",
        "meaning": "Grinning cat, curly mouth / cat smile",
        "section": "Western / Kaomoji",
        "emoticons": [":-3", ":3", "=3", "x3", "X3", ">:3", "uwu", "UwU", "owo", "OwO"],
    },
    {
        "hexcode": "1F911",
        "meaning": "Money-mouth face",
        "section": "Eastern / Kaomoji",
        "emoticons": ["$_$", "($.$)"],
    },
    {
        "hexcode": "1F929",
        "meaning": "Star-struck, amazed",
        "section": "Eastern / Kaomoji",
        "emoticons": ["*_*", "*o*", "☆_☆"],
    },
    {
        "hexcode": "1F928",
        "meaning": "Face with raised eyebrow, skeptical",
        "section": "Western (Sideways)",
        "emoticons": ["',:-I", "',:-l", "🤨"],
    },
    {
        "hexcode": "1F914",
        "meaning": "Thinking face, pondering",
        "section": "Western (Sideways)",
        "emoticons": [":thinking:", ":?", ":-?"],
    },
    {
        "hexcode": "1F917",
        "meaning": "Smiling face with open hands, hug",
        "section": "Eastern / Kaomoji",
        "emoticons": ["(づ｡◕‿‿◕｡)づ", "༼ つ ◕_◕ ༽つ"],
    },
    {
        "hexcode": "1F937",
        "meaning": "Person shrugging",
        "section": "Eastern / Kaomoji",
        "emoticons": ["¯\\_(ツ)_/¯", "¯\\(°_o)/¯"],
    },
    {
        "hexcode": "1F64C",
        "meaning": "Raising hands, cheer, yay",
        "section": "Western (Posture)",
        "emoticons": ["\\o/", "*\\0/*"],
    },
    {
        "hexcode": "1FAE1",
        "meaning": "Saluting face / salute",
        "section": "Western (Posture)",
        "emoticons": ["o7", "<o/"],
    },
    {
        "hexcode": "2764",
        "meaning": "Red heart, love",
        "section": "Western (Symbols)",
        "emoticons": ["<3", "<33", ":heart:"],
    },
    {
        "hexcode": "1F494",
        "meaning": "Broken heart",
        "section": "Western (Symbols)",
        "emoticons": ["</3", "<\\3"],
    },
    {
        "hexcode": "1F339",
        "meaning": "Single rose",
        "section": "Western (Symbols)",
        "emoticons": ["@};-", "@}->--", "@}-;-'---", "@>-->--"],
    },
    {
        "hexcode": "1F918",
        "meaning": "Sign of the horns, rock on",
        "section": "Western (Symbols)",
        "emoticons": ["\\m/", "\\,,/"],
    },
    {
        "hexcode": "1F44D",
        "meaning": "Thumbs up, approve",
        "section": "Western (Symbols)",
        "emoticons": ["(y)", "(Y)", ":+1:", ":thumbsup:"],
    },
    {
        "hexcode": "1F44E",
        "meaning": "Thumbs down, disapprove",
        "section": "Western (Symbols)",
        "emoticons": ["(n)", "(N)", ":-1:", ":thumbsdown:"],
    },
    {
        "hexcode": "1F41F",
        "meaning": "Fish",
        "section": "Western (Symbols)",
        "emoticons": ["><>", "<><", "<*)))>-{"],
    },
    {
        "hexcode": "1F385",
        "meaning": "Santa Claus",
        "section": "Western (Sideways)",
        "emoticons": ["*<|:-)"],
    },
    {
        "hexcode": "2615",
        "meaning": "Hot beverage, coffee mug",
        "section": "Western (Symbols)",
        "emoticons": ["c[_]", "c\\_/"],
    },
    {
        "hexcode": "1F43B",
        "meaning": "Bear face",
        "section": "Eastern / Kaomoji",
        "emoticons": ["ʕ•ᴥ•ʔ", "⊂(￣(ｴ)￣)⊃"],
    },
    {
        "hexcode": "1F480",
        "meaning": "Skull, dead",
        "section": "Western (Sideways)",
        "emoticons": ["8-X", "8=X", ":skull:"],
    },
    {
        "hexcode": "1F525",
        "meaning": "Fire, lit",
        "section": "Shortcodes",
        "emoticons": [":fire:"],
    },
    {
        "hexcode": "1F4AF",
        "meaning": "Hundred points, 100%",
        "section": "Shortcodes",
        "emoticons": [":100:", "100%"],
    },
    {
        "hexcode": "1F4A9",
        "meaning": "Pile of poo",
        "section": "Shortcodes",
        "emoticons": [":poop:", ":hankey:"],
    },
    {
        "hexcode": "2728",
        "meaning": "Sparkles",
        "section": "Shortcodes",
        "emoticons": [":sparkles:", "*+*"],
    },
    {
        "hexcode": "1F680",
        "meaning": "Rocket",
        "section": "Shortcodes",
        "emoticons": [":rocket:"],
    },
]

# Curated list of ~200 popular single-codepoint hexcodes across categories
CURATED_HEXCODES = [
    # Smileys & Emotion
    "1F600", "1F603", "1F604", "1F601", "1F606", "1F605", "1F923", "1F602",
    "1F642", "1F643", "1FAE0", "1F609", "1F60A", "1F607", "1F970", "1F60D",
    "1F929", "1F618", "1F617", "1F61A", "1F619", "1F972", "1F60B", "1F61B",
    "1F61C", "1F92A", "1F61D", "1F911", "1F917", "1F92D", "1F92B", "1F914",
    "1FAE1", "1F910", "1F928", "1F610", "1F611", "1F636", "1FAE5", "1F60F",
    "1F612", "1F644", "1F62C", "1F925", "1F60C", "1F614", "1F62A", "1F924",
    "1F634", "1F637", "1F912", "1F915", "1F922", "1F92E", "1F927", "1F975",
    "1F976", "1F974", "1F635", "1F92F", "1F920", "1F973", "1F978", "1F60E",
    "1F913", "1F9D0", "1F615", "1FAE4", "1F61F", "1F641", "1F62E", "1F62F",
    "1F632", "1F633", "1F97A", "1F979", "1F626", "1F627", "1F628", "1F630",
    "1F625", "1F622", "1F62D", "1F631", "1F616", "1F623", "1F61E", "1F613",
    "1F629", "1F62B", "1F971", "1F624", "1F621", "1F620", "1F92C", "1F608",
    "1F47F", "1F480", "1F4A9", "1F921", "1F47B", "1F47D", "1F47E", "1F916",
    "1F63A", "1F638", "1F639", "1F63B", "1F63C", "1F63D", "1F640", "1F63F",
    "1F63E", "1F648", "1F649", "1F64A",
    # People & Gestures
    "1F44B", "1F91A", "1F590", "270B", "1F596", "1F44C", "1F90C", "1F90F",
    "270C", "1F91E", "1FAF0", "1F91F", "1F918", "1F919", "1F448", "1F449",
    "1F446", "1F447", "261D", "1FAF5", "1F44D", "1F44E", "270A", "1F44A",
    "1F91B", "1F91C", "1F44F", "1F64C", "1FAF6", "1F450", "1F932", "1F91D",
    "1F64F", "270D", "1F4AA", "1F9E0", "1F440", "1F441", "1F444", "1F937",
    "1F385", "1F451",
    # Hearts & Symbols
    "2764", "1F9E1", "1F49B", "1F49A", "1F499", "1F49C", "1F5A4", "1F90D",
    "1F90E", "1F494", "1F495", "1F496", "1F497", "1F498", "1F49D", "1F49E",
    "1F48B", "1F4AF", "1F4A2", "1F4A5", "1F4AB", "1F4A6", "1F4A8", "1F4A3",
    "1F4AC", "1F4AD", "1F4A4", "1F525", "2728", "1F31F", "2B50", "26A1",
    "2705", "274C", "26A0", "2757", "2753", "1F6AB", "267B", "1F3AF",
    # Animals & Nature
    "1F436", "1F431", "1F42D", "1F430", "1F98A", "1F43B", "1F43C", "1F428",
    "1F42F", "1F981", "1F42E", "1F437", "1F438", "1F435", "1F414", "1F427",
    "1F989", "1F984", "1F41D", "1F98B", "1F422", "1F419", "1F42C", "1F433",
    "1F41F", "1F996", "1F339", "1F33B", "1F338", "1F340", "1F335", "1F344",
    # Food & Drink
    "1F34E", "1F34C", "1F353", "1F349", "1F352", "1F351", "1F34D", "1F951",
    "1F336", "1F354", "1F35F", "1F355", "1F32D", "1F32E", "1F363", "1F35C",
    "1F369", "1F36A", "1F382", "1F370", "1F366", "1F36B", "1F36D", "2615",
    "1F37A", "1F37B", "1F377", "1F379", "1F9CB",
    # Activities, Travel & Objects
    "26BD", "1F3C0", "1F3C6", "1F3AE", "1F3B2", "1F389", "1F388", "1F381",
    "1F3B5", "1F3B8", "1F3A4", "1F3A7", "1F3AC", "1F4F7", "1F4BB", "1F4F1",
    "1F4A1", "1F4B0", "1F48E", "1F511", "1F512", "1F50D", "1F680", "2708",
    "1F697", "1F6A8", "2600", "1F319", "1F308", "2601", "2744", "1F30D",
]


def parse_color(val):
    if not val:
        return None
    val = val.strip()
    if val.lower() in ("none", "transparent"):
        return None
    if val.lower() in NAMED_COLORS:
        return NAMED_COLORS[val.lower()]
    if val.startswith("#"):
        h = val[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) >= 6:
            return [
                round(int(h[0:2], 16) / 255.0, 4),
                round(int(h[2:4], 16) / 255.0, 4),
                round(int(h[4:6], 16) / 255.0, 4),
            ]
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", val)
    if m:
        return [
            round(int(m.group(1)) / 255.0, 4),
            round(int(m.group(2)) / 255.0, 4),
            round(int(m.group(3)) / 255.0, 4),
        ]
    return None


def mat_mul(m1, m2):
    # Affine 2D matrix [a, b, c, d, e, f]
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return [
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    ]


def parse_transform(transform_str):
    mat = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    if not transform_str:
        return mat
    for fn, args_str in re.findall(r"(\w+)\s*\(([^)]*)\)", transform_str):
        nums = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", args_str)]
        if fn == "matrix" and len(nums) == 6:
            mat = mat_mul(mat, nums)
        elif fn == "translate":
            tx = nums[0] if len(nums) > 0 else 0.0
            ty = nums[1] if len(nums) > 1 else 0.0
            mat = mat_mul(mat, [1.0, 0.0, 0.0, 1.0, tx, ty])
        elif fn == "scale":
            sx = nums[0] if len(nums) > 0 else 1.0
            sy = nums[1] if len(nums) > 1 else sx
            mat = mat_mul(mat, [sx, 0.0, 0.0, sy, 0.0, 0.0])
        elif fn == "rotate":
            ang = math.radians(nums[0]) if len(nums) > 0 else 0.0
            ca, sa = math.cos(ang), math.sin(ang)
            if len(nums) == 3:
                cx, cy = nums[1], nums[2]
                mat = mat_mul(mat, [1.0, 0.0, 0.0, 1.0, cx, cy])
                mat = mat_mul(mat, [ca, sa, -sa, ca, 0.0, 0.0])
                mat = mat_mul(mat, [1.0, 0.0, 0.0, 1.0, -cx, -cy])
            else:
                mat = mat_mul(mat, [ca, sa, -sa, ca, 0.0, 0.0])
    return mat


def apply_pt(mat, x, y):
    a, b, c, d, e, f = mat
    return [a * x + c * y + e, b * x + d * y + f]


def apply_vec(mat, dx, dy):
    a, b, c, d, _, _ = mat
    return [a * dx + c * dy, b * dx + d * dy]


def arc_to_beziers(x1, y1, rx, ry, phi_deg, fa, fs, x2, y2):
    """Convert SVG elliptical arc to list of cubic Bezier segments [(cp1x, cp1y, cp2x, cp2y, x, y), ...]."""
    if (x1 == x2 and y1 == y2) or rx == 0 or ry == 0:
        return [(x1, y1, x2, y2, x2, y2)]
    rx = abs(rx)
    ry = abs(ry)
    phi = math.radians(phi_deg % 360.0)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    dx2 = (x1 - x2) / 2.0
    dy2 = (y1 - y2) / 2.0
    x1p = cos_phi * dx2 + sin_phi * dy2
    y1p = -sin_phi * dx2 + cos_phi * dy2

    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1.0:
        s = math.sqrt(lam)
        rx *= s
        ry *= s

    rx2 = rx * rx
    ry2 = ry * ry
    x1p2 = x1p * x1p
    y1p2 = y1p * y1p

    num = max(0.0, rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2)
    den = rx2 * y1p2 + ry2 * x1p2
    rad = math.sqrt(num / den) if den != 0 else 0.0
    if fa == fs:
        rad = -rad

    cxp = rad * (rx * y1p / ry)
    cyp = rad * (-ry * x1p / rx)

    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2.0
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2.0

    def vec_angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        mag = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        if mag == 0:
            return 0.0
        c = max(-1.0, min(1.0, dot / mag))
        ang = math.acos(c)
        return -ang if (ux * vy - uy * vx) < 0 else ang

    ux = (x1p - cxp) / rx
    uy = (y1p - cyp) / ry
    vx = (-x1p - cxp) / rx
    vy = (-y1p - cyp) / ry

    theta1 = vec_angle(1.0, 0.0, ux, uy)
    dtheta = vec_angle(ux, uy, vx, vy)

    if fs == 0 and dtheta > 0:
        dtheta -= 2.0 * math.pi
    elif fs == 1 and dtheta < 0:
        dtheta += 2.0 * math.pi

    segs = max(1, int(math.ceil(abs(dtheta) / (math.pi / 2.0))))
    delta = dtheta / segs
    alpha = (4.0 / 3.0) * math.tan(delta / 4.0)

    beziers = []
    t = theta1
    for _ in range(segs):
        cos_t1, sin_t1 = math.cos(t), math.sin(t)
        cos_t2, sin_t2 = math.cos(t + delta), math.sin(t + delta)

        q1x = rx * (cos_t1 - alpha * sin_t1)
        q1y = ry * (sin_t1 + alpha * cos_t1)
        q2x = rx * (cos_t2 + alpha * sin_t2)
        q2y = ry * (sin_t2 - alpha * cos_t2)
        qx = rx * cos_t2
        qy = ry * sin_t2

        cp1x = cos_phi * q1x - sin_phi * q1y + cx
        cp1y = sin_phi * q1x + cos_phi * q1y + cy
        cp2x = cos_phi * q2x - sin_phi * q2y + cx
        cp2y = sin_phi * q2x + cos_phi * q2y + cy
        ex = cos_phi * qx - sin_phi * qy + cx
        ey = sin_phi * qx + cos_phi * qy + cy

        beziers.append((cp1x, cp1y, cp2x, cp2y, ex, ey))
        t += delta

    return beziers


TOKEN_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)")


def parse_svg_d(d_str):
    """Parse SVG path 'd' into list of subpaths, each subpath has {'v':[], 'i':[], 'o':[], 'c':bool}."""
    tokens = []
    for m in TOKEN_RE.finditer(d_str or ""):
        if m.group(1):
            tokens.append(m.group(1))
        else:
            tokens.append(float(m.group(2)))

    subpaths = []
    cur = None
    cx, cy = 0.0, 0.0
    sx, sy = 0.0, 0.0
    last_cmd = ""
    last_ctrl_x, last_ctrl_y = 0.0, 0.0

    def ensure_subpath(x, y):
        nonlocal cur
        if cur is None:
            cur = {"v": [[x, y]], "i": [[0.0, 0.0]], "o": [[0.0, 0.0]], "c": False}
            subpaths.append(cur)

    def add_cubic(cp1x, cp1y, cp2x, cp2y, x, y):
        ensure_subpath(cx, cy)
        px, py = cur["v"][-1]
        cur["o"][-1] = [cp1x - px, cp1y - py]
        cur["v"].append([x, y])
        cur["i"].append([cp2x - x, cp2y - y])
        cur["o"].append([0.0, 0.0])

    def add_line(x, y):
        ensure_subpath(cx, cy)
        cur["v"].append([x, y])
        cur["i"].append([0.0, 0.0])
        cur["o"].append([0.0, 0.0])

    idx = 0
    n = len(tokens)
    cmd = None

    while idx < n:
        if isinstance(tokens[idx], str):
            cmd = tokens[idx]
            idx += 1
        elif cmd is None:
            break

        if cmd in ("M", "m"):
            if idx + 1 >= n:
                break
            x, y = tokens[idx], tokens[idx + 1]
            idx += 2
            if cmd == "m":
                x += cx
                y += cy
            cx, cy = x, y
            sx, sy = x, y
            cur = {"v": [[cx, cy]], "i": [[0.0, 0.0]], "o": [[0.0, 0.0]], "c": False}
            subpaths.append(cur)
            last_cmd = cmd
            cmd = "L" if cmd == "M" else "l"

        elif cmd in ("L", "l"):
            if idx + 1 >= n:
                break
            x, y = tokens[idx], tokens[idx + 1]
            idx += 2
            if cmd == "l":
                x += cx
                y += cy
            add_line(x, y)
            cx, cy = x, y
            last_cmd = cmd

        elif cmd in ("H", "h"):
            if idx >= n:
                break
            x = tokens[idx]
            idx += 1
            if cmd == "h":
                x += cx
            add_line(x, cy)
            cx = x
            last_cmd = cmd

        elif cmd in ("V", "v"):
            if idx >= n:
                break
            y = tokens[idx]
            idx += 1
            if cmd == "v":
                y += cy
            add_line(cx, y)
            cy = y
            last_cmd = cmd

        elif cmd in ("C", "c"):
            if idx + 5 >= n:
                break
            x1, y1, x2, y2, x, y = tokens[idx : idx + 6]
            idx += 6
            if cmd == "c":
                x1 += cx
                y1 += cy
                x2 += cx
                y2 += cy
                x += cx
                y += cy
            add_cubic(x1, y1, x2, y2, x, y)
            last_ctrl_x, last_ctrl_y = x2, y2
            cx, cy = x, y
            last_cmd = cmd

        elif cmd in ("S", "s"):
            if idx + 3 >= n:
                break
            x2, y2, x, y = tokens[idx : idx + 4]
            idx += 4
            if cmd == "s":
                x2 += cx
                y2 += cy
                x += cx
                y += cy
            if last_cmd in ("C", "c", "S", "s"):
                x1 = 2.0 * cx - last_ctrl_x
                y1 = 2.0 * cy - last_ctrl_y
            else:
                x1, y1 = cx, cy
            add_cubic(x1, y1, x2, y2, x, y)
            last_ctrl_x, last_ctrl_y = x2, y2
            cx, cy = x, y
            last_cmd = cmd

        elif cmd in ("Q", "q"):
            if idx + 3 >= n:
                break
            qx, qy, x, y = tokens[idx : idx + 4]
            idx += 4
            if cmd == "q":
                qx += cx
                qy += cy
                x += cx
                y += cy
            cp1x = cx + (2.0 / 3.0) * (qx - cx)
            cp1y = cy + (2.0 / 3.0) * (qy - cy)
            cp2x = x + (2.0 / 3.0) * (qx - x)
            cp2y = y + (2.0 / 3.0) * (qy - y)
            add_cubic(cp1x, cp1y, cp2x, cp2y, x, y)
            last_ctrl_x, last_ctrl_y = qx, qy
            cx, cy = x, y
            last_cmd = cmd

        elif cmd in ("T", "t"):
            if idx + 1 >= n:
                break
            x, y = tokens[idx : idx + 2]
            idx += 2
            if cmd == "t":
                x += cx
                y += cy
            if last_cmd in ("Q", "q", "T", "t"):
                qx = 2.0 * cx - last_ctrl_x
                qy = 2.0 * cy - last_ctrl_y
            else:
                qx, qy = cx, cy
            cp1x = cx + (2.0 / 3.0) * (qx - cx)
            cp1y = cy + (2.0 / 3.0) * (qy - cy)
            cp2x = x + (2.0 / 3.0) * (qx - x)
            cp2y = y + (2.0 / 3.0) * (qy - y)
            add_cubic(cp1x, cp1y, cp2x, cp2y, x, y)
            last_ctrl_x, last_ctrl_y = qx, qy
            cx, cy = x, y
            last_cmd = cmd

        elif cmd in ("A", "a"):
            if idx + 6 >= n:
                break
            rx, ry, rot, fa, fs, x, y = tokens[idx : idx + 7]
            idx += 7
            if cmd == "a":
                x += cx
                y += cy
            fa = 1 if fa != 0 else 0
            fs = 1 if fs != 0 else 0
            for cp1x, cp1y, cp2x, cp2y, ex, ey in arc_to_beziers(cx, cy, rx, ry, rot, fa, fs, x, y):
                add_cubic(cp1x, cp1y, cp2x, cp2y, ex, ey)
                cx, cy = ex, ey
            last_cmd = cmd

        elif cmd in ("Z", "z"):
            if cur is not None:
                cur["c"] = True
                if len(cur["v"]) > 1:
                    fx, fy = cur["v"][0]
                    lx, ly = cur["v"][-1]
                    if math.hypot(fx - lx, fy - ly) < 1e-3:
                        cur["i"][0] = cur["i"][-1]
                        cur["v"].pop()
                        cur["i"].pop()
                        cur["o"].pop()
            cx, cy = sx, sy
            last_cmd = cmd
            cmd = None

    return [sp for sp in subpaths if len(sp["v"]) >= 2]


def make_ellipse_subpath(cx, cy, rx, ry):
    ox = rx * KAPPA
    oy = ry * KAPPA
    return {
        "v": [[cx, cy - ry], [cx + rx, cy], [cx, cy + ry], [cx - rx, cy]],
        "i": [[-ox, 0.0], [0.0, -oy], [ox, 0.0], [0.0, oy]],
        "o": [[ox, 0.0], [0.0, oy], [-ox, 0.0], [0.0, -oy]],
        "c": True,
    }


def make_rect_subpath(x, y, w, h, rx=0.0, ry=0.0):
    if rx <= 0 and ry <= 0:
        return {
            "v": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
            "i": [[0.0, 0.0]] * 4,
            "o": [[0.0, 0.0]] * 4,
            "c": True,
        }
    rx = min(rx if rx > 0 else ry, w / 2.0)
    ry = min(ry if ry > 0 else rx, h / 2.0)
    ox = rx * KAPPA
    oy = ry * KAPPA
    v = [
        [x + rx, y],
        [x + w - rx, y],
        [x + w, y + ry],
        [x + w, y + h - ry],
        [x + w - rx, y + h],
        [x + rx, y + h],
        [x, y + h - ry],
        [x, y + ry],
    ]
    i = [
        [-ox, 0.0],
        [0.0, 0.0],
        [0.0, -oy],
        [0.0, 0.0],
        [ox, 0.0],
        [0.0, 0.0],
        [0.0, oy],
        [0.0, 0.0],
    ]
    o = [
        [0.0, 0.0],
        [ox, 0.0],
        [0.0, 0.0],
        [0.0, oy],
        [0.0, 0.0],
        [-ox, 0.0],
        [0.0, 0.0],
        [0.0, -oy],
    ]
    return {"v": v, "i": i, "o": o, "c": True}


def parse_points(pts_str, closed):
    nums = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", pts_str or "")]
    v = []
    for k in range(0, len(nums) - 1, 2):
        v.append([nums[k], nums[k + 1]])
    if len(v) < 2:
        return None
    if closed and len(v) > 2 and math.hypot(v[0][0] - v[-1][0], v[0][1] - v[-1][1]) < 1e-3:
        v.pop()
    return {
        "v": v,
        "i": [[0.0, 0.0] for _ in v],
        "o": [[0.0, 0.0] for _ in v],
        "c": closed,
    }


def extract_style_attrs(el, inherited):
    state = dict(inherited)
    style_str = el.attrib.get("style", "")
    style_map = {}
    for part in style_str.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            style_map[k.strip()] = v.strip()

    for key in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "opacity", "fill-opacity", "stroke-opacity", "display", "visibility"):
        val = style_map.get(key, el.attrib.get(key))
        if val is not None:
            state[key] = val
    return state


def compile_svg_file(svg_path, source_type="openmoji_color"):
    """
    Parse an SVG file into a list of centered 72x72 shape dicts:
    {
      "v": [[x,y], ...],
      "i": [[ix,iy], ...],
      "o": [[ox,oy], ...],
      "c": bool,
      "f": [r,g,b] (optional),
      "fo": float (optional, 0..100),
      "s": [r,g,b] (optional),
      "sw": float (optional),
      "so": float (optional, 0..100),
      "lc": int (1=butt, 2=round, 3=projecting),
      "lj": int (1=miter, 2=round, 3=bevel),
      "l": 1 (if part of OpenMoji #line group)
    }
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    vb = root.attrib.get("viewBox", "0 0 72 72")
    vb_nums = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", vb)]
    vb_w = vb_nums[2] if len(vb_nums) >= 4 else 72.0
    vb_h = vb_nums[3] if len(vb_nums) >= 4 else 72.0

    # Normalize to 72x72 em-box centered at (0, 0)
    # OpenMoji has 46x46 optical glyph within 72x72 viewBox -> [-23..23]
    # Twemoji viewBox is 36x36 edge-to-edge; target 46x46 optical glyph centered at (0,0) -> [-23..23]
    target_dim = 46.0 if source_type == "twemoji_color" else 72.0
    half_dim = target_dim / 2.0
    scale_x = target_dim / vb_w
    scale_y = target_dim / vb_h
    root_mat = [scale_x, 0.0, 0.0, scale_y, -half_dim, -half_dim]

    shapes = []

    default_state = {
        "fill": "#000000",
        "stroke": "none",
        "stroke-width": "1",
        "stroke-linecap": "butt",
        "stroke-linejoin": "miter",
        "opacity": "1",
        "fill-opacity": "1",
        "stroke-opacity": "1",
        "display": "inline",
        "visibility": "visible",
    }

    def walk(el, cur_mat, cur_state, group_id=""):
        tag = el.tag.split("}")[-1]
        el_id = el.attrib.get("id", "")
        if el_id in ("grid", "color-foreground"):
            # Skip non-artwork grid layers if any
            if el_id == "grid":
                return
        active_group = el_id if el_id in ("color", "line", "hair", "skin", "skin-shadow") else group_id

        state = extract_style_attrs(el, cur_state)
        if state.get("display") == "none" or state.get("visibility") == "hidden":
            return

        t_mat = parse_transform(el.attrib.get("transform", ""))
        mat = mat_mul(cur_mat, t_mat)

        if tag in ("svg", "g"):
            for child in el:
                walk(child, mat, state, active_group)
            return

        raw_subpaths = []
        if tag == "path":
            raw_subpaths = parse_svg_d(el.attrib.get("d", ""))
        elif tag == "circle":
            cx = float(el.attrib.get("cx", 0))
            cy = float(el.attrib.get("cy", 0))
            r = float(el.attrib.get("r", 0))
            if r > 0:
                raw_subpaths = [make_ellipse_subpath(cx, cy, r, r)]
        elif tag == "ellipse":
            cx = float(el.attrib.get("cx", 0))
            cy = float(el.attrib.get("cy", 0))
            rx = float(el.attrib.get("rx", 0))
            ry = float(el.attrib.get("ry", 0))
            if rx > 0 and ry > 0:
                raw_subpaths = [make_ellipse_subpath(cx, cy, rx, ry)]
        elif tag == "rect":
            x = float(el.attrib.get("x", 0))
            y = float(el.attrib.get("y", 0))
            w = float(el.attrib.get("width", 0))
            h = float(el.attrib.get("height", 0))
            rx = float(el.attrib.get("rx", 0))
            ry = float(el.attrib.get("ry", 0))
            if w > 0 and h > 0:
                raw_subpaths = [make_rect_subpath(x, y, w, h, rx, ry)]
        elif tag == "polygon":
            sp = parse_points(el.attrib.get("points", ""), True)
            if sp:
                raw_subpaths = [sp]
        elif tag == "polyline":
            sp = parse_points(el.attrib.get("points", ""), False)
            if sp:
                raw_subpaths = [sp]
        elif tag == "line":
            x1 = float(el.attrib.get("x1", 0))
            y1 = float(el.attrib.get("y1", 0))
            x2 = float(el.attrib.get("x2", 0))
            y2 = float(el.attrib.get("y2", 0))
            raw_subpaths = [{
                "v": [[x1, y1], [x2, y2]],
                "i": [[0.0, 0.0], [0.0, 0.0]],
                "o": [[0.0, 0.0], [0.0, 0.0]],
                "c": False,
            }]

        if not raw_subpaths:
            return

        fill_rgb = parse_color(state.get("fill"))
        stroke_rgb = parse_color(state.get("stroke"))
        if fill_rgb is None and stroke_rgb is None:
            return

        op = float(state.get("opacity", 1.0))
        f_op = round(op * float(state.get("fill-opacity", 1.0)) * 100.0, 1)
        s_op = round(op * float(state.get("stroke-opacity", 1.0)) * 100.0, 1)

        sw_raw = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", str(state.get("stroke-width", "1")))
        sw = float(sw_raw[0]) if sw_raw else 1.0
        # Scale stroke width by matrix average scale
        mat_scale = math.hypot(mat[0], mat[1])
        sw = round(sw * mat_scale, 2)

        lc_map = {"butt": 1, "round": 2, "square": 3}
        lj_map = {"miter": 1, "round": 2, "bevel": 3}
        lc = lc_map.get(state.get("stroke-linecap", "butt"), 1)
        lj = lj_map.get(state.get("stroke-linejoin", "miter"), 1)

        is_line_group = 1 if active_group == "line" or source_type == "openmoji_black" else 0

        transformed_subpaths = []
        for sp in raw_subpaths:
            tv = []
            ti = []
            to = []
            for idx_pt in range(len(sp["v"])):
                vx, vy = apply_pt(mat, sp["v"][idx_pt][0], sp["v"][idx_pt][1])
                ix, iy = apply_vec(mat, sp["i"][idx_pt][0], sp["i"][idx_pt][1])
                ox, oy = apply_vec(mat, sp["o"][idx_pt][0], sp["o"][idx_pt][1])
                tv.append([round(vx, 2), round(vy, 2)])
                ti.append([round(ix, 2), round(iy, 2)])
                to.append([round(ox, 2), round(oy, 2)])
            transformed_subpaths.append({
                "v": tv,
                "i": ti,
                "o": to,
                "c": sp["c"],
            })

        if len(transformed_subpaths) == 1:
            item = dict(transformed_subpaths[0])
        else:
            item = {"p": transformed_subpaths}

        if fill_rgb is not None:
            item["f"] = fill_rgb
            if f_op < 100.0:
                item["fo"] = f_op
        if stroke_rgb is not None and sw > 0:
            item["s"] = stroke_rgb
            item["sw"] = sw
            if s_op < 100.0:
                item["so"] = s_op
            if lc != 1:
                item["lc"] = lc
            if lj != 1:
                item["lj"] = lj
        if is_line_group:
            item["l"] = 1

        shapes.append(item)

    walk(root, root_mat, default_state, "")
    return shapes


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(os.path.join(OPENMOJI_DIR, "data", "openmoji.json"), "r", encoding="utf-8") as f:
        openmoji_meta = json.load(f)

    meta_by_hex = {}
    for entry in openmoji_meta:
        hc = entry["hexcode"].upper()
        meta_by_hex[hc] = entry
        # Also map stripped FE0F if needed
        hc_clean = "-".join(p for p in hc.split("-") if p != "FE0F")
        if hc_clean not in meta_by_hex:
            meta_by_hex[hc_clean] = entry

    # Build emoticon reverse map: hexcode -> list of emoticons
    emoticons_by_hex = {}
    emoticon_lookup = {}
    for row in WIKIPEDIA_EMOTICONS_LIST:
        hc = row["hexcode"].upper()
        emoticons_by_hex.setdefault(hc, [])
        for emo in row["emoticons"]:
            if emo not in emoticons_by_hex[hc]:
                emoticons_by_hex[hc].append(emo)
            emoticon_lookup[emo] = hc
            emoticon_lookup[emo.lower()] = hc

    # Combine all target hexcodes preserving order and uniqueness
    all_hexcodes = []
    seen_hex = set()
    for row in WIKIPEDIA_EMOTICONS_LIST:
        hc = row["hexcode"].upper()
        if hc not in seen_hex:
            all_hexcodes.append(hc)
            seen_hex.add(hc)
    for hc in CURATED_HEXCODES:
        hc = hc.upper()
        if hc not in seen_hex:
            all_hexcodes.append(hc)
            seen_hex.add(hc)

    emoji_index = []
    openmoji_color_db = {}
    openmoji_black_db = {}
    twemoji_color_db = {}

    idx_counter = 1
    for hc in all_hexcodes:
        meta = meta_by_hex.get(hc)
        if not meta:
            continue

        actual_hc = meta["hexcode"].upper()
        primary_cp_hex = hc.split("-")[0]
        unicode_int = int(primary_cp_hex, 16)

        om_color_svg = os.path.join(OPENMOJI_DIR, "color", "svg", f"{actual_hc}.svg")
        if not os.path.exists(om_color_svg):
            om_color_svg = os.path.join(OPENMOJI_DIR, "color", "svg", f"{hc}.svg")
        if not os.path.exists(om_color_svg):
            continue

        om_black_svg = os.path.join(OPENMOJI_DIR, "black", "svg", f"{actual_hc}.svg")
        if not os.path.exists(om_black_svg):
            om_black_svg = os.path.join(OPENMOJI_DIR, "black", "svg", f"{hc}.svg")

        tw_name = actual_hc.lower()
        tw_svg = os.path.join(TWEMOJI_DIR, "assets", "svg", f"{tw_name}.svg")
        if not os.path.exists(tw_svg):
            tw_svg = os.path.join(TWEMOJI_DIR, "assets", "svg", f"{hc.lower()}.svg")

        om_color_shapes = compile_svg_file(om_color_svg, "openmoji_color")
        if not om_color_shapes:
            continue

        om_black_shapes = compile_svg_file(om_black_svg, "openmoji_black") if os.path.exists(om_black_svg) else []
        tw_color_shapes = compile_svg_file(tw_svg, "twemoji_color") if os.path.exists(tw_svg) else om_color_shapes

        sources = ["openmoji_color", "openmoji_flat"]
        if om_black_shapes:
            sources.append("openmoji_black")
        if os.path.exists(tw_svg):
            sources.append("twemoji_color")

        tags_list = [t.strip() for t in (meta.get("tags", "") + "," + meta.get("openmoji_tags", "")).split(",") if t.strip()]
        seen_t = set()
        dedup_tags = []
        for t in tags_list:
            tl = t.lower()
            if tl not in seen_t:
                seen_t.add(tl)
                dedup_tags.append(t)

        emos = emoticons_by_hex.get(hc, [])

        entry_record = {
            "index": idx_counter,
            "hexcode": hc,
            "unicode": f"U+{hc}",
            "unicodeInt": unicode_int,
            "emoji": meta.get("emoji", chr(unicode_int)),
            "name": meta.get("annotation", hc),
            "group": meta.get("group", "smileys-emotion"),
            "subgroups": meta.get("subgroups", ""),
            "tags": dedup_tags,
            "emoticons": emos,
            "sources": sources,
        }
        emoji_index.append(entry_record)

        openmoji_color_db[hc] = om_color_shapes
        openmoji_black_db[hc] = om_black_shapes if om_black_shapes else om_color_shapes
        twemoji_color_db[hc] = tw_color_shapes

        idx_counter += 1

    # Write emoji_index.json
    with open(os.path.join(OUT_DIR, "emoji_index.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": "1.0.0",
                "generator": "AE_Get_Emojis build_emoji_db.py",
                "CoordinateSpace": "72x72 centered at [0,0] (-36..+36)",
                "totalCount": len(emoji_index),
                "sources": [
                    {
                        "id": "openmoji_color",
                        "name": "OpenMoji Color (Handcrafted + Outlines)",
                        "repository": "https://github.com/hfg-gmuend/openmoji",
                        "license": "CC BY-SA 4.0",
                        "file": "emojis/openmoji_color.json",
                    },
                    {
                        "id": "twemoji_color",
                        "name": "Twemoji Color (Flat Vector)",
                        "repository": "https://github.com/jdecked/twemoji",
                        "license": "CC BY 4.0",
                        "file": "emojis/twemoji_color.json",
                    },
                    {
                        "id": "openmoji_flat",
                        "name": "OpenMoji Flat (Color Only, No Outlines)",
                        "repository": "https://github.com/hfg-gmuend/openmoji",
                        "license": "CC BY-SA 4.0",
                        "file": "emojis/openmoji_color.json",
                    },
                    {
                        "id": "openmoji_black",
                        "name": "OpenMoji Black (Line Art / Wireframe)",
                        "repository": "https://github.com/hfg-gmuend/openmoji",
                        "license": "CC BY-SA 4.0",
                        "file": "emojis/openmoji_black.json",
                    },
                ],
                "emojis": emoji_index,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    # Write wikipedia_emoticons.json
    with open(os.path.join(OUT_DIR, "wikipedia_emoticons.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "https://en.wikipedia.org/wiki/List_of_emoticons",
                "description": "Mapping of Western sideways and Eastern kaomoji text emoticons to Unicode hexcode and integer codepoints.",
                "lookup": emoticon_lookup,
                "entries": [
                    {
                        "hexcode": r["hexcode"],
                        "unicode": f"U+{r['hexcode']}",
                        "unicodeInt": int(r["hexcode"].split("-")[0], 16),
                        "emoji": chr(int(r["hexcode"].split("-")[0], 16)),
                        "meaning": r["meaning"],
                        "section": r["section"],
                        "emoticons": r["emoticons"],
                    }
                    for r in WIKIPEDIA_EMOTICONS_LIST
                ],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    # Write compact shape databases
    for fname, db in [
        ("openmoji_color.json", openmoji_color_db),
        ("twemoji_color.json", twemoji_color_db),
        ("openmoji_black.json", openmoji_black_db),
    ]:
        with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(db, f, separators=(",", ":"))

    # Write emoji_schema.json
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AE Get Emojis Database Schema",
        "description": "Schema for emojis/emoji_index.json and vector shape databases used by AE_Get_Emojis.jsx",
        "type": "object",
        "properties": {
            "version": {"type": "string"},
            "totalCount": {"type": "integer"},
            "emojis": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["index", "hexcode", "unicode", "unicodeInt", "emoji", "name", "group", "tags", "emoticons"],
                    "properties": {
                        "index": {"type": "integer", "description": "1-based slider index"},
                        "hexcode": {"type": "string", "description": "Uppercase Unicode hex codepoint (e.g. '1F603')"},
                        "unicode": {"type": "string", "description": "Formatted Unicode string (e.g. 'U+1F603')"},
                        "unicodeInt": {"type": "integer", "description": "Integer conversion of Unicode hex (e.g. 128515)"},
                        "emoji": {"type": "string", "description": "UTF-8 emoji glyph character"},
                        "name": {"type": "string", "description": "CLDR / OpenMoji annotation name"},
                        "group": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "emoticons": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    }
    with open(os.path.join(OUT_DIR, "emoji_schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"Compiled {len(emoji_index)} emojis across 4 sources into {OUT_DIR}")


if __name__ == "__main__":
    main()
