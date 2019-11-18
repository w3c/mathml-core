#!/usr/bin/python

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

def buildKey(characters, form):
    # Concatenate characters and form to build the key.
    key = ""
    for c in characters:
        key += unichr(c)
    key += " " + form
    return key

# Extract the operator dictionary.
xsltTransform = etree.XSLT(etree.parse("./operator-dictionary.xsl"))

root = xsltTransform(etree.parse(unicodeXML)).getroot()
entriesWithMultipleCharacters={}
knownTables = {
    "infixEntriesWithDefaultValues": [],
    "infixEntriesWithSpacing4": [],
    "infixEntriesWithSpacing3": [],
    "infixEntriesWithSpacing5AndAccent": [],
    "infixEntriesWithSpacing5AndAccentStretchy": [],
    "infixEntriesWithSpacing5AndStretchy": [],
    "postfixEntriesWithSpacing0AndAccent": [],
    "prefixEntriesWithSpacing0AndStretchySymmetricFence": [],
    "postfixEntriesWithSpacing0AndStretchySymmetricFence": [],
    "postfixEntriesWithSpacing0AndAccentStretchy": [],
    "prefixEntriesWithLspace1Rspace2AndSymmetricMovablelimitsLargeop": [],
    "prefixEntriesWithLspace1Rspace2AndSymmetricLargeop": [],
    "prefixEntriesWithLspace0Rspace1AndSymmetricLargeop": [],
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
                                   "accent",
                                   "fence",
                                   "separator"])

    if len(characters) > 1:
        entriesWithMultipleCharacters[key] = value
        continue
    character = characters[0]

    if (value["lspace"] == defaultSpacing and
        value["rspace"] == defaultSpacing and
        "properties" not in value and
        form == "infix"):
        knownTables["infixEntriesWithDefaultValues"].append(character)
        continue

    if (value["lspace"] == 4 and
        value["rspace"] == 4 and
        "properties" not in value and
        form == "infix"):
        knownTables["infixEntriesWithSpacing4"].append(character)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" not in value and
        form == "infix"):
        knownTables["infixEntriesWithSpacing3"].append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'accent': True} and
        form == "infix"):
        knownTables["infixEntriesWithSpacing5AndAccent"].append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'accent': True, 'stretchy': True} and
        form == "infix"):
        knownTables["infixEntriesWithSpacing5AndAccentStretchy"].append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'stretchy': True} and
        form == "infix"):
        knownTables["infixEntriesWithSpacing5AndStretchy"].append(character)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'accent': True} and
        form == "postfix"):
        knownTables["postfixEntriesWithSpacing0AndAccent"].append(character)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True, 'fence': True} and
        form == "prefix"):
        knownTables["prefixEntriesWithSpacing0AndStretchySymmetricFence"].append(character)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True, 'fence': True} and
        form == "postfix"):
        knownTables["postfixEntriesWithSpacing0AndStretchySymmetricFence"].append(character)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'accent': True, 'stretchy': True} and
        form == "postfix"):
        knownTables["postfixEntriesWithSpacing0AndAccentStretchy"].append(character)
        continue

    if (value["lspace"] == 1 and
        value["rspace"] == 2 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'movablelimits': True, 'largeop': True} and
        form == "prefix"):
        knownTables["prefixEntriesWithLspace1Rspace2AndSymmetricMovablelimitsLargeop"].append(character)
        continue

    if (value["lspace"] == 1 and
        value["rspace"] == 2 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        knownTables["prefixEntriesWithLspace1Rspace2AndSymmetricLargeop"].append(character)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 1 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        knownTables["prefixEntriesWithLspace0Rspace1AndSymmetricLargeop"].append(character)
        continue

    v = str(value)
    if v not in otherValuesCount:
        otherValuesCount[v] = 0
    otherValuesCount[v] += 1
    otherValueTotalCount += 1

    otherEntries[key] = value


def toHexa(character):
    return "U+%04X" % character

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

for name, table in sorted(knownTables.items(),
                          key=(lambda v: len(v[1])), reverse=True):
    print(name, len(table))
    print(toUnicodeRanges(table))
    print("")

print("otherEntries", otherValueTotalCount)
for value, count in sorted(otherValuesCount.items(),
                           key=operator.itemgetter(1), reverse=True):
   print("  * %d: %s" % (count, str(value)))
print("")

print("entriesWithMultipleCharacters", len(entriesWithMultipleCharacters))
for name in entriesWithMultipleCharacters:
   print("  * %s: %s" % (name, str(entriesWithMultipleCharacters[name])))

# TODO: format tables
