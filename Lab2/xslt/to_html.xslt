<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!-- Выводим HTML -->
  <xsl:output method="html" encoding="UTF-8" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN" />

  <!-- Главный шаблон -->
  <xsl:template match="/">
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>Albums</title>
        <style type="text/css">
          body { font-family: Arial, sans-serif; margin: 20px; background:#f7f7f7; color:#222; }
          table.albums { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 0 5px rgba(0,0,0,0.05); }
          table.albums th, table.albums td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
          table.albums th { background: #2b6cb0; color: #fff; font-weight: 600; }
          tr.album-row:nth-child(even) { background: #fbfdff; }
          .tracks-list { margin:0; padding-left: 18px; }
          .small { font-size: 0.9em; color: #555; }
        </style>
      </head>
      <body>
        <h1>Music albums</h1>
        <p class="small">Generated from XML</p>

        <!-- Таблица -->
        <table class="albums">
          <thead>
            <tr>
              <th>Title</th>
              <th>Artists</th>
              <th>Genres</th>
              <th>Release date</th>
              <th>Age limit</th>
              <th>Tracks (title — duration)</th>
            </tr>
          </thead>
          <tbody>
            <!-- Проходим по всем album -->
            <xsl:for-each select="albums/album">
              <tr class="album-row">
                <td><xsl:value-of select="title"/></td>

                <!-- artists: перечислить через запятую -->
                <td>
                  <xsl:for-each select="artists/artist">
                    <xsl:value-of select="."/>
                    <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
                  </xsl:for-each>
                </td>

                <!-- genres -->
                <td>
                  <xsl:for-each select="genres/genre">
                    <xsl:value-of select="."/>
                    <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
                  </xsl:for-each>
                </td>

                <td><xsl:value-of select="releaseDate"/></td>
                <td><xsl:value-of select="ageLimit"/></td>

                <!-- tracks: вложенный список -->
                <td>
                  <ul class="tracks-list">
                    <xsl:for-each select="tracks/track">
                      <li>
                        <xsl:value-of select="title"/>
                        <xsl:text> — </xsl:text>
                        <xsl:value-of select="duration"/>
                      </li>
                    </xsl:for-each>
                  </ul>
                </td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
