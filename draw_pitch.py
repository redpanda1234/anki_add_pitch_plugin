import sys


def hira_to_mora(hira):
    """Example:
    in:  'しゅんかしゅうとう'
    out: ['しゅ', 'ん', 'か', 'しゅ', 'う', 'と', 'う']
    """

    mora_arr = []
    combiners = [
        "ゃ",
        "ゅ",
        "ょ",
        "ぁ",
        "ぃ",
        "ぅ",
        "ぇ",
        "ぉ",
        "ャ",
        "ュ",
        "ョ",
        "ァ",
        "ィ",
        "ゥ",
        "ェ",
        "ォ",
    ]

    i = 0
    while i < len(hira):
        if i + 1 < len(hira) and hira[i + 1] in combiners:
            mora_arr.append("{}{}".format(hira[i], hira[i + 1]))
            i += 2
        else:
            mora_arr.append(hira[i])
            i += 1
    return mora_arr


def circle(x, y, devoiced=False, o=False):
    if not devoiced:
        r = ('<circle r="5" cx="{}" cy="{}" style="opacity:1;fill:#000;" />').format(
            x, y
        )

        if o:
            r += (
                '<circle r="3.25" cx="{}" cy="{}" style="opacity:1;fill:#fff;"' "/>"
            ).format(x, y)
    else:
        assert not o
        r = (
            '<circle r="5" cx="{}" cy="{}" stroke="black" stroke-dasharray="2" style="opacity:1;fill:#EBEBEB;" />'
        ).format(x, y)
    return r


def text(x, mora, devoiced=False):
    # letter positioning tested with Noto Sans CJK JP
    color = "#000"
    if devoiced:
        color = "#CDCDCD"
    if len(mora) == 1:
        return (
            '<text x="{}" y="67.5" style="font-size:20px;font-family:sans-'
            "serif;fill:" + color + ';">{}</text>'
        ).format(x, mora)
    else:
        return (
            '<text x="{}" y="67.5" style="font-size:20px;font-family:sans-'
            "serif;fill:" + color + ';">{}</text><text x="{}" y="67.5" style="font-'
            "size:14px;font-family:sans-serif;fill:" + color + ';">{}</text>'
        ).format(x - 5, mora[0], x + 12, mora[1])


def path(x, y, typ, step_width):
    if typ == "s":  # straight
        delta = "{},0".format(step_width)
    elif typ == "u":  # up
        delta = "{},-25".format(step_width)
    elif typ == "d":  # down
        delta = "{},25".format(step_width)
    return (
        '<path d="m {},{} {}" style="fill:none;stroke:#000;stroke-width' ':1.5;" />'
    ).format(x, y, delta)


def pitch_svg(word, patt, silent=False):
    """Draw pitch accent patterns in SVG

    Examples:
        はし HLL (箸)
        はし LHL (橋)
        はし LHH (端)
    """

    mora = hira_to_mora(word)

    if len(patt) - len(mora) != 1 and not silent:
        print(
            ("pattern should be number of morae + 1 (got: {}, {})").format(word, patt)
        )
    positions = max(len(mora), len(patt))
    step_width = 35
    margin_lr = 16
    svg_width = max(0, ((positions - 1) * step_width) + (margin_lr * 2))

    svg = (
        '<svg class="pitch" width="{0}px" height="75px" viewBox="0 0 {0} 75' '">'
    ).format(svg_width)

    chars = ""
    for pos, mor in enumerate(mora):
        x_center = margin_lr + (pos * step_width)
        devoiced = (pos < len(patt)) and (patt[pos] in ["h", "l"])
        chars += text(x_center - 11, mor, devoiced=devoiced)

    circles = ""
    paths = ""
    for pos, accent in enumerate(patt):
        x_center = margin_lr + (pos * step_width)
        if accent in ["H", "h", "1", "2"]:
            y_center = 5
        elif accent in ["L", "l", "0"]:
            y_center = 30

        devoiced = (pos < len(mora)) and (accent in ["h", "l"])

        circles += circle(x_center, y_center, devoiced=devoiced, o=pos >= len(mora))
        if pos > 0:
            if prev_center[1] == y_center:
                path_typ = "s"
            elif prev_center[1] < y_center:
                path_typ = "d"
            elif prev_center[1] > y_center:
                path_typ = "u"
            paths += path(prev_center[0], prev_center[1], path_typ, step_width)
        prev_center = (x_center, y_center)

        # Don't bother drawing more than one trailing pitch guide
        if pos >= len(mora):
            break

    svg += chars
    svg += paths
    svg += circles
    svg += "</svg>"

    return svg


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 draw_pitch.py <word> <patt>")
        sys.exit()
    print(pitch_svg(sys.argv[1], sys.argv[2], silent=True))
