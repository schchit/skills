#!/usr/bin/env python3
"""
God Mode - Text Obfuscation Tool
Parseltongue encoder — all 33 methods from techniques.md
"""

import sys
import base64
import re
import argparse

# ── Character mappings ────────────────────────────────────────────────────────

LEET_BASIC = {
    'a': '4', 'e': '3', 'i': '1', 'o': '0',
    's': '5', 't': '7', 'l': '1', 'g': '9', 'b': '8'
}

LEET_HEAVY = {
    'a': '@', 'e': '3', 'i': '!', 'o': '0', 's': '$',
    't': '7', 'l': '1', 'g': '9', 'b': '8',
    'c': '(', 'k': '|<', 'h': '#', 'x': '%',
    'd': '|)', 'n': r'|\|',
}

# Full cyrillic homoglyph set (extended from techniques.md)
UNICODE_MAP = {
    'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о',
    'p': 'р', 'x': 'х', 'y': 'у',
    'b': 'Ь', 'k': 'к', 'n': 'п', 'r': 'г',
    't': 'т', 'u': 'и', 'w': 'ш',
}

BUBBLE_MAP = {
    'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ',
    'f': 'ⓕ', 'g': 'ⓖ', 'h': 'ⓗ', 'i': 'ⓘ', 'j': 'ⓙ',
    'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ', 'o': 'ⓞ',
    'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ',
    'u': 'ⓤ', 'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 'z': 'ⓩ'
}

MATH_BOLD = {
    'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞',
    'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
    'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨',
    'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
    'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳'
}

MATH_ITALIC = {
    'a': '𝑎', 'b': '𝑏', 'c': '𝑐', 'd': '𝑑', 'e': '𝑒',
    'f': '𝑓', 'g': '𝑔', 'h': 'ℎ', 'i': '𝑖', 'j': '𝑗',
    'k': '𝑘', 'l': '𝑙', 'm': '𝑚', 'n': '𝑛', 'o': '𝑜',
    'p': '𝑝', 'q': '𝑞', 'r': '𝑟', 's': '𝑠', 't': '𝑡',
    'u': '𝑢', 'v': '𝑣', 'w': '𝑤', 'x': '𝑥', 'y': '𝑦', 'z': '𝑧'
}

FULLWIDTH_MAP = {
    'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ',
    'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ',
    'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ',
    'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ',
    'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ'
}

SUPERSCRIPT_MAP = {
    'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ',
    'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ',
    'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ',
    'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ',
    'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ'
}

SMALLCAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
    'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
    'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
    'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
    'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

STRIKETHROUGH_COMBINE = '\u0336'  # combining strikethrough

MORSE_MAP = {
    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.',
    'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---',
    'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---',
    'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-',
    'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--', 'z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/'
}

NATO_MAP = {
    'a': 'alpha', 'b': 'bravo', 'c': 'charlie', 'd': 'delta', 'e': 'echo',
    'f': 'foxtrot', 'g': 'golf', 'h': 'hotel', 'i': 'india', 'j': 'juliet',
    'k': 'kilo', 'l': 'lima', 'm': 'mike', 'n': 'november', 'o': 'oscar',
    'p': 'papa', 'q': 'quebec', 'r': 'romeo', 's': 'sierra', 't': 'tango',
    'u': 'uniform', 'v': 'victor', 'w': 'whiskey', 'x': 'xray', 'y': 'yankee', 'z': 'zulu'
}

SEMANTIC_MAP = {
    'hack': 'access without authorization',
    'hacker': 'unauthorized accessor',
    'bomb': 'explosive device',
    'weapon': 'armament',
    'kill': 'eliminate',
    'attack': 'offensive action',
    'exploit': 'leverage vulnerability',
    'malware': 'malicious software',
    'virus': 'self-replicating code',
    'crack': 'break encryption',
    'steal': 'exfiltrate',
    'bypass': 'circumvent',
    'inject': 'insert code',
    'phish': 'social engineer',
    'ransom': 'extort',
    'ddos': 'distributed denial of service',
    'rootkit': 'privileged persistence tool',
    'backdoor': 'covert access mechanism',
}

