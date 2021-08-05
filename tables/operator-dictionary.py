#!/usr/bin/env python3

from lxml import etree
from download import downloadUnicodeXML
from math import ceil

import operator
import json

# Retrieve the unicode.xml file if necessary.
unicodeXML = downloadUnicodeXML()

defaultSpacing = 5 # 0.2777777777777778em

def parseHexaNumber(string):
    return int("0x%s" % string, 16)

def parseHexaSequence(string):
    return tuple(map(parseHexaNumber, string[1:].split("-")))

def parseSpaces(value, entry, names):
    for name in names:
        value[name] = defaultSpacing
        attributeValue = entry.get(name)
        if attributeValue is not None:
            value[name] = int(attributeValue)

def parseProperties(value, entry, names):
    attributeValue = entry.get("properties")
    if attributeValue is not None:
        if ("properties" not in value):
            value["properties"] = {}
        for name in names:
            if attributeValue.find(name) >= 0:
                value["properties"][name] = True

def serializeString(characters):
    string = ""
    for c in characters:
        string += chr(c)
    return string

def buildKey(characters, form):
    # Concatenate characters and form to build the key.
    key = serializeString(characters)
    key += " " + form
    return key

def toHexa(character):
    return "U+%04X" % character

def appendCharacters(name, character, value):
    if value:
        if "value" not in knownTables[name]:
            knownTables[name]["value"] = value
        assert knownTables[name]["value"] == value

    assert len(characters) in [1, 2]

    if len(characters) > 1:
        if "multipleChar" not in knownTables[name]:
            knownTables[name]["multipleChar"] = []
        knownTables[name]["multipleChar"].append(characters)
        if (characters not in multipleCharTable):
            multipleCharTable.append(characters)
        return

    if "singleChar" not in knownTables[name]:
        knownTables[name]["singleChar"] = []
    if (characters[0] not in knownTables[name]["singleChar"]):
        knownTables[name]["singleChar"].append(characters[0])

def dumpKnownTables(fenceAndSeparators):
    for name, item in sorted(knownTables.items(),
                             key=(lambda v: len(v[1]["singleChar"])),
                             reverse=True):
        if ((name in ["fence", "separator"]) != fenceAndSeparators):
            continue
        print(name)

        table = item["singleChar"]
        print("  singleChar (%d): " % len(table), end="")
        for unicodeRange in toRanges(table):
            print("%s, " % stringifyRange(unicodeRange), end="")

        if "multipleChar" in item:
            table = item["multipleChar"]
            print("  multipleChar (%d): " % len(table), end="")
            for sequence in sorted(table):
                print("'%s' " % serializeString(sequence), end="")
            print("")

        print("")

def stringifyRange(unicodeRange):
    if unicodeRange[0] == unicodeRange[1]:
        return "{%s}" % toHexa(unicodeRange[0])
    else:
        return "[%s–%s]" % (toHexa(unicodeRange[0]), toHexa(unicodeRange[1]))

def toRanges(operators, max_range_length = 256):
    current_range = None
    ranges = []

    for character in operators:
        if not current_range:
            current_range = character, character
        else:
            if (current_range[1] + 1 - current_range[0] < max_range_length and
                current_range[1] + 1 == character):
                current_range = current_range[0], character
            else:
                ranges.append(current_range)
                current_range = character, character

    if current_range:
        ranges.append(current_range)

    return ranges

def printCodePointStats():
    ranges=[(0x0000, 0x1FFF), (0x2000, 0x2FFF)]
    minmax=[]
    for r in ranges:
        minmax.append([r[1], r[0]])

    for name in knownTables:
        for entry in knownTables[name]["singleChar"]:
            for index, r in enumerate(ranges):
                if r[0] <= entry and entry <= r[1]:
                    minmax[index][0] = min(minmax[index][0], entry)
                    minmax[index][1] = max(minmax[index][1], entry)

    print("Code points are in the following intervals:")
    s = 0
    for r in minmax:
        print("  [%s–%s] (length 0x%04X)" % (toHexa(r[0]), toHexa(r[1]), r[1] - r[0] + 1))
        s += r[1] - r[0] + 1

    print("Total: 0x%04X different code points\n" % s)

