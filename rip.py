import os
import subprocess
import json

import discid
import musicbrainzngs as mb

import config

# Read the disc ID
disc = discid.read()

# Get disc info from Musicbrainz
mb.set_useragent("jrip", "0.01", "http://jasongullickson.com")
releases = mb.get_releases_by_discid(disc.id, includes=["recordings","artists"])

# Select the first release
release = releases['disc']['release-list'][0]
id = release['id']
title = release['title']

# Select the first artist
artist = release["artist-credit"][0]["artist"]["name"]


# Create the directory structure
wav_output_dir = f"{config.WAV_PATH}/{artist}/{title}"
os.makedirs(wav_output_dir, exist_ok=True)

# Save all the metadata
with open(f"{wav_output_dir}/metadata.json", "w") as f:
    json.dump(releases, f, sort_keys=True, indent=2)


# Get tracks
tracks = release["medium-list"][0]["track-list"]

# Rip!
for track in tracks:
    track_number = track["number"]
    track_title = track["recording"]["title"]
    track_filename = f"{track_number}_{track_title}.wav"

    print(f"Ripping {track_filename}")

    # rip the track
    rip_result = subprocess.run(["/usr/bin/cdparanoia", "-q", track_number, f"{wav_output_dir}/{track_filename}"])

    print(rip_result)
