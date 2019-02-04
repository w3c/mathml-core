<xsl:stylesheet version="3.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xs="http://www.w3.org/2001/XMLSchema"
		exclude-result-prefixes="xs"
		>

<xsl:output method="html" />

<xsl:template  match="spec">
 <html lang="en">
  <head>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>
<title><xsl:apply-templates mode="title" select="front/title"/></title>
<link rel="stylesheet" href="LaTeXML.css" type="text/css"/>
<link rel="stylesheet" href="ltx-article.css" type="text/css"/>
<link rel="stylesheet" href="ltx-listings.css" type="text/css"/>
<link rel="stylesheet" href="style.css" type="text/css"/>
<style type="text/css">
  pre { white-space: pre-wrap;}
 </style>
<style>
  a.loc {
  padding-bottom: .1em; /* align underline with the rest of the text */
  color: hsla(203, 90%, 30%,.8);
	}
 </style>
<link rel="stylesheet" type="text/css" href="https://www.w3.org/StyleSheets/TR/2016/W3C-ED"/>

<script src="//www.w3.org/scripts/TR/2016/fixup.js"> </script>
  </head>
  <body>
   <div class="head"><p><a href="https://www.w3.org/"><img src="https://www.w3.org/StyleSheets/TR/2016/logos/W3C" alt="W3C" height="48" width="72"/></a></p>
<h1 id="title"><xsl:apply-templates select="front/title/node()"/></h1>
<h2 id="w3c-doctype">Editors' Draft</h2>
<dl>
<dt>This version:</dt><dd><a href="#">...</a></dd>
<dt>Editors:</dt>
<dd><xsl:apply-templates select="front/editors"/></dd></dl>
<p class="copyright"><a href="https://www.w3.org/Consortium/Legal/ipr-notice#Copyright">Copyright</a> &#xa9; 1998-2017 <a href="https://www.w3.org/"><abbr title="World Wide Web Consortium">W3C</abbr></a><sup>&#xae;</sup> (<a href="https://www.csail.mit.edu/"><abbr title="Massachusetts Institute of Technology">MIT</abbr></a>, <a href="https://www.ercim.eu/"><abbr title="European Research Consortium for Informatics and Mathematics">ERCIM</abbr></a>, <a href="https://www.keio.ac.jp/">Keio</a>, <a href="http://ev.buaa.edu.cn/">Beihang</a>). W3C <a href="https://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer">liability</a>, <a href="https://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks">trademark</a> and <a href="https://www.w3.org/Consortium/Legal/copyright-documents">document use</a> rules apply.</p>
   <hr title="Separator for header"/></div>

   <div>
    <h2><a id="abstract"></a>Abstract</h2>
    <xsl:apply-templates select="abstract/*"/>
   </div>
<div>
<h2><a id="status"></a>Status of this Document</h2>
<p><strong>This document is an editors' copy that has no official standing.</strong></p>
<xsl:apply-templates select="form/status/*"/>
</div>

<p>This document is governed by the <a href="https://www.w3.org/2017/Process-20170301/" id="w3c_process_revision">1 March 2017 W3C Process Document</a>. </p>

<nav id="toc">
 <h2 id="tochead">Table of Contents</h2>
 <ol class="toc">
 <xsl:apply-templates mode="toc" select="minh|section"/>
 </ol>
</nav>

<div class="body">

 <xsl:apply-templates select="minh|section"/>

</div>


</body>
 </html>
 </xsl:template>


 <!-- toc -->
 <xsl:template match="minh" mode="toc">
  <xsl:apply-templates mode="toc" select="doc(concat('MathMLinHTML5-xml/',@file,'.xml'))/html/body/div/div/section"/>
 </xsl:template>

 <xsl:template mode="toc" match="section">
  <li>
   <a href="#{@id}"><xsl:apply-templates select="(h1|h2|h3)[1]/node()"/></a>
   <xsl:if test="section">
    <ol class="toc">
   <xsl:apply-templates mode="toc" select="section"/>
    </ol>
   </xsl:if>
  </li>
 </xsl:template>

<!-- main mode -->

 <xsl:template match="*">
  <xsl:copy>
   <xsl:copy-of select="@*"/>
   <xsl:apply-templates/>
  </xsl:copy>
 </xsl:template>


 <xsl:template match="minh">
  <xsl:apply-templates select="doc(concat('MathMLinHTML5-xml/',@file,'.xml'))/html/body/div/div/section"/>
 </xsl:template>


<!-- hyperlinked rnc listings -->
<xsl:template match="rnc">
 <xsl:variable name="l">
  <section xmlns="">
   <xsl:copy-of select="ancestor::section[@id][1]/@id"/>
   <pre class="example">
   <xsl:copy-of select="@revisionflag"/>
   <xsl:analyze-string select="replace(unparsed-text(concat('./',@file)),'(\s+$|^\s+)','')" regex="(#.*)">
    <xsl:matching-substring>
     <comment><xsl:value-of select="."/></comment>
    </xsl:matching-substring>
    <xsl:non-matching-substring>
     <xsl:analyze-string select="." regex="&quot;[^&quot;]*&quot;">
      <xsl:matching-substring>
       <string><xsl:value-of select="."/></string>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
       <xsl:analyze-string select="." regex="[a-zA-Z][a-zA-Z0-9\.:\-]*">
	<xsl:matching-substring>
	 <token><xsl:value-of select="."/></token>
	</xsl:matching-substring>
	<xsl:non-matching-substring>
	 <xsl:value-of select="."/>
	</xsl:non-matching-substring>
       </xsl:analyze-string>
      </xsl:non-matching-substring>
     </xsl:analyze-string>
    </xsl:non-matching-substring>
   </xsl:analyze-string>
   <xsl:text>&#10;</xsl:text>
  </pre>
  </section>
 </xsl:variable>
 <xsl:apply-templates select="$l/section/*"/>
</xsl:template>

<xsl:template match="comment">
<span style="color:brown;"><xsl:value-of select="."/></span></xsl:template>

<xsl:template match="token">
  <xsl:value-of select="."/>
</xsl:template>
<xsl:template match="string">
  <xsl:value-of select="."/>
</xsl:template>


<xsl:template match="token[not(preceding-sibling::*[1]='element' 
or preceding-sibling::*[1]='attribute')]" priority="2">
<a href="#rnc{ancestor::section[1]/@id[not(current()='OMOBJ')]}{.}"><xsl:value-of select="."/></a>
</xsl:template>

<xsl:template match="token[.='element' or .='attribute'
or .='default' or .='namespace' or .='pattern' or .='text' 
or .='include']"
priority="4">
  <span style="font-weight:bold;"><xsl:value-of select="."/></span>
</xsl:template>

<xsl:template
match="token[starts-with(normalize-space(following-sibling::node()[1]),'=')]"
priority="3">
<a name="rnc{ancestor::section[1]/@id[not(current()='OMOBJ')]}{preceding-sibling::*[1][.='namespace']}{.}" style="color:blue;"><xsl:value-of select="."/></a>
</xsl:template>


<xsl:template
match="token[contains(.,':')]" priority="5">
<a href="#rnc{ancestor::section[1]/@id}namespace{substring-before(.,':')}"><xsl:value-of
select="substring-before(.,':')"/>:</a>
<xsl:value-of select="substring-after(.,':')"/>
</xsl:template>

<xsl:template match="token[starts-with(.,'xsd:')]" priority="6">
  <span style="font-weight:bold;"><xsl:value-of select="."/></span>
</xsl:template>

</xsl:stylesheet>