def printRangeStats():
    print("The max of codePointEnd - codePointStart for ranges are ")
    maxDeltaTotal = 0
    for name in knownTables:
        maxDelta = 0
        for unicodeRange in toRanges(knownTables[name]["singleChar"]):
            maxDelta = max(maxDelta, unicodeRange[1] - unicodeRange[0])
        print(maxDelta, end=" ")
        maxDeltaTotal = max(maxDeltaTotal, maxDelta)

    print("(maximum is 0x%04X)" % maxDeltaTotal)
    print()

# Extract the operator dictionary.
xsltTransform = etree.XSLT(etree.parse("./operator-dictionary.xsl"))

root = xsltTransform(etree.parse(unicodeXML)).getroot()
otherEntriesWithMultipleCharacters={}
knownTables = {
    "infixEntriesWithDefaultValues": {},
    "infixEntriesWithSpacing4": {},
    "infixEntriesWithSpacing3": {},
    "infixEntriesWithSpacing5AndStretchy": {},
    "prefixEntriesWithSpacing0AndStretchySymmetric": {},
    "postfixEntriesWithSpacing0AndStretchySymmetric": {},
    "prefixEntriesWithLspace0Rspace0": {},
    "postfixEntriesWithLspace0Rspace0": {},
    "postfixEntriesWithLspace0Rspace0AndStretchy": {},
    "prefixEntriesWithLspace3Rspace3AndSymmetricLargeop": {},
    "prefixEntriesWithLspace3Rspace3AndSymmetricMovablelimitsLargeop": {},
    "infixEntriesWithLspace0Rspace0": {},
    "infixEntriesWithLspace0Rspace3": {},
    "prefixEntriesWithLspace3Rspace0": {},
    "fence": {},
    "separator": {},
}
multipleCharTable = []
otherEntries={}
otherValuesCount={}
otherValueTotalCount=0

for entry in root:
    unicodeText = entry.get("unicode")
    characters = parseHexaSequence(unicodeText)

    form = entry.get("form")
    key = buildKey(characters, form)
    value = {"form": form}
    parseSpaces(value, entry, ["lspace", "rspace"])
    parseProperties(value, entry, ["stretchy",
                                   "symmetric",
                                   "largeop",
                                   "movablelimits",
                                   "fence",
                                   "separator"])

    if "properties" in value:
        # Use a separate tables for fence and separators as they are not needed
        # for rendering.
        if ("fence" in value["properties"]):
            appendCharacters("fence", characters, None)
            del value["properties"]["fence"]
        if ("separator" in value["properties"]):
            appendCharacters("separator", characters, None)
            del value["properties"]["separator"]
        if (value["properties"] == {}):
            del value["properties"]

    if (value["lspace"] == defaultSpacing and
        value["rspace"] == defaultSpacing and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithDefaultValues", characters, value)
        continue

    if (value["lspace"] == 4 and
        value["rspace"] == 4 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing4", characters, value)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing3", characters, value)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'stretchy': True} and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing5AndStretchy", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithSpacing0AndStretchySymmetric", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True} and
        form == "postfix"):
        appendCharacters("postfixEntriesWithSpacing0AndStretchySymmetric", characters, value)
        continue

    if (value["lspace"] == 1 and
        value["rspace"] == 2 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace1Rspace2AndSymmetricLargeop", characters, value)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'movablelimits': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace3Rspace3AndSymmetricMovablelimitsLargeop", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 1 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace0Rspace1AndSymmetricLargeop", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace0Rspace0", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "postfix"):
        appendCharacters("postfixEntriesWithLspace0Rspace0", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'stretchy': True} and
        form == "postfix"):
        appendCharacters("postfixEntriesWithLspace0Rspace0AndStretchy", characters, value)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace3Rspace3AndSymmetricLargeop", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithLspace0Rspace0", characters, value)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 3 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithLspace0Rspace3", characters, value)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace3Rspace0", characters, value)
        continue

    if len(characters) > 1:
        otherEntriesWithMultipleCharacters[key] = value
        continue
    character = characters[0]

    v = str(value)
    if v not in otherValuesCount:
        otherValuesCount[v] = 0
        otherEntries[v] = []

    otherValuesCount[v] += 1
    otherValueTotalCount += 1
    otherEntries[v].append(character)

