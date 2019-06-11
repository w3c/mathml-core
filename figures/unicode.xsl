<!-- generate tables to be included -->
<!--
 java -jar saxon9he.jar ../xml-entities/unicode.xml  figures/unicode.xsl
-->
<xsl:stylesheet version="3.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xs="http://www.w3.org/2001/XMLSchema"
		xmlns:f="data:,f"
		exclude-result-prefixes="xs f"
		>

 <xsl:output method="xml" doctype-public="" doctype-system="" omit-xml-declaration="yes"/>

 <xsl:key name="id" match="*[@id]" use="@id"/>
 
<!-- operator dictionary -->

<xsl:template  match="/">

<xsl:result-document href="op-dict.html">

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
     <xsl:for-each select="/unicode/charlist/character/operator-dictionary">
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
</xsl:result-document>




<!-- combining character mapping -->


<xsl:result-document href="comb-table.html">
 <section id="comb-comb">
  <h3>Combining</h3>
  <table>
   <thead>
    <tr>
     <th colspan="2">Non Combining</th>
     <th>Style</th>
     <th colspan="2">Combining</th>
    </tr>
   </thead>
   <tbody>
    <xsl:for-each select="/unicode/charlist/character/combref">
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
  <h3>Non Combining</h3>
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
    <xsl:for-each select="/unicode/charlist/character/noncombref">
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
</xsl:result-document>
</xsl:template>


</xsl:stylesheet>
