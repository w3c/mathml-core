#!/usr/bin/python

from lxml import etree
from download import downloadUnicodeXML

import operator
#import json, re
#from utils import mathfont

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
infixEntriesWithDefaultValues=[]
infixEntriesWithSpacing4=[]
infixEntriesWithSpacing3=[]
infixEntriesWithSpacing5AndAccent=[]
infixEntriesWithSpacing5AndAccentStretchy=[]
infixEntriesWithSpacing5AndStretchy=[]
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
        infixEntriesWithDefaultValues.append(character)
        continue
    
    if (value["lspace"] == 4 and
        value["rspace"] == 4 and
        "properties" not in value and
        form == "infix"):
        infixEntriesWithSpacing4.append(character)
        continue
    
    if (value["lspace"] == 3 and
        value["rspace"] == 3 and
        "properties" not in value and
        form == "infix"):
        infixEntriesWithSpacing3.append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'accent': True} and
        form == "infix"):
        infixEntriesWithSpacing5AndAccent.append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'accent': True, 'stretchy': True} and
        form == "infix"):
        infixEntriesWithSpacing5AndAccentStretchy.append(character)
        continue

    if (value["lspace"] == 5 and
        value["rspace"] == 5 and
        value["properties"] == {'stretchy': True} and
        form == "infix"):
        infixEntriesWithSpacing5AndStretchy.append(character)
        continue
    
    v = str(value)
    if v not in otherValuesCount:
        otherValuesCount[v] = 0
    otherValuesCount[v] += 1
    otherValueTotalCount += 1

    otherEntries[key] = value
    
print("entriesWithMultipleCharacters", len(entriesWithMultipleCharacters))
print("infixEntriesWithDefaultValues", len(infixEntriesWithDefaultValues))
print("infixEntriesWithSpacing3", len(infixEntriesWithSpacing3))
print("infixEntriesWithSpacing4", len(infixEntriesWithSpacing4))
print("infixEntriesWithSpacing5AndAccent", len(infixEntriesWithSpacing5AndAccent))
print("infixEntriesWithSpacing5AndAccentStretchy", len(infixEntriesWithSpacing5AndAccentStretchy))
print("infixEntriesWithSpacing5AndStretchy", len(infixEntriesWithSpacing5AndStretchy))
print("otherEntries", otherValueTotalCount)
for v in sorted(otherValuesCount.items(),
                key=operator.itemgetter(1), reverse=True):
   print("  * %d: %s" % (v[1], str(v[0])))

# TODO: format tables
