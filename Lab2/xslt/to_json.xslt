<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Выводим plain text -->
  <xsl:output method="text" encoding="UTF-8"/>

  <!-- Главный шаблон: формируем JSON-массив albums -->
  <xsl:template match="/albums">
    <xsl:text>[</xsl:text>
    <xsl:for-each select="album">
      <xsl:if test="position() &gt; 1">
        <xsl:text>,</xsl:text>
      </xsl:if>
      <xsl:text>&#10;  {</xsl:text>

      <!-- title -->
      <xsl:text>&#10;    "title": "</xsl:text>
      <xsl:value-of select="title"/>
      <xsl:text>",</xsl:text>

      <!-- artists -->
      <xsl:text>&#10;    "artists": [</xsl:text>
      <xsl:for-each select="artists/artist">
        <xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
        <xsl:text>"</xsl:text>
        <xsl:value-of select="."/>
        <xsl:text>"</xsl:text>
      </xsl:for-each>
      <xsl:text>],</xsl:text>

      <!-- genres -->
      <xsl:text>&#10;    "genres": [</xsl:text>
      <xsl:for-each select="genres/genre">
        <xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
        <xsl:text>"</xsl:text>
        <xsl:value-of select="."/>
        <xsl:text>"</xsl:text>
      </xsl:for-each>
      <xsl:text>],</xsl:text>

      <!-- releaseDate -->
      <xsl:text>&#10;    "releaseDate": "</xsl:text>
      <xsl:value-of select="releaseDate"/>
      <xsl:text>",</xsl:text>

      <!-- ageLimit -->
      <xsl:text>&#10;    "ageLimit": "</xsl:text>
      <xsl:value-of select="ageLimit"/>
      <xsl:text>",</xsl:text>

      <!-- tracks -->
      <xsl:text>&#10;    "tracks": [</xsl:text>
      <xsl:for-each select="tracks/track">
        <xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
        <xsl:text>&#10;      { "title": "</xsl:text>
        <xsl:value-of select="title"/>
        <xsl:text>", "duration": "</xsl:text>
        <xsl:value-of select="duration"/>
        <xsl:text>" }</xsl:text>
      </xsl:for-each>
      <xsl:text>&#10;    ]</xsl:text>

      <xsl:text>&#10;  }</xsl:text>
    </xsl:for-each>
    <xsl:text>&#10;]</xsl:text>
  </xsl:template>

</xsl:stylesheet>