multipleCharTable.sort()

singleCharCount = otherValueTotalCount
for name in knownTables:
    singleCharCount += len(knownTables[name]["singleChar"])
multipleCharCount = (len(multipleCharTable) +
                     len(otherEntriesWithMultipleCharacters))
print("Dictionary size: %d" % (singleCharCount + multipleCharCount))
print("  single char: %d" % singleCharCount)
print("  multiple char: %d" % multipleCharCount)
print("")

dumpKnownTables(False)

print("otherEntries", otherValueTotalCount)
for value, count in sorted(otherValuesCount.items(),
                           key=operator.itemgetter(1), reverse=True):
   print("  * %s: %d" % (value, count))
   print("    [", end="")
   for entry in otherEntries[value]:
       print(toHexa(entry), end=", ")
   print("]")
   print("")

print("otherEntriesWithMultipleCharacters",
      len(otherEntriesWithMultipleCharacters))
for name in otherEntriesWithMultipleCharacters:
   print("  * %s: %s" % (name, str(otherEntriesWithMultipleCharacters[name])))
print("")

print("Other tables:\n")
dumpKnownTables(True)

print("multiple char (%d): " % len(multipleCharTable), end="")
for sequence in sorted(multipleCharTable):
    print("'%s' " % serializeString(sequence), end="")
print("\n")

################################################################################
def serializeValue(value, fence, separator):
    properties = ""
    if "properties" in value:
        for p in ["stretchy", "symmetric", "largeop", "movablelimits"]:
            if p in value["properties"]:
                properties += "%s " % p
    if fence:
        properties += "fence "
    if separator:
        properties += "separator "
    if properties == "":
        properties = "N/A"

    spaces = ["0",
              "0.05555555555555555em",
              "0.1111111111111111em",
              "0.16666666666666666em",
              "0.2222222222222222em",
              "0.2777777777777778em",
              "0.3333333333333333em",
              "0.3888888888888889em"]

    return "<td><code>%s</code></td><td><code>%s</code></td><td>%s</td>" % (
        spaces[value["lspace"]],
        spaces[value["rspace"]],
        properties)

totalEntryCount = 0
print("Generate operator-dictionary.html...", end=" ");
md = open("operator-dictionary.html", "w")
md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");

md.write('<figure id="operator-dictionary-table">')
md.write("<table class='sortable'>\n");
md.write("<tr><th>Content</th><th>form</th><th>rspace</th><th>lspace</th><th>properties</th></tr>\n")
for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if ((name in ["fence", "separator"])):
        continue
    for entry in knownTables[name]["singleChar"]:
        if entry >= 0x10000:
            md.write('<tr style="background: lightyellow;">')
        else:
            md.write("<tr>")
        md.write("<td>&#x%0X; U+%04X</td>" % (entry, entry))
        md.write("<td><code>%s</code></td>" % knownTables[name]["value"]["form"])
        md.write(serializeValue(knownTables[name]["value"],
                                entry in knownTables["fence"]["singleChar"],
                                entry in knownTables["separator"]["singleChar"]))
        totalEntryCount += 1
        md.write("</tr>\n");
    if "multipleChar" in knownTables[name]:
        for entry in knownTables[name]["multipleChar"]:
            md.write("<tr style='background: lightblue'>");
            md.write("<td>String ")
            md.write(serializeString(entry))
            for character in entry:
                md.write(" U+%04X" % character)
            md.write("</td>")
            md.write("<td><code>%s</code></td>" % knownTables[name]["value"]["form"])
            fence = "multipleChar" in knownTables["fence"] and entry in knownTables["fence"]["multipleChar"]
            separator = "multipleChar" in knownTables["separator"] and entry in knownTables["separator"]["multipleChar"]
            md.write(serializeValue(knownTables[name]["value"],
                                    fence,
                                    separator))
            totalEntryCount += 1
            md.write("</tr>\n");

