import json
import os
import random
from jsonpath_ng import parse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(BASE_DIR, "out", "albums.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def a_albums_by_genre(data, genre):
    expr = parse("$[*]")
    return [a.value["title"] for a in expr.find(data) if genre in a.value.get("genres", [])]

def b_genres_by_artist(data, artist):
    expr = parse("$[*]")
    genres = set(
        g
        for album in expr.find(data)
        if artist in album.value.get("artists", [])
        for g in album.value.get("genres", [])
    )
    return sorted(genres)

def parse_duration(dur_str):
    mins, secs = map(int, dur_str.split(":"))
    return mins * 60 + secs

def c_albums_with_tracks_over_5min(data):
    expr = parse("$[*]")
    result = []
    for album in expr.find(data):
        tracks = album.value.get("tracks", [])
        if any(parse_duration(t["duration"]) > 300 for t in tracks):
            result.append(album.value["title"])
    return result

def d_random_playlist(data, n):
    expr = parse("$[*].tracks[*]")
    all_tracks = [t.value for t in expr.find(data)]
    return random.sample(all_tracks, min(n, len(all_tracks)))

def e_counts_per_album(data):
    expr = parse("$[*]")
    out = []
    for album in expr.find(data):
        title = album.value["title"]
        genre_count = len(album.value.get("genres", []))
        track_count = len(album.value.get("tracks", []))
        out.append((title, genre_count, track_count))
    return out

def main():
    data = load_json(JSON_PATH)
    print("JSON loaded:", JSON_PATH)

    # a)
    genre = "Alternative Rock"
    albums_genre = a_albums_by_genre(data, genre)
    print(f"\n(a) Альбомы жанра '{genre}':")
    for t in albums_genre:
        print(" -", t)

    # b)
    artist = "Radiohead"
    genres = b_genres_by_artist(data, artist)
    print(f"\n(b) Жанры, в которых работал исполнитель '{artist}':")
    for g in genres:
        print(" -", g)

    # c)
    long_albums = c_albums_with_tracks_over_5min(data)
    print("\n(c) Альбомы с треками длиннее 5 минут:")
    for a in long_albums:
        print(" -", a)

    # d)
    N = 5
    playlist = d_random_playlist(data, N)
    print(f"\n(d) Случайный плейлист из {N} композиций:")
    for t in playlist:
        print(f" - {t['title']} ({t['duration']}) — из '{t.get('album','Unknown Album')}'")

    # e)
    counts = e_counts_per_album(data)
    print("\n(e) Для каждого альбома: (название, число жанров, число треков):")
    for title, gcount, tcount in counts:
        print(f" - {title}: genres={gcount}, tracks={tcount}")

if __name__ == "__main__":
    main()
