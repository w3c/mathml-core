#!/usr/bin/python

from __future__ import print_function

# Base character, stretch axis, extender, bottom/left, middle, top/right
unicodeAssemblies = {
    0x0028: [True,  0x239C, 0x239D, 0x0000, 0x239B], # LEFT PARENTHESIS
    0x0029: [True,  0x239F, 0x23A0, 0x0000, 0x239E], # RIGHT PARENTHESIS,
    0x003D: [False, 0x003D, 0x003D, 0x0000, 0x0000], # = EQUALS SIGN
    0x005B: [True,  0x23A2, 0x23A3, 0x0000, 0x23A1], # LEFT SQUARE BRACKET
    0x005D: [True,  0x23A5, 0x23A6, 0x0000, 0x23A4], # RIGHT SQUARE BRACKET
    0x005F: [False, 0x005F, 0x005F, 0x0000, 0x0000], # _ LOW LINE
    0x007B: [True,  0x23AA, 0x23A9, 0x23A8, 0x23A7], # LEFT CURLY BRACKET
    0x007C: [True,  0x007C, 0x007C, 0x0000, 0x0000], # VERTICAL LINE
    0x007D: [True,  0x23AA, 0x23AD, 0x23AC, 0x23AB], # RIGHT CURLY BRACKET
    0x00AF: [False, 0x00AF, 0x00AF, 0x0000, 0x0000], # MACRON
    0x2016: [True,  0x2016, 0x2016, 0x0000, 0x0000], # DOUBLE VERTICAL LINE
    0x203E: [False, 0x203E, 0x203E, 0x0000, 0x0000], # OVERLINE
    0x2190: [False, 0x23AF, 0x2190, 0x0000, 0x23AF], # LEFTWARDS ARROW
    0x2191: [True,  0x23D0, 0x23D0, 0x0000, 0x2191], # UPWARDS ARROW
    0x2192: [False, 0x23AF, 0x23AF, 0x0000, 0x2192], # RIGHTWARDS ARROW
    0x2193: [True,  0x23D0, 0x2193, 0x0000, 0x23D0], # DOWNWARDS ARROW
    0x2194: [False, 0x23AF, 0x2190, 0x0000, 0x2192], # LEFT RIGHT ARROW
    0x2195: [True,  0x23D0, 0x2193, 0x0000, 0x2191], # UP DOWN ARROW
    0x21A4: [False, 0x23AF, 0x2190, 0x0000, 0x22A3], # LEFTWARDS ARROW FROM BAR
    0x21A6: [False, 0x23AF, 0x22A2, 0x0000, 0x2192], # RIGHTWARDS ARROW FROM BAR
    0x21BC: [False, 0x23AF, 0x21BC, 0x0000, 0x23AF], # RIGHTWARDS HARPOON WITH BARB UPWARDS
    0x21BD: [False, 0x23AF, 0x21BD, 0x0000, 0x23AF], # LEFTWARDS HARPOON WITH BARB DOWNWARDS
    0x21C0: [False, 0x23AF, 0x23AF, 0x0000, 0x21C0], # RIGHWARDS HARPOON WITH BARB UPWARDS
    0x21C1: [False, 0x23AF, 0x23AF, 0x0000, 0x21C1], # HARPOON WITH BARB DOWNWARDS
    0x2223: [True,  0x2223, 0x2223, 0x0000, 0x0000], # DIVIDES
    0x2225: [True,  0x2225, 0x2225, 0x0000, 0x0000], # PARALLEL TO
    0x2308: [True,  0x23A2, 0x23A2, 0x0000, 0x23A1], # LEFT CEILING
    0x2309: [True,  0x23A5, 0x23A5, 0x0000, 0x23A4], # RIGHT CEILING
    0x230A: [True,  0x23A2, 0x23A3, 0x0000, 0x0000], # LEFT FLOOR
    0x230B: [True,  0x23A5, 0x23A6, 0x0000, 0x0000], # RIGHT FLOOR
    0x23B0: [True,  0x23AA, 0x23AD, 0x0000, 0x23A7], # UPPER LEFT OR LOWER RIGHT CURLY BRACKET SECTION (lmoustache)
    0x23B1: [True,  0x23AA, 0x23A9, 0x0000, 0x23AB], # UPPER RIGHT OR LOWER LEFT CURLY BRACKET SECTION (rmoustache)
    0x27F5: [False, 0x23AF, 0x2190, 0x0000, 0x23AF], # LONG LEFTWARDS ARROW
    0x27F6: [False, 0x23AF, 0x23AF, 0x0000, 0x2192], # LONG RIGHTWARDS ARROW
    0x27F7: [False, 0x23AF, 0x2190, 0x0000, 0x2192], # LONG LEFT RIGHT ARROW
    0x294E: [False, 0x23AF, 0x21BC, 0x0000, 0x21C0], # LEFT BARB UP RIGHT BARB UP HARPOON
    0x2950: [False, 0x23AF, 0x21BD, 0x0000, 0x21C1], # LEFT BARB DOWN RIGHT BARB DOWN HARPOON
    0x295A: [False, 0x23AF, 0x21BC, 0x0000, 0x22A3], # LEFTWARDS HARPOON WITH BARB UP FROM BAR
    0x295B: [False, 0x23AF, 0x22A2, 0x0000, 0x21C0], # RIGHTWARDS HARPOON WITH BARB UP FROM BAR
    0x295E: [False, 0x23AF, 0x21BD, 0x0000, 0x22A3], # LEFTWARDS HARPOON WITH BARB DOWN FROM BAR
    0x295F: [False, 0x23AF, 0x22A2, 0x0000, 0x21C1], # RIGHTWARDS HARPOON WITH BARB DOWN FROM BAR
}

def stretchAxis(isVertical):
    if isVertical:
        return "Vertical"
    return "Horizontal"

def codePoint(c):
    if c == 0:
        return "N/A"
    return "U+%04X &#x%0X;" % (c, c)

print("Generate unicode-assembly.html...", end=" ")
f = open("unicode-assembly.html", "w")
f.write("\
<table class=\"sortable\">\n\
  <tr>\n\
    <th>Base Character</th>\n\
    <th>Stretch Axis</th>\n\
    <th>Extender Character</th>\n\
    <th>Bottom/Left Character</th>\n\
    <th>Middle Character</th>\n\
    <th>Top/Right Character</th>\n\
  </tr>\n\
")
for baseCharacter in sorted(unicodeAssemblies):
    assert unicodeAssemblies[baseCharacter][1] != 0
    assert unicodeAssemblies[baseCharacter][2] != 0
    f.write("\
  <tr>\n\
    <td>%s</td>\n\
    <td>%s</td>\n\
    <td>%s</td>\n\
    <td>%s</td>\n\
    <td>%s</td>\n\
    <td>%s</td>\n\
  </tr>\n\
" % (codePoint(baseCharacter),
     stretchAxis(unicodeAssemblies[baseCharacter][0]),
     codePoint(unicodeAssemblies[baseCharacter][1]),
     codePoint(unicodeAssemblies[baseCharacter][2]),
     codePoint(unicodeAssemblies[baseCharacter][3]),
     codePoint(unicodeAssemblies[baseCharacter][4])))

f.write("</table>\n")
f.close()
print("done.")
