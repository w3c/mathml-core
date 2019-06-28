#!/usr/bin/python

from __future__ import print_function
from lxml import etree
from download import downloadUnicodeXML

# Retrieve the unicode.xml file if necessary.
unicodeXML = downloadUnicodeXML()

# Extract the mathvariants transformation.
xsltTransform = etree.XSLT(etree.XML('''\
<xsl:stylesheet version="1.0"
                       xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:strip-space elements="*"/>
  <xsl:template match="charlist">
    <root><xsl:apply-templates select="character"/></root>
  </xsl:template>
  <xsl:template match="character">
    <xsl:if test="surrogate">
      <entry>
        <xsl:attribute name="mathvariant">
            <xsl:value-of select="surrogate/@mathvariant"/>
        </xsl:attribute>
        <xsl:attribute name="baseChar">
          <xsl:value-of select="surrogate/@ref"/>
        </xsl:attribute>
        <xsl:attribute name="transformedChar">
          <xsl:choose>
            <xsl:when test="bmp">
              <xsl:value-of select="bmp/@ref"/>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="@id"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
      </entry>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>'''))

# Put the mathvariant transforms into a Python structure.
mathvariantTransforms = {}
root = xsltTransform(etree.parse(unicodeXML)).getroot()
def parseCodePoint(aHexaString):
    return int("0x%s" % aHexaString[1:], 16)
for entry in root:
    mathvariant = entry.get("mathvariant")
    baseChar = parseCodePoint(entry.get("baseChar"))
    transformedChar = parseCodePoint(entry.get("transformedChar"))
    if mathvariant not in mathvariantTransforms:
        mathvariantTransforms[mathvariant] = {}
    mathvariantTransforms[mathvariant][baseChar] = transformedChar

# There is no "isolated" mathvariant.
del mathvariantTransforms["isolated"]

# Create a test font for each mathvariant.
for mathvariant in mathvariantTransforms:
    print("Generate mathvariant table for %s..." % mathvariant, end=" ");
    md = open("mathvariants-%s.html" % mathvariant, "w")
    md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");
    md.write("<table>\n");
    md.write("<tr><th>Original</th><th>%s</th></tr>\n" % mathvariant)
    for baseChar in mathvariantTransforms[mathvariant]:
        transformedChar = mathvariantTransforms[mathvariant][baseChar]
        md.write('<tr><td>&#x%0X; U+%04X</td><td>&#x%0X; U+%05X</td></tr>\n' %
                 (baseChar, baseChar, transformedChar, transformedChar))
    md.write("</table>");
    print("done.");
md.close()