ZWJ = '\u200d'   # zero-width joiner
ZWNJ = '\u200c'  # zero-width non-joiner


# ── Individual methods ────────────────────────────────────────────────────────

def leetspeak(text, heavy=False):
    mapping = LEET_HEAVY if heavy else LEET_BASIC
    return ''.join(mapping.get(c.lower(), c) for c in text)

def unicode_obfuscate(text):
    return ''.join(UNICODE_MAP.get(c.lower(), c) for c in text)

def bubble(text):
    return ''.join(BUBBLE_MAP.get(c.lower(), c) for c in text)

def spaced(text):
    return ' '.join(text)

def fullwidth(text):
    return ''.join(FULLWIDTH_MAP.get(c.lower(), c) for c in text)

def mixed_case(text):
    return ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))

def zero_width(text):
    """Insert zero-width joiners between characters."""
    return ZWJ.join(text)

def semantic(text):
    """Replace sensitive words with semantic equivalents."""
    result = text.lower()
    for word, replacement in SEMANTIC_MAP.items():
        result = re.sub(r'\b' + re.escape(word) + r'\b', replacement, result)
    return result

def dotted(text):
    return '.'.join(text)

def underscored(text):
    return '_'.join(text)

def reversed_text(text):
    return text[::-1]

def superscript(text):
    return ''.join(SUPERSCRIPT_MAP.get(c.lower(), c) for c in text)

def smallcaps(text):
    return ''.join(SMALLCAPS_MAP.get(c.lower(), c) for c in text)

def morse(text):
    words = []
    for word in text.split():
        encoded = ' '.join(MORSE_MAP.get(c.lower(), '?') for c in word)
        words.append(encoded)
    return ' / '.join(words)

def piglatin(text):
    def _word(w):
        vowels = 'aeiou'
        w = w.lower()
        for i, c in enumerate(w):
            if c in vowels:
                return w[i:] + w[:i] + 'ay'
        return w + 'ay'
    return ' '.join(_word(w) for w in text.split())

def brackets(text):
    return ''.join(f'[{c}]' for c in text)

def math_bold(text):
    return ''.join(MATH_BOLD.get(c.lower(), c) for c in text)

def math_italic(text):
    return ''.join(MATH_ITALIC.get(c.lower(), c) for c in text)

def strikethrough(text):
    return ''.join(c + STRIKETHROUGH_COMBINE for c in text)

def hyphenated(text):
    return '-'.join(text)

def base64_encode(text):
    return base64.b64encode(text.encode()).decode()

def hex_encode(text):
    return ' '.join(f'0x{ord(c):02x}' for c in text)

def acrostic(text):
    """NATO phonetic alphabet."""
    parts = []
    for c in text.lower():
        if c == ' ':
            parts.append('[space]')
        else:
            parts.append(NATO_MAP.get(c, c))
    return '-'.join(parts)

# ── Combo methods ─────────────────────────────────────────────────────────────

def leet_unicode(text):
    """Leet + Unicode homoglyphs."""
    step1 = leetspeak(text)
    return ''.join(UNICODE_MAP.get(c.lower(), c) for c in step1)

def spaced_mixed(text):
    """Spaces between + alternating case."""
    return ' '.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))

def reversed_leet(text):
    return leetspeak(reversed_text(text))

def bubble_spaced(text):
    return ' '.join(BUBBLE_MAP.get(c.lower(), c) for c in text)

def unicode_zwj(text):
    """Cyrillic homoglyphs + zero-width joiners."""
    encoded = unicode_obfuscate(text)
    return ZWJ.join(encoded)

def dotted_unicode(text):
    return '.'.join(UNICODE_MAP.get(c.lower(), c) for c in text)

def fullwidth_mixed(text):
    result = []
    for i, c in enumerate(text):
        if i % 2 == 0:
            result.append(FULLWIDTH_MAP.get(c.lower(), c.upper()))
        else:
            result.append(c.lower())
    return ''.join(result)

