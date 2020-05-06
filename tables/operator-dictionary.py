#!/usr/bin/python3

from lxml import etree
from download import downloadUnicodeXML

import operator
#import json, re

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
        return

    if "singleChar" not in knownTables[name]:
        knownTables[name]["singleChar"] = []
    knownTables[name]["singleChar"].append(characters[0])

def dumpKnownTables(fenceAndSeparators):
    for name, item in sorted(knownTables.items(),
                             key=(lambda v: len(v[1]["singleChar"])),
                             reverse=True):
        if ((name in ["fences", "separators"]) != fenceAndSeparators):
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
    "fences": {},
    "separators": {}
}
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
            appendCharacters("fences", characters, None)
            del value["properties"]["fence"]
        if ("separator" in value["properties"]):
            appendCharacters("separators", characters, None)
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

def stringifyRange(unicodeRange):
    if unicodeRange[0] == unicodeRange[1]:
        return toHexa(unicodeRange[0])
    else:
        return "[%s, %s]" % (toHexa(unicodeRange[0]), toHexa(unicodeRange[1]))

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

print("Separate tables for fences and separators:\n")
dumpKnownTables(True)


# Dump the HTML content
operatorProperties = ["stretchy", "symmetric", "largeop", "movablelimits"]
def serializeValue(value):
    properties = ""
    if "properties" in value:
        for p in operatorProperties:
            if p in value["properties"]:
                properties += "%s " % p
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

    return "<td><code>%s</code></td><td><code>%s</code></td><td><code>%s</code></td><td>%s</td>" % (
        value["form"],
        spaces[value["lspace"]],
        spaces[value["rspace"]],
        properties)

print("Generate operator-dictionary.html...", end=" ");
md = open("operator-dictionary.html", "w")
md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");

md.write("<ul>");
for name in ["fences", "separators"]:
    md.write("<li>%s: " % name);
    for entry in knownTables[name]["singleChar"]:
        md.write("<code>&#x%0X; U+%04X</code>, " % (entry, entry))
    if "multipleChar" in knownTables[name]:
        for entry in knownTables[name]["multipleChar"]:
            md.write("<code>")
            md.write(serializeString(entry))
            for character in entry:
                md.write(" U+%04X" % character)
            md.write("</code>, ")
    md.write("</li>");
md.write("</ul>")

md.write("<table class='sortable'>\n");
md.write("<tr>")
md.write("<th>Content</th><th>form</th><th>rspace</th><th>lspace</th>")
md.write("<th>")
for p in operatorProperties:
    md.write("%s " % p)
md.write("</th>")
md.write("</tr>")
for name, item in sorted(knownTables.items(),
                         key=(lambda v: len(v[1]["singleChar"])),
                         reverse=True):
    if ((name in ["fences", "separators", "infixEntriesWithDefaultValues"])):
        continue
    for entry in knownTables[name]["singleChar"]:
        md.write("<tr>");
        md.write("<td>&#x%0X; U+%04X</td>" % (entry, entry))
        md.write(serializeValue(knownTables[name]["value"]))
        md.write("</tr>");
    if "multipleChar" in knownTables[name]:
        for entry in knownTables[name]["multipleChar"]:
            md.write("<tr>");
            md.write("<td>")
            md.write(serializeString(entry))
            for character in entry:
                md.write(" U+%04X" % character)
            md.write("</td>")
            md.write(serializeValue(knownTables[name]["value"]))
            md.write("</tr>");

# FIXME: decide what to do with these values.
for value, count in sorted(otherValuesCount.items(),
                           key=operator.itemgetter(1), reverse=True):
    for entry in otherEntries[value]:
        md.write("<tr style='text-decoration: line-through;'>");
        md.write("<td>&#x%0X; U+%04X</td>" % (entry, entry))
        md.write("<td colspan='5'>%s</td>" % value)
        md.write("</tr>");
for name in otherEntriesWithMultipleCharacters:
    md.write("<tr style='text-decoration: line-through;'>");
    md.write("<td>")
    md.write(name)
    md.write("</td>")
    md.write(serializeValue(otherEntriesWithMultipleCharacters[name]))
    md.write("</tr>");

md.write("</table>\n");
print("done.");