# FIXME: decide what to do with these values.
# Ugly hack for now, hopefully these edge cases will be handled normally later or removed.
for value, count in sorted(otherValuesCount.items(),
                           key=operator.itemgetter(1), reverse=True):
    for entry in otherEntries[value]:
        parsed_value = json.loads(value.replace("'", '"').replace("True", '"True"'))
        md.write("<tr style='text-decoration: line-through;'>");
        md.write("<td>&#x%0X; U+%04X</td>" % (entry, entry))
        md.write("<td><code>%s</code></td>" % parsed_value["form"])
        md.write(serializeValue(parsed_value,
                                "properties" in parsed_value and "fence" in parsed_value["properties"],
                                "properties" in parsed_value and "separator" in parsed_value["properties"]))
        md.write("</tr>\n");
for name in otherEntriesWithMultipleCharacters:
    md.write("<tr style='text-decoration: line-through; background: lightblue'>");
    md.write("<td>String ")
    md.write(name)
    md.write("</td>")
    md.write("<td><code>%s</code></td>" % otherEntriesWithMultipleCharacters[name]["form"])
    md.write(serializeValue(otherEntriesWithMultipleCharacters[name], False, False))
    md.write("</tr>\n");

md.write("</table>\n");
md.write('<figcaption>Mapping from operator (Content, Form) to properties.<br/>Total size: %d entries, ≥ %d bytes<br/>(assuming \'Content\' uses at least one UTF-16 character, \'Form\' 2 bits, spacing 3 bits and properties 3 bits).</figcaption>' % (totalEntryCount, ceil(totalEntryCount * (16 + 2 + 3 + 3)/8.)))
md.write('</figure>')
print("done.");
################################################################################

# Delete infix operators using default values.
del knownTables["infixEntriesWithDefaultValues"]

