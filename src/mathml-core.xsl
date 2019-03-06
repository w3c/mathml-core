<xsl:stylesheet version="3.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xs="http://www.w3.org/2001/XMLSchema"
		xmlns:f="data:,f"
		exclude-result-prefixes="xs f"
		>

 <xsl:output method="html" version="5"/>


 <xsl:template match="/">
  <xsl:variable name="p1">
  <xsl:apply-templates mode="include"/>
  </xsl:variable>
  <xsl:apply-templates select="$p1/node()"/>
 </xsl:template>

 
 
 <xsl:template mode="include" match="include">
  <xsl:copy-of select="doc(concat(@file,'.html'))/html/body/(abstract|section)"/>
 </xsl:template>

 <xsl:template mode="include" match="*">
  <xsl:copy>
   <xsl:copy-of select="@*"/>
   <xsl:apply-templates mode="include"/>
  </xsl:copy>
 </xsl:template>


 <xsl:template match="img[matches(@src,'^figures.*svg')]" >
  <xsl:apply-templates mode="svg" select="doc(@src)/node()">
   <xsl:with-param name="file" select="substring-after(@src,'figures/')" tunnel="yes"/>
   <xsl:with-param name="gid" select="generate-id()" tunnel="yes"/>
  </xsl:apply-templates>
 </xsl:template>

<!-- svg mode unnamespaces elements and makes ids unique-->
 <xsl:template match="@*|node()" mode="svg">
  <xsl:copy>
   <xsl:apply-templates select="@*,node()" mode="svg"/>
  </xsl:copy>
 </xsl:template>

 <xsl:template match="*" mode="svg" priority="2">
  <xsl:element name="{local-name(.)}">
   <xsl:apply-templates select="@*,node()" mode="svg"/>
  </xsl:element>
 </xsl:template>

<!-- would need to make use of the ids match as well if there were any-->
 <xsl:template match="@id" mode="svg">
  <xsl:param name="file" tunnel="yes"/>
  <xsl:attribute name="id" select="concat($file,'.',.)"/>
 </xsl:template>

<!-- ensure font class selectors stay local -->
 <xsl:template match="*:style/text()" mode="svg">
  <xsl:param name="file" tunnel="yes"/>
  <xsl:variable name="qf" select="replace($file,'\.','\\\\.')"/>
  <xsl:value-of select="replace(.,'text\.f[0-9]+',
			concat('#',$qf,'\\.page1 $0'))"/>
 </xsl:template>

  
<xsl:template  match="spec">
 <html lang="en">
  <head>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>
<script src="sorttable.js"/>
<title><xsl:apply-templates mode="title" select="front/title"/></title>
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
 <xsl:apply-templates mode="toc" select="./div/section"/>
 </ol>
</nav>

<div class="body">

 <xsl:apply-templates select="./div/section"/>

</div>


</body>
 </html>
 </xsl:template>


 <!-- toc -->

 <xsl:template mode="toc" match="section">
  <li>
   <a href="#{@id}">
    <span>
     <xsl:if test="../@id='appendix'">Appendix </xsl:if>
     <xsl:value-of select="f:number(.)"/>
    </span>
    <xsl:text> </xsl:text>
    <xsl:apply-templates select="(h1|h2|h3)[1]/node()"/>
   </a>
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

 <xsl:template match="h1|h2|h3">
 <xsl:copy>
  <xsl:copy-of select="@*"/>
      <span class="secnum">
       <xsl:if test="../../@id='appendix'">Appendix </xsl:if>
       <xsl:value-of select="f:number(parent::section)"/>
      </span>
      <xsl:text> </xsl:text>
    <xsl:apply-templates/>
 </xsl:copy>
</xsl:template>

