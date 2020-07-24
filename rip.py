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
mp3_output_dir = f"{config.MP3_PATH}/{artist}/{title}"
os.makedirs(wav_output_dir, exist_ok=True)
os.makedirs(mp3_output_dir, exist_ok=True)

# Save all the metadata
with open(f"{wav_output_dir}/metadata.json", "w") as f:
    json.dump(releases, f, sort_keys=True, indent=2)



# Get tracks
tracks = release["medium-list"][0]["track-list"]

# Rip!
for track in tracks:
    track_number = track["number"]
    track_title = track["recording"]["title"]
    track_filename = f"{track_number}_{track_title}"

    print(f"Ripping {track_filename}")

    # Create ffmpeg metadata file
    track_metadata_filename = f"{wav_output_dir}/{track_filename}.txt"
    with open(track_metadata_filename, "w") as mf:
        mf.write(f"title={track_title}\n")
        mf.write(f"artist={artist}\n")
        mf.write(f"album={title}\n")
        mf.close()

    # rip the track
    rip_result = subprocess.run([
        "/usr/bin/cdparanoia", 
        "-q", 
        track_number, 
        f"{wav_output_dir}/{track_filename}.wav"
    ])

    # TODO: Handle failures gracefully (rip_result.returncode?)

    # Encode
    print(f"Encoding {track_filename}")

    # For now we'll encode one track at a time, but we could do this
    # separately and in parallel if we wanted to

    # ffmpeg -i track.wav -b:a 320k -metadata title="foo" -metadata artist="bar" -metadata album="baz" track.mp3
    mp3_encode_result = subprocess.run([
        "/usr/bin/ffmpeg",
        "-i",
        f"{wav_output_dir}/{track_filename}.wav",
        "-i",
        f"{track_metadata_filename}",
        "-map_metadata",
        "1",
        "-write_id3v2",
        "1",
        "-b:a",
        "320k",
        "-f",
        "mp3",
        f"{mp3_output_dir}/{track_filename}.mp3"
    ])

    # full list of metadata fields: title, comment, description, artist, album_artist, album, date, track (x/y), disc (x/y), genre, composer, producer, publisher, copyright
    # https://gist.github.com/eyecatchup/0757b3d8b989fe433979db2ea7d95a01
