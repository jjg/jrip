import os
import subprocess
import json

import discid
import musicbrainzngs as mb

import config

# Escape the metadata to meet ffmpeg's requirements
def ff_escape(s):
    s.replace("=", "\=")
    s.replace(";", "\;")
    s.replace("#", "\#")
    s.replace("\\", "\\\\")
    s.replace("\n", "\\\n")
    s.replace(" ", "\ ")
    return s


# Read the disc ID
disc = discid.read()

# Get disc info from Musicbrainz
mb.set_useragent("jrip", "0.01", "http://jasongullickson.com")
releases = mb.get_releases_by_discid(disc.id, includes=["recordings","artists"])

# If there's more than one release or artist guess that the first
# one is best (we'll save all the metadata to a file in case
# we change our minds later).
release = releases['disc']['release-list'][0]
artist = release["artist-credit"][0]["artist"]["name"]
title = release['title']

# Create the output directories
# TODO: This should be dynamic, based on output formats 
# specified in the config file
wav_output_dir = f"{config.WAV_PATH}/{artist}/{title}"
mp3_output_dir = f"{config.MP3_PATH}/{artist}/{title}"
os.makedirs(wav_output_dir, exist_ok=True)
os.makedirs(mp3_output_dir, exist_ok=True)

# Save all the metadata
with open(f"{wav_output_dir}/metadata.json", "w") as f:
    json.dump(releases, f, sort_keys=True, indent=2)

# TODO: Get the album art

# Process the tracks
tracks = release["medium-list"][0]["track-list"]
for track in tracks:
    track_number = track["number"]
    track_title = track["recording"]["title"]
    track_filename = f"{track_number}_{track_title}"

    # Create ffmpeg metadata file
    # TODO: Add more metadata to this file
    track_metadata_filename = f"{wav_output_dir}/{track_filename}.txt"
    with open(track_metadata_filename, "w") as mf:
        mf.write(";FFMETADATA1\n")
        mf.write(f"title={ff_escape(track_title)}\n")
        mf.write(f"artist={ff_escape(artist)}\n")
        mf.write(f"album={ff_escape(title)}\n")

    # Rip 
    print(f"Ripping {track_filename}")
    rip_result = subprocess.run([
        "/usr/bin/cdparanoia", 
        "-q", 
        track_number, 
        f"{wav_output_dir}/{track_filename}.wav"
    ], check=True)

    # Encode
    print(f"Encoding {track_filename}")

    # For now we'll encode one track at a time, but we could do this
    # separately and in parallel if we wanted to

    # TODO: Encode to a dynamic number of formats defined
    # in the config file
    # TODO: Add the album art to the encoded file
    # TODO: Encode to FLAC
    # TODO: Suppress or re-route ffmpeg's text output
    # TODO: Don't prompt if file exists, just overwrite it
    mp3_encode_result = subprocess.run([
        "/usr/bin/ffmpeg",
        "-i",
        f"{wav_output_dir}/{track_filename}.wav",
        "-i",
        f"{track_metadata_filename}",
        "-map_metadata",
        "1",
        "-write_id3v2",
        "3",
        "-write_id3v1",
        "1",
        "-b:a",
        "320k",
        "-f",
        "mp3",
        f"{mp3_output_dir}/{track_filename}.mp3"
    ], check=True)

# TODO: Handle exceptions and provide useful feedback
print("All done!")