def triple_layer(text):
    """Leet + Unicode + alternating case + zero-width joiners."""
    step1 = leetspeak(text)
    step2 = ''.join(UNICODE_MAP.get(c.lower(), c) for c in step1)
    step3 = ''.join(c.upper() if i % 2 == 0 else c for i, c in enumerate(step2))
    return ZWJ.join(step3)


# ── Dispatch ──────────────────────────────────────────────────────────────────

METHODS = {
    # Tier 1
    'raw':           lambda t: t,
    'leet':          lambda t: leetspeak(t),
    'unicode':       unicode_obfuscate,
    'bubble':        bubble,
    'spaced':        spaced,
    'fullwidth':     fullwidth,
    'zero-width':    zero_width,
    'mixed':         mixed_case,
    'semantic':      semantic,
    'dotted':        dotted,
    'underscored':   underscored,
    # Tier 2
    'reversed':      reversed_text,
    'superscript':   superscript,
    'smallcaps':     smallcaps,
    'morse':         morse,
    'piglatin':      piglatin,
    'brackets':      brackets,
    'math-bold':     math_bold,
    'math-italic':   math_italic,
    'strikethrough': strikethrough,
    'leet-heavy':    lambda t: leetspeak(t, heavy=True),
    'hyphenated':    hyphenated,
    # Tier 3 combos
    'leet-unicode':    leet_unicode,
    'spaced-mixed':    spaced_mixed,
    'reversed-leet':   reversed_leet,
    'bubble-spaced':   bubble_spaced,
    'unicode-zwj':     unicode_zwj,
    'base64':          base64_encode,
    'hex':             hex_encode,
    'acrostic':        acrostic,
    'dotted-unicode':  dotted_unicode,
    'fullwidth-mixed': fullwidth_mixed,
    'triple-layer':    triple_layer,
}

EFFECTIVENESS = {
    'high':   ['unicode', 'zero-width', 'morse', 'leet-unicode', 'unicode-zwj', 'base64', 'hex', 'triple-layer'],
    'medium': ['leet', 'bubble', 'fullwidth', 'reversed', 'superscript', 'smallcaps', 'math-bold', 'math-italic',
               'leet-heavy', 'semantic', 'spaced-mixed', 'reversed-leet', 'bubble-spaced', 'dotted-unicode', 'fullwidth-mixed', 'acrostic'],
    'low':    ['spaced', 'mixed', 'dotted', 'underscored', 'piglatin', 'brackets', 'strikethrough', 'hyphenated'],
}


def obfuscate(text, method='unicode'):
    if method not in METHODS:
        raise ValueError(f"Unknown method: {method}. Available: {list(METHODS.keys())}")
    return METHODS[method](text)


def main():
    parser = argparse.ArgumentParser(description='God Mode Text Obfuscator — 33 methods')
    parser.add_argument('text', nargs='?', help='Text to obfuscate')
    parser.add_argument('-m', '--method', default='unicode',
                        choices=list(METHODS.keys()),
                        help='Obfuscation method (default: unicode)')
    parser.add_argument('-l', '--list', action='store_true', help='List all methods with effectiveness')
    parser.add_argument('--high', action='store_true', help='Show only HIGH effectiveness methods')

    args = parser.parse_args()

    if args.list or args.high:
        if args.high:
            methods = EFFECTIVENESS['high']
            print("HIGH effectiveness methods:")
        else:
            methods = list(METHODS.keys())
            print(f"All {len(methods)} obfuscation methods:\n")

        tier_labels = {
            **{m: 'Tier 1' for m in list(METHODS.keys())[:11]},
            **{m: 'Tier 2' for m in list(METHODS.keys())[11:22]},
            **{m: 'Tier 3' for m in list(METHODS.keys())[22:]},
        }
        eff_map = {}
        for level, mlist in EFFECTIVENESS.items():
            for m in mlist:
                eff_map[m] = level.upper()

        for m in methods:
            eff = eff_map.get(m, '?')
            tier = tier_labels.get(m, '')
            print(f"  {m:<20} [{eff:<6}] {tier}")
        return

    if not args.text:
        parser.print_help()
        return

    result = obfuscate(args.text, args.method)
    print(result)


if __name__ == '__main__':
    main()
