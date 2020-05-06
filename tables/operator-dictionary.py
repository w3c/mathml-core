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

def appendCharacters(name, character):
    if len(characters) > 1:
        if "multipleChar" not in knownTables[name]:
            knownTables[name]["multipleChar"] = []
        knownTables[name]["multipleChar"].append(serializeString(characters))
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
            for string in sorted(table):
                print("'%s' " % string, end="")
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
            appendCharacters("fences", characters)
            del value["properties"]["fence"]
        if ("separator" in value["properties"]):
            appendCharacters("separators", characters)
            del value["properties"]["separator"]
        if (value["properties"] == {}):
            del value["properties"]

    if (value["lspace"] == defaultSpacing and
        value["rspace"] == defaultSpacing and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithDefaultValues", characters)
        continue

    if (value["lspace"] == 4 and
        value["rspace"] == 4 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing4", characters)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" not in value and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing3", characters)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'stretchy': True} and
        form == "infix"):
        appendCharacters("infixEntriesWithSpacing5AndStretchy", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithSpacing0AndStretchySymmetric", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'stretchy': True} and
        form == "postfix"):
        appendCharacters("postfixEntriesWithSpacing0AndStretchySymmetric", characters)
        continue

    if (value["lspace"] == 1 and
        value["rspace"] == 2 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'movablelimits': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace1Rspace2AndSymmetricMovablelimitsLargeop", characters)
        continue

    if (value["lspace"] == 1 and
        value["rspace"] == 2 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace1Rspace2AndSymmetricLargeop", characters)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'movablelimits': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace3Rspace3AndSymmetricMovablelimitsLargeop", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 1 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace0Rspace1AndSymmetricLargeop", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace0Rspace0", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" not in value and
        form == "postfix"):
        appendCharacters("postfixEntriesWithLspace0Rspace0", characters)
        continue

    if (value["lspace"] == 0 and
        value["rspace"] == 0 and
        "properties" in value and
        value["properties"] == {'stretchy': True} and
        form == "postfix"):
        appendCharacters("postfixEntriesWithLspace0Rspace0AndStretchy", characters)
        continue

    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" in value and
        value["properties"] == {'symmetric': True, 'largeop': True} and
        form == "prefix"):
        appendCharacters("prefixEntriesWithLspace3Rspace3AndSymmetricLargeop", characters)
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
    otherEntries[v].append(toHexa(character))

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
   print("    %s" % str(otherEntries[value]))
   print("")

print("otherEntriesWithMultipleCharacters",
      len(otherEntriesWithMultipleCharacters))
for name in otherEntriesWithMultipleCharacters:
   print("  * %s: %s" % (name, str(otherEntriesWithMultipleCharacters[name])))
print("")

print("Separate tables for fences and separators:\n")
dumpKnownTables(True)

# TODO: format tables