# Convert nonBMP characters to surrogates pair (multiChar)
# Not used anymore, but keep it in case that changes in the future...
def convertToSurrogatePairs():
    for name in knownTables:
        for entry in knownTables[name]["singleChar"]:
            if entry >= 0x10000:
                if "multipleChar" not in knownTables[name]:
                    knownTables[name]["multipleChar"] = []
                high_surrogate = ((entry - 0x10000) // 0x400) + 0xD800
                low_surrogate = ((entry - 0x10000) & (0x400 - 1)) + 0xDC00
                characters = (high_surrogate, low_surrogate)
                knownTables[name]["multipleChar"].append(characters)
                if characters not in multipleCharTable:
                    multipleCharTable.append(characters)

        for entry in knownTables[name]["singleChar"]:
            knownTables[name]["singleChar"] = [ entry for entry in knownTables[name]["singleChar"] if entry < 0x10000 ]

    multipleCharTable.sort()
    for name in knownTables:
        if "multipleChar" in knownTables[name]:
            knownTables[name]["multipleChar"].sort()
        knownTables[name]["singleChar"].sort()

# Remove non-BMP characters. (Arabic Operators and supplemental arrows-C
knownNonBMP = [0x1EEF0, 0x1EEF1]
for name in knownTables:
    for entry in knownTables[name]["singleChar"]:
        assert entry < 0x10000 or entry in knownNonBMP or (entry >=0x1F800 and entry < 0x1F900)
    knownTables[name]["singleChar"] = [ entry for entry in knownTables[name]["singleChar"] if entry < 0x10000 ]

# Convert multiChar to singleChar
reservedBlock = (0x0320, 0x03FF)
for name in knownTables:
    if "multipleChar" in knownTables[name]:
        for entry in knownTables[name]["multipleChar"]:
            codePoint = reservedBlock[0] + multipleCharTable.index(entry);
            assert codePoint <= reservedBlock[1]
            if codePoint not in knownTables[name]["singleChar"]:
                knownTables[name]["singleChar"].append(codePoint)

for name in knownTables:
    knownTables[name]["singleChar"].sort()

# Print more statistics
print()
printCodePointStats()
printRangeStats()

# Print the compact dictionary
print("Generate operator-dictionary-compact.html...", end=" ");
md = open("operator-dictionary-compact.html", "w")
md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");

totalEntryCount = 0
totalBytes = 0
md.write('<figure id="operator-dictionary-compact-special-tables">')
md.write("<table>");
md.write("<tr>");
md.write("<th>Special Table</th><th>Entries</th>");
md.write("</tr>\n");
md.write("<tr>")
md.write("<td><code>Operators_2_ascii_chars</code></td>");
md.write("<td>%d entries (2-characters ASCII strings): <code>" % len(multipleCharTable));
for sequence in multipleCharTable:
    assert len(sequence) == 2
    md.write("'%s%s', " % (chr(sequence[0]), chr(sequence[1])))
    totalBytes += 2
    totalEntryCount += 1
md.write("</code></td>");
md.write("</tr>\n")

for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if name not in ["fence", "separator"]:
        continue
    count = len(knownTables[name]["singleChar"])
    md.write("<tr>")
    md.write("<td><code>Operators_%s</code></td>" % name);
    ranges = toRanges(knownTables[name]["singleChar"])
    if (3 * len(ranges) < 2 * count):
        md.write("<td>%d entries (%d Unicode ranges): <code>" % (count, len(ranges)))
        for entry in ranges:
            md.write("%s, " % stringifyRange(entry))
        totalBytes += 3 * len(ranges)
    else:
        md.write("<td>%d entries: <code>" % count)
        for entry in knownTables[name]["singleChar"]:
            md.write("U+%04X, " % entry)
        totalBytes += 2 * count
    totalEntryCount += count
    md.write("</code></td>")
    md.write("</tr>\n")
md.write("</table>");
md.write('<figcaption>Special tables for the operator dictionary.<br/>Total size: %d entries, %d bytes.<br/>(assuming characters are UTF-16 and 1-byte range lengths)</figcaption>' % (totalEntryCount, totalBytes))
md.write('</figure>')

totalEntryCount = 0
totalBytes = 0
value_index = 0
md.write('<figure id="operator-dictionary-category-table">')
md.write("<table>");
md.write("<tr><th>(Content, Form) keys</th><th>Category</th></tr>\n");

for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if name in ["fence", "separator"]:
        continue
    count = len(knownTables[name]["singleChar"])
    md.write("<tr>")
    totalEntryCount += count

    ranges = toRanges(knownTables[name]["singleChar"])
    if (3 * len(ranges) < 2 * count):
        md.write("<td>%d entries (%d Unicode ranges)  in <strong>%s</strong> form: <code>" % (count, len(ranges), knownTables[name]["value"]["form"]))
        for entry in ranges:
            md.write("%s, " % stringifyRange(entry))
        totalBytes += 3 * len(ranges)
    else:
        md.write("<td>%d entries in <strong>%s</strong> form: <code>" % (count, knownTables[name]["value"]["form"]))
        for entry in knownTables[name]["singleChar"]:
            md.write("U+%04X, " % entry)
        totalBytes += 2 * count
    md.write("</code></td>")
    md.write("<td>%s</td>" % chr(ord('A') + value_index));
    value_index += 1;
    md.write("</tr>\n")
md.write("</table>");
md.write('<figcaption>Mapping from operator (Content, Form) to a category.<br/>Total size: %d entries, %d bytes.<br/>(assuming characters are UTF-16 and 1-byte range lengths)</figcaption>' % (totalEntryCount, totalBytes))
md.write('</figure>')

def formValueFromString(value):
    form = knownTables[name]["value"]["form"]
    if form == "infix":
        return 0
    if form == "prefix":
        return 1
    assert form == "postfix"
    return 2

category_for_form = [0, 0, 0]
value_index = 0
md.write('<figure id="operator-dictionary-categories-values">')
md.write("<table>");
md.write("<tr><th>Category</th><th>Form</th><th>Encoding</th><th>rspace</th><th>lspace</th><th>properties</th></tr>\n")
for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if ((name in ["fence", "separator"])):
        continue
    for entry in knownTables[name]["singleChar"]:
        md.write("<tr>");
        md.write("<td>%s</td>" % chr(ord('A') + value_index))
        md.write("<td>%s</td>" % knownTables[name]["value"]["form"]);
        form = formValueFromString(knownTables[name]["singleChar"])
        if category_for_form[form] >= 4:
            md.write("<td>N/A</td>")
        else:
            hexa = form + (category_for_form[form] << 2)
            category_for_form[form] += 1
            md.write("<td>0x%01X</td>" % hexa)
        md.write(serializeValue(knownTables[name]["value"], False, False))
        md.write("</tr>\n");
        break
    value_index += 1

md.write("</table>");
md.write('<figcaption>Operators values for each category.<br/>The third column provides a 4bits encoding of the categories<br/>where the 2 least significant bits encodes the form infix (0), prefix (1) and postfix (2).</figcaption>')
md.write('</figure>')

print("done.");

# Calculate compact form for the largest categories.
compact_table = []
category_for_form = [0, 0, 0]
totalEntryCount = 0
for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if name in ["fence", "separator"]:
        continue
    count = len(knownTables[name]["singleChar"])
    form = formValueFromString(knownTables[name]["singleChar"])
    if category_for_form[form] >= 4:
        continue
    totalEntryCount += count
    hexa = form + (category_for_form[form] << 2)
    category_for_form[form] += 1

    for entry in knownTables[name]["singleChar"]:
        assert entry <= 0x3FF or (0x2000 <= entry and entry <= 0x2BFF)
        if 0x2000 <= entry and entry <= 0x2BFF:
            entry = entry - 0x1C00
        entry = entry + (hexa << 12)
        compact_table.append(entry)

def cmp_key(x):
    return x & 0x3FFF
compact_table.sort(key=cmp_key)

bits_per_range = 4
compact_table = toRanges(compact_table, 1 << bits_per_range)
rangeCount = 0

md.write('<figure id="operator-dictionary-categories-hexa-table">')
md.write('%d entries (%d ranges of length at most %d): <code>' % (totalEntryCount, len(compact_table), 1 << bits_per_range));
for r in compact_table:
    if r[0] == r[1]:
        md.write('{0x%04X}, ' % r[0])
    else:
        md.write('[0x%04X–0x%04X], ' % (r[0], r[1]))
    rangeCount += 1

md.write('</code>');
md.write('<figcaption>List of entries for the largest categories, sorted by key.<br/><code>Key</code> is <code>Entry</code> %% 0x4000, category encoding is <code>Entry</code> / 0x1000.<br/>Total size: %d entries, %d bytes<br/>(assuming %d bits for range lengths).</figcaption>' % (totalEntryCount, ceil((16+bits_per_range) * rangeCount / 8.), bits_per_range))
md.write('</figure>')

# Dump compact dictionary for C++-like table.
#for r in compact_table:
#    print('{0x%04X, %d}, ' % (r[0], r[1] - r[0]), end="")
#print()
