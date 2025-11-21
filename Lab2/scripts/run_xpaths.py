#!/usr/bin/env python3
# run_xpaths.py
# Пример выполнения XPath-запросов для файлов lab2/albums.xml

import os
import random
from lxml import etree

# Путь к XML (предполагаем, что запускаем из lab2/)
BASE = os.path.dirname(os.path.dirname(__file__))  # lab2
XML_PATH = os.path.join(BASE, "albums.xml")

def parse_xml(path):
    tree = etree.parse(path)
    return tree

def a_albums_by_genre(tree, genre):
    expr = f'//album[genres/genre = "{genre}"]/title/text()'
    return tree.xpath(expr)

def b_genres_by_artist(tree, artist):
    expr = f'//album[artists/artist = "{artist}"]/genres/genre/text()'
    return tree.xpath(expr)

def c_albums_with_tracks_over_5min(tree):
    # Надежный способ: пройти по каждому альбому и проверять durations в Python.
    albums = tree.xpath('//album')
    result = []
    for a in albums:
        title = a.xpath('title/text()')[0]
        tracks = a.xpath('tracks/track/duration/text()')
        for d in tracks:
            # d формат "M:SS" или "MM:SS"
            try:
                mins, secs = d.split(":")
                mins_i = int(mins)
                secs_i = int(secs)
            except Exception:
                continue
            total_seconds = mins_i * 60 + secs_i
            if total_seconds > 5 * 60:
                result.append(title)
                break
    return result

def d_random_playlist(tree, n):
    # Получаем все треки как (album_title, track_title, duration)
    tracks = []
    albums = tree.xpath('//album')
    for a in albums:
        album_title = a.xpath('title/text()')[0]
        for t in a.xpath('tracks/track'):
            t_title = t.xpath('title/text()')[0]
            t_dur = t.xpath('duration/text()')[0]
            tracks.append({"album": album_title, "title": t_title, "duration": t_dur})
    if n >= len(tracks):
        return tracks
    return random.sample(tracks, n)

def e_counts_per_album(tree):
    albums = tree.xpath('//album')
    out = []
    for a in albums:
        title = a.xpath('title/text()')[0]
        genre_count = a.xpath('count(genres/genre)')
        track_count = a.xpath('count(tracks/track)')
        # xpath count returns float - convert to int
        out.append((title, int(genre_count), int(track_count)))
    return out

def main():
    tree = parse_xml(XML_PATH)
    print("XML parsed:", XML_PATH)

    # a)
    genre = "Alternative Rock"
    albums_genre = a_albums_by_genre(tree, genre)
    print(f"\n(a) Альбомы жанра '{genre}':")
    for t in albums_genre:
        print(" -", t)

    # b)
    artist = "Radiohead"
    genres = b_genres_by_artist(tree, artist)
    # unique
    genres_unique = sorted(set(genres))
    print(f"\n(b) Жанры, в которых работал исполнитель '{artist}':")
    for g in genres_unique:
        print(" -", g)

    # c)
    long_albums = c_albums_with_tracks_over_5min(tree)
    print("\n(c) Альбомы с треками длиннее 5 минут:")
    for a in long_albums:
        print(" -", a)

    # d)
    N = 5
    playlist = d_random_playlist(tree, N)
    print(f"\n(d) Случайный плейлист из {N} композиций:")
    for t in playlist:
        print(f" - {t['title']} ({t['duration']}) — из '{t['album']}'")

    # e)
    counts = e_counts_per_album(tree)
    print("\n(e) Для каждого альбома: (название, число жанров, число треков):")
    for title, gcount, tcount in counts:
        print(f" - {title}: genres={gcount}, tracks={tcount}")

if __name__ == "__main__":
    main()