<!-- single file output -->
<xsl:template match="a">
 <xsl:copy>
  <xsl:copy-of select="@*"/>
  <xsl:choose>
   <xsl:when  test="matches(@href,'^[a-zA-Z0-9.]*#')">
    <xsl:variable name="id" select="replace(@href,'^[a-zA-Z0-9.]*#','')"/>
    <xsl:attribute name="href" select="concat('#',$id)"/>
    <xsl:choose>
     <xsl:when test=".='auto'">
      <xsl:for-each select="key('id',$id)">
       <xsl:choose>
	<xsl:when test="self::section">
	<xsl:number level="multiple" select="."/>
	</xsl:when>
	<xsl:when test="self::figure">
	<xsl:number level="any" select="."/>
	</xsl:when>
	<xsl:when test="self::li/ancestor::section/@id='references'">
	 <xsl:apply-templates select="span[1]/node()"/>
	</xsl:when>
	<xsl:otherwise>
	 <xsl:message select="'href to #:',name(),  $id"/>
	 <xsl:text>Unknown Reference</xsl:text>
	</xsl:otherwise>
       </xsl:choose>
      </xsl:for-each>
      <xsl:if test="not(key('id',$id))">
	 <xsl:message select="'href to id #:', $id"/>
	 <xsl:text>Unknown Reference</xsl:text>
      </xsl:if>
     </xsl:when>
     <xsl:otherwise>
      <xsl:apply-templates/>
     </xsl:otherwise>
    </xsl:choose>
     </xsl:when>
     <xsl:otherwise>
      <xsl:copy-of select="@href"/>
      <xsl:apply-templates/>
     </xsl:otherwise>
    </xsl:choose>
   </xsl:copy>
  </xsl:template>



<!-- hyperlinked rnc listings -->
<xsl:template match="rnc">
 <xsl:variable name="l">
  <section xmlns="">
   <xsl:copy-of select="ancestor::section[@id][1]/@id"/>
   <pre class="example">
   <xsl:copy-of select="@revisionflag"/>
   <xsl:analyze-string select="replace(unparsed-text(concat('../',@file)),'(\s+$|^\s+)','')" regex="(#.*)">
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



<xsl:function name="f:number">
 <xsl:param name="e" as="element()"/>
 <xsl:for-each select="$e">
  <xsl:choose>
   <xsl:when  test="ancestor::div[last()]/@id='appendix'">
    <xsl:number level="multiple" format="A.1"/>
   </xsl:when>
   <xsl:otherwise>
    <xsl:number level="multiple"/>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:for-each>
</xsl:function>


<!-- operator dictionary -->

<xsl:template  match="opdict">


 <xsl:variable  name="c" select="'priority','lspace','rspace'"/>
 <xsl:variable  name="p" select="'fence','stretchy','separator','accent','largeop','movablelimits', 'symmetric'"/>
 <xsl:variable name="v" select="'linebreakstyle','minsize'"/>
<xsl:text>&#10;</xsl:text>
 <table class="sortable">
<xsl:text>&#10;</xsl:text>
   <thead>
<xsl:text>&#10;</xsl:text>
     <tr>
<xsl:text>&#10;</xsl:text>
       <xsl:for-each select="'Character','Glyph','Name','form',$c,'Properties'">
	 <th><xsl:value-of select="."/></th>
       </xsl:for-each>
     </tr>
<xsl:text>&#10;</xsl:text>
   </thead>
<xsl:text>&#10;</xsl:text>
   <tbody>
<xsl:text>&#10;</xsl:text>
     <xsl:for-each select="doc('unicode.xml')/unicode/charlist/character/operator-dictionary">
       <xsl:sort select="xs:integer(@priority)"/>
       <xsl:text>&#10;</xsl:text>
       <tr>

	<xsl:if test="../@id='U02ADC'">
          <xsl:attribute name="class" select="'diff-chg'"/>
	</xsl:if>
	 <xsl:variable name="od" select="."/>
	 <xsl:variable name="d" select="for $i in tokenize(../@dec,'-') return xs:integer($i)"/>
	 <xsl:text>&#10;</xsl:text>
	 <th>
	  <xsl:attribute name="abbr" select="$d[1]"/>
	   <xsl:choose>
	     <xsl:when test="empty($d[. &gt;127])">
	     <xsl:value-of select="replace(replace(codepoints-to-string($d),'&amp;','&amp;amp;'),'&lt;','&amp;lt;')"/>
	     </xsl:when>
	     <xsl:otherwise>
	       <xsl:value-of select="replace(../@id,'[U-]0*([0-9A-F]*)','&amp;#x$1;')"/>
	     </xsl:otherwise>
	   </xsl:choose>
	 </th>
	 <th>
	  <xsl:value-of select="
				if($d=9001)
				 then '&#x3008;'
				else if($d=9002) then
				'&#x3009;'
				else codepoints-to-string($d)"/>
	 </th>
	 <th class="uname">
	 <xsl:value-of select="lower-case(../description)"/></th>
	 <th><xsl:value-of select="@form"/></th>
	 <xsl:for-each select="$c">
	   <td><xsl:value-of select="$od/@*[name()=current()]"/></td>
	 </xsl:for-each>
	 <td>
	   <xsl:value-of select="
				 $p[$od/@*[.='true']/name()=.],
				 $od/@*[name()=$v]/concat(name(),'=',.)
            " separator=", "/>
	 </td>
