#!/usr/bin/python3

from lxml import etree
from download import downloadUnicodeXML

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

    if len(characters) > 1:
        if "multipleChar" not in knownTables[name]:
            knownTables[name]["multipleChar"] = []
        knownTables[name]["multipleChar"].append(characters)
        if (characters not in multipleCharTable):
            multipleCharTable.append(characters)
        return

    if "singleChar" not in knownTables[name]:
        knownTables[name]["singleChar"] = []
    knownTables[name]["singleChar"].append(characters[0])

def dumpKnownTables(fenceAndSeparators):
    for name, item in sorted(knownTables.items(),
                             key=(lambda v: len(v[1]["singleChar"])),
                             reverse=True):
        if ((name in ["fence", "separator"]) != fenceAndSeparators):
            continue
        print(name)

        table = item["singleChar"]
        print("  singleChar (%d): " % len(table), toUnicodeRanges(table))

        if "multipleChar" in item:
            table = item["multipleChar"]
            print("  multipleChar (%d): " % len(table), end="")
            for sequence in sorted(table):
                print("'%s' " % serializeString(sequence), end="")
            print("")

        print("")

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
    "prefixEntriesWithLspace1Rspace2AndSymmetricMovablelimitsLargeop": {},
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
        value["properties"] == {'symmetric': True, 'movablelimits': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace1Rspace2AndSymmetricMovablelimitsLargeop", characters, value)
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

def stringifyRange(unicodeRange):
    assert unicodeRange[1] - unicodeRange[0] < 256

    if unicodeRange[0] == unicodeRange[1]:
        return "{%s}" % toHexa(unicodeRange[0])
    else:
        return "[%s–%s]" % (toHexa(unicodeRange[0]), toHexa(unicodeRange[1]))

def toUnicodeRanges(operators):
    unicodeRange = None
    ranges = []

    for character in operators:
        if not unicodeRange:
            unicodeRange = character, character
        else:
            if unicodeRange[1] + 1 == character:
                unicodeRange = unicodeRange[0], character
            else:
                ranges.append(stringifyRange(unicodeRange))
                unicodeRange = character, character

    if unicodeRange:
        ranges.append(stringifyRange(unicodeRange))

    return ranges

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
md.write("<tr><th>Content</th><th>form</th><th>rspace</th><th>lspace</th><th>properties</th></tr>")
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
        md.write("</tr>");
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
            md.write("</tr>");

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
        md.write("</tr>");
for name in otherEntriesWithMultipleCharacters:
    md.write("<tr style='text-decoration: line-through; background: lightblue'>");
    md.write("<td>String ")
    md.write(name)
    md.write("</td>")
    md.write("<td><code>%s</code></td>" % otherEntriesWithMultipleCharacters[name]["form"])
    md.write(serializeValue(otherEntriesWithMultipleCharacters[name], False, False))
    md.write("</tr>");

md.write("</table>\n");
md.write('<figcaption>Mapping from operator (Content, Form) to properties.<br/>Total size: %d entries, ≥ %d bytes<br/>(assuming \'Content\' uses at least one UTF-16 character, \'Form\' 2 bits, spacing 3 bits and properties 3 bits).</figcaption>' % (totalEntryCount, totalEntryCount * (16 + 2 + 3 + 3)/8))
md.write('</figure>')
print("done.");
################################################################################

def nonBMPToSurrogate(character):
    return (low_surrogate, high_surrogate)

# Delete infix operators using default values.
del knownTables["infixEntriesWithDefaultValues"]

reservedBlock = (0xE000, 0xF8FF)

# Convert nonBMP characters to surrogates pair (multiChar)
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

# Convert multiChar to singleChar
for name in knownTables:
    if "multipleChar" in knownTables[name]:
        for entry in knownTables[name]["multipleChar"]:
            codePoint = reservedBlock[0] + multipleCharTable.index(entry);
            assert codePoint <= reservedBlock[1]
            if codePoint not in knownTables[name]["singleChar"]:
                knownTables[name]["singleChar"].append(codePoint)

for name in knownTables:
    knownTables[name]["singleChar"].sort()

print("Generate operator-dictionary-compact.html...", end=" ");
md = open("operator-dictionary-compact.html", "w")
md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");

md.write('<figure id="operator-dictionary-compact-special-tables">')
md.write("<table>");
md.write("<tr>");
md.write("<th>Special Table</th><th>Unicode strings/characters</th>");
md.write("</tr>");

totalBytes = 0
md.write("<tr>")
md.write("<td><code>Operators_multichar</code></td>");
md.write("<td>%d null-terminated strings: <code>" % len(multipleCharTable));
for sequence in multipleCharTable:
    md.write("{");
    for character in sequence:
        md.write("U+%04X," % character)
        totalBytes += 2
    md.write("U+0000}, ");
    totalBytes += 2
md.write("</code></td>");
md.write("</tr>")

for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if name not in ["fence", "separator"]:
        continue
    count = len(knownTables[name]["singleChar"])
    md.write("<tr>")
    md.write("<td><code>Operators_%s</code></td>" % name);
    ranges = toUnicodeRanges(knownTables[name]["singleChar"])
    if (3 * len(ranges) < 2 * count):
        md.write("<td>%d ranges (%d characters): <code>" % (len(ranges), count))
        for entry in ranges:
            md.write("%s, " % entry)
        totalBytes += 3 * len(ranges)
    else:
        md.write("<td>%d characters: <code>" % count)
        for entry in knownTables[name]["singleChar"]:
            md.write("U+%04X, " % entry)
        totalBytes += 2 * count
    md.write("</code></td>")
    md.write("</tr>")
md.write("</table>");
md.write('<figcaption>Special tables for the operator dictionary.<br/>Total size: %d bytes.<br/>(assuming characters are UTF-16 and 1-byte range lengths)</figcaption>' % totalBytes)
md.write('</figure>')

totalEntryCount = 0
totalBytes = 0
value_index = 0
md.write('<figure id="operator-dictionary-category-table">')
md.write("<table>");
md.write("<tr><th>(Content, Form) keys</th><th>Category</th></tr>");

for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if name in ["fence", "separator"]:
        continue
    count = len(knownTables[name]["singleChar"])
    md.write("<tr>")
    totalEntryCount += count

    ranges = toUnicodeRanges(knownTables[name]["singleChar"])
    if (3 * len(ranges) < 2 * count):
        md.write("<td>%d ranges (%d characters) in <strong>%s</strong> form: <code>" % (len(ranges), count, knownTables[name]["value"]["form"]))
        for entry in ranges:
            md.write("%s, " % entry)
        totalBytes += 3 * len(ranges)
    else:
        md.write("<td>%d characters in <strong>%s</strong> form: <code>" % (count, knownTables[name]["value"]["form"]))
        for entry in knownTables[name]["singleChar"]:
            md.write("U+%04X, " % entry)
        totalBytes += 2 * count
    md.write("</code></td>")
    md.write("<td>%d</td>" % value_index);
    value_index += 1;
    md.write("</tr>")
md.write("</table>");
md.write('<figcaption>Mapping from operator (Content, Form) to a category.<br/>Total size: %d entries, %d bytes.<br/>(assuming characters are UTF-16 and 1-byte range lengths)</figcaption>' % (totalEntryCount, totalBytes))
md.write('</figure>')

value_index = 0
md.write('<figure id="operator-dictionary-categories-values">')
md.write("<table>");
md.write("<tr><th>Category</th><th>rspace</th><th>lspace</th><th>properties</th></tr>")
for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if ((name in ["fence", "separator"])):
        continue
    for entry in knownTables[name]["singleChar"]:
        md.write("<tr>");
        md.write("<td>%d</td>" % value_index)
        md.write(serializeValue(knownTables[name]["value"],
                                False,
                                False))
        md.write("</tr>");
        break
    value_index += 1

md.write("</table>");
md.write('<figcaption>Operators values for each category.</figcaption>')
md.write('</figure>')

print("done.");
