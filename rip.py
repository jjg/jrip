import subprocess

import discid
import musicbrainzngs as mb

mb.set_useragent("jrip", "0.01", "http://jasongullickson.com")

disc = discid.read()

releases = mb.get_releases_by_discid(disc.id, includes=["recordings","artists"])

# select the first one
release = releases['disc']['release-list'][0]
id = release['id']
artist = release["artist-credit"][0]["artist"]["name"]
title = release['title']

print(f"{title} by {artist}")

# Get tracks
tracks = release["medium-list"][0]["track-list"]

for track in tracks:
    track_number = track["number"]
    track_title = track["recording"]["title"]

    print(f"{track_number} - {track_title}")

    # rip the track: cdparanoia -q 1 track-name
    rip_result = subprocess.run(["/usr/bin/cdparanoia", "-q", track_number, f"{track_title}.wav"])

    print(rip_result)