<xsl:text>&#10;</xsl:text>
       </tr>
<xsl:text>&#10;</xsl:text>
     </xsl:for-each>
   </tbody>
<xsl:text>&#10;</xsl:text>
 </table>
<xsl:text>&#10;</xsl:text>
</xsl:template>



<!-- combining character mapping -->
<xsl:key name="id" match="*[@id]" use="@id"/>

<xsl:template match="combequiv">
 <section id="comb-comb">
  <h2>Combining</h2>
  <table>
   <thead>
    <tr>
     <th colspan="2">Non Combining</th>
     <th>Style</th>
     <th colspan="2">Combining</th>
    </tr>
   </thead>
   <tbody>
    <xsl:for-each select="doc('unicode.xml')/unicode/charlist/character/combref">
     <tr>
      <td><xsl:value-of select="replace(../@id,'U0?','U+')"/></td>
      <td><xsl:value-of select="lower-case(../description)"/></td>
      <td><xsl:value-of select="@style"/></td>
      <td><xsl:value-of select="replace(@ref,'U0?','U+')"/></td>
      <td><xsl:value-of select="lower-case(key('id',@ref)/description)"/></td>
      </tr>
    </xsl:for-each>
   </tbody>
  </table>
 </section>
 <section id="comb-noncomb">
  <h2>Non Combining</h2>
  <!-- not clear both of these are needed-->
  <table>
   <thead>
    <tr>
     <th colspan="2">Combining</th>
     <th>Style</th>
     <th colspan="2">Non Combining</th>
    </tr>
   </thead>
   <tbody>
    <xsl:for-each select="doc('unicode.xml')/unicode/charlist/character/noncombref">
     <tr>
      <td><xsl:value-of select="replace(../@id,'U0?','U+')"/></td>
      <td><xsl:value-of select="lower-case(../description)"/></td>
      <td><xsl:value-of select="@style"/></td>
      <td><xsl:value-of select="replace(@ref,'U0?','U+')"/></td>
      <td><xsl:value-of select="lower-case(key('id',@ref)/description)"/></td>
      </tr>
    </xsl:for-each>
   </tbody>
  </table>
 </section>
</xsl:template>



<!-- issue handling -->
 <xsl:variable name="issues" select="json-to-xml(unparsed-text('https://api.github.com/repos/mathml-refresh/mathml/issues?labels=core'))"/>
 
 <xsl:template match="ul[@id='openissues']">
  <table>
   <tbody>
    <xsl:for-each select="$issues/*/*:map">
     <xsl:sort select="number(*:number[@key='number'])"/>
     <tr>
      <td><xsl:value-of select="*:number[@key='number']"/></td>
      <td><a href="{*:string[@key='html_url']}">
      <xsl:value-of select="*:string[@key='title']"/></a></td>
     </tr>
    </xsl:for-each>
   </tbody>
  </table>
 </xsl:template>

<!-- individual issue asides, only appears if still in open list -->
<xsl:template match="aside[@data-gh]">
  <xsl:for-each select="$issues/*/*:map[*:number[@key='number']=current()/@data-gh]">
   <aside class="issue" id="gh-issue-{@data-gh}">
    GitHub Issue <xsl:value-of select="*:number[@key='number']"/>:
   <a href="{*:string[@key='html_url']}">
      <xsl:value-of select="*:string[@key='title']"/>
   </a>
 </aside>
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
