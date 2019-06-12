#!/usr/bin/python

from __future__ import print_function
from lxml import etree
import os
import progressbar
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def downloadWithProgressBar(url, outputDirectory="./", forceDownload=False):

    baseName = os.path.basename(url)
    fileName = os.path.join(outputDirectory, baseName)

    if not forceDownload and os.path.exists(fileName):
        return fileName

    request = urlopen(url)
    totalSize = int(request.info().getheader('Content-Length').strip())
    bar = progressbar.ProgressBar(maxval=totalSize).start()

    chunkSize = 16 * 1024
    downloaded = 0
    print("Downloading %s" % url)
    os.umask(0o002)
    with open(fileName, 'wb') as fp:
        while True:
            chunk = request.read(chunkSize)
            downloaded += len(chunk)
            bar.update(downloaded)
            if not chunk: break
            fp.write(chunk)
        bar.finish()

    return fileName

# Retrieve the unicode.xml file if necessary.
unicodeXML = downloadWithProgressBar("http://www.w3.org/2003/entities/2007xml/unicode.xml")

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
print("Generate mathvariant tables...", end=" ");
md = open("mathvariants.html", "w")
md.write("<!-- This file was automatically generated from generate-math-variant-tables.py. Do not edit. -->\n");
for mathvariant in mathvariantTransforms:
    md.write("<section>\n")
    md.write("<h4><code>%s</code> mappings</h4>\n" % mathvariant)
    md.write("<table>\n");
    md.write("<tr><th>Original</th><th>%s</th></tr>\n" % mathvariant)
    for baseChar in mathvariantTransforms[mathvariant]:
        transformedChar = mathvariantTransforms[mathvariant][baseChar]
        md.write('<tr><td>&#x%0X; U+%04X</td><td>&#x%0X; U+%05X</td></tr>\n' %
                 (baseChar, baseChar, transformedChar, transformedChar))
    md.write("</table>\n");
    md.write("</section>\n\n")
md.close()
print("done.");
