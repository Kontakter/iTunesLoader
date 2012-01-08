#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cue_parser
from util import run, remove_file

import os
import string
import optparse

LOCATION = os.path.dirname(os.path.realpath(__file__))
ADD_SONG = os.path.join(LOCATION, "upload_file_to_itunes.applescript")
SET_TAG = os.path.join(LOCATION, "set_tags_to_last_song.applescript")

AUDIO_EXT = ["flac", "m4a", "mp3", "ape", "wav", "aiff"]
PLAYLIST_EXT = ["cue", "pls", "m3u"]

class Cue(object):
    # TODO: exclude using of audiotools
    def __init__(self, filename):
        self.filename = filename
        cue = cue_parser.parse(filename)
        self.artist = cue["disk_info"].get("PERFORMER", "")
        self.album = cue["disk_info"].get("TITLE", "")
        self.genre = cue["disk_info"].get("REM", {}).get("GENRE", "")
        self.year = cue["disk_info"].get("REM", {}).get("DATE", "")
        self.track_count = len(cue["tracks"])
        self.tracks = [cue["tracks"][i].get("TITLE", "") for i in xrange(self.track_count)]

    def find_track(self, name):
        if name[0] in string.digits and name[1] in string.digits:
            num = int(name[0:2])
            return (num, self.tracks[num - 1])
        else:
            f = self.tracks.find(name)
            if f != -1:
                return (f + 1, self.tracks[f])
            else:
                raise Exception("Cannot find description of file %s in cue" % name)

    def getname(self, name):
        return self.find_track(name)[1]
    
    def track_index(self, name):
        return self.find_track(name)[0]

class Enter(object):
    def __init__(self, old_path, new_path):
        self.old_path = os.path.abspath(old_path)
        print "Processing " + new_path + " ..."
        os.chdir(new_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_path)

def extract_extension(name):
    basename, extension = os.path.splitext(name)
    return extension[1:].lower()

def walk_audiofiles(top):
    extensions = AUDIO_EXT + PLAYLIST_EXT
    for root, dirs, files in os.walk(top):
        audio_files = [f for f in files if extract_extension(f) in extensions]
        yield os.path.abspath(root), audio_files

def process_dir(files, only_add, delete, ignore_cue):
    def add_file_to_itunes(filename, cue=None):
        filename = os.path.abspath(filename)
        print "Adding file %s to iTunes" % filename
        run("osascript %s '%s'" % (ADD_SONG, filename))
        if cue is not None:
            name = os.path.splitext(os.path.basename(filename))[0]
            run('osascript %(bin)s '
                '"%(track)s" "%(artist)s" "%(album)s" "%(genre)s" "%(name)s" "%(track_count)d" "%(track_index)d" "%(year)s"' %
                {"bin": SET_TAG,
                 "track": name,
                 "artist": cue.artist,
                 "album": cue.album,
                 "genre": getattr(cue, "genre", ""),
                 "name": cue.getname(name),
                 "track_count": cue.track_count,
                 "track_index": cue.track_index(name),
                 "year": cue.year})

    extensions = [extract_extension(f) for f in files]
    audio_files = filter(lambda f: extract_extension(f) in AUDIO_EXT, files)
    audio_ext = set(filter(AUDIO_EXT.__contains__, extensions))
    playlist_ext = filter(PLAYLIST_EXT.__contains__, extensions)
    if len(audio_ext) != 1:
        print "Error: directory with target files must contain "\
              "only one type of audio files, there are %s." % str(audio_ext)
        return

    cue = None
    files_to_add = []
    if "cue" in playlist_ext and not ignore_cue:
        if playlist_ext.count("cue") > 1:
            print "Error: more than one cue files, ignoring this path."
            return

        cue = Cue(filter(lambda x: extract_extension(x) == "cue", files)[0])
        if len(audio_files) != cue.track_count and len(audio_files) != 1:
            print "Error: number of audio files differ from number of tracks, "\
                  "ignoring this path, %d %d " % (len(audio_files), cue.track_count)
            return

        if len(audio_files) == 1:
            if extract_extension(audio_files[0]) not in ["flac", "ape", "wav"]:
                print "Error: wrong extension %s. It is not supported with cue. "\
                      "Ignoring this path."
                return
            run("xld -c \"%s\" -f wav \"%s\"" % (cue.filename, audio_files[0]))
            if delete:
                remove_file(audio_files[0])
            audio_files = [f for f in os.listdir(".") if extract_extension(f) == "wav"]

    for f in audio_files:
        if extract_extension(f) in ["mp3", "m4a"]:
            files_to_add.append(f)
        elif not only_add:
            basename, _ = os.path.splitext(f)
            target_file = basename + ".m4a"
            run("ffmpeg -i \"%s\" -acodec alac \"%s\"" % (f, target_file))
            files_to_add.append(target_file)
            if delete:
                remove_file(f)

    for f in files_to_add:
        add_file_to_itunes(f, cue)
    #if delete and cue is not None:
    #    remove_file(cue.filename)

if __name__ == "__main__":
    parser = optparse.OptionParser(
        description="Convert audio and add to iTunes."
                    "Supported formats: flac, m4a, mp3, ape."
                    "Also cue playlists are supported."
                    "There is one required parametr: path to folder with album")
    parser.add_option("--delete,-d", action="store_true", dest="delete", default=False,
                      help="Set this option for deletion old file in conversion case.")
    parser.add_option("--only-add, -o", dest="only_add",
                      action="store_true", default=False,
                      help="Add all mp3 and m4a files.")
    parser.add_option("--ignore-cue, -i", dest="ignore_cue",
                      action="store_true", default=False,
                      help="Ignore all cue files.")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        exit()

    options.path = os.path.abspath(args[0])
    for path, files in walk_audiofiles(options.path):
        with Enter(options.path, path) as _:
            if not files:
                print "Directory doesn't contain supported formats."
                continue
            process_dir(files, options.only_add, options.delete, options.ignore_cue)
