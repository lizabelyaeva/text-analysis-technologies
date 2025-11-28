<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!-- Режим вывода: текст -->
  <xsl:output method="text" encoding="UTF-8"/>

  <!-- Шаблон для корня: обходим все album -->
  <xsl:template match="/albums">
    <xsl:text>Albums list
====================
</xsl:text>
    <xsl:for-each select="album">
      <xsl:text>Title: </xsl:text><xsl:value-of select="title"/><xsl:text>&#10;</xsl:text>
      <xsl:text>Artists: </xsl:text>
      <xsl:for-each select="artists/artist">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
      </xsl:for-each>
      <xsl:text>&#10;</xsl:text>

      <xsl:text>Genres: </xsl:text>
      <xsl:for-each select="genres/genre">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
      </xsl:for-each>
      <xsl:text>&#10;</xsl:text>

      <xsl:text>Release date: </xsl:text><xsl:value-of select="releaseDate"/><xsl:text>&#10;</xsl:text>
      <xsl:text>Age limit: </xsl:text><xsl:value-of select="ageLimit"/><xsl:text>&#10;</xsl:text>

      <xsl:text>Tracks:</xsl:text><xsl:text>&#10;</xsl:text>
      <xsl:for-each select="tracks/track">
        <xsl:text>  - </xsl:text><xsl:value-of select="title"/>
        <xsl:text> (</xsl:text><xsl:value-of select="duration"/><xsl:text>)</xsl:text>
        <xsl:text>&#10;</xsl:text>
      </xsl:for-each>

      <xsl:text>--------------------</xsl:text><xsl:text>&#10;&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
