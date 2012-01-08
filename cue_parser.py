#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Parse cue sheet according to http://digitalx.org/cue-sheet/syntax/
# Also module ignore empty lines and strip spaces and quotes.
# Pregaps, postgaps, index, FILE and ISRC are parsed as strings.
# Author: Kolesnichenko Ignat, email: ignat1990@gmail.com

from util import run

import os
import string
import shutil
import itertools

def _parse_block(lines, keywords, process_rem_comment):
    comment = "REM"
    strip_symbols = " \"'"
    keyword_dict = {}
    for line in lines:
        if not line: continue
        keyword, value = line.split(" ", 1)
        value = value.strip(strip_symbols)
        # Case of comment
        if keyword == comment:
            if not process_rem_comment: continue
            if "REM" not in keyword_dict:
                keyword_dict["REM"] = {}
            ok = False
            if len(value.split()) > 1:
                k, v = value.split(" ", 1)
                if all(c in string.ascii_uppercase for c in k):
                    keyword_dict["REM"][k] = v.strip(strip_symbols)
                    ok = True
            if not ok:
                if None not in keyword_dict["REM"]:
                    keyword_dict["REM"][None] = []
                keyword_dict["REM"][None].append(value)
        # Case of unknown keyword
        elif keyword not in keywords:
            print "Warning: cannot parse line '%s'" % line
        else:
            if keyword in keyword_dict:
                keyword_dict[keyword] = [keyword_dict[keyword], value]
            else:
                keyword_dict[keyword] = value
    return keyword_dict

def _parse_stream(cue_stream):

    track_keyword = "TRACK"
    disk_keywords = ["PERFORMER", "TITLE", "CATALOG",
                     "CDTEXTFILE", "FILE", "SONGWRITER"]
    track_keywords = ["PERFORMER", "TITLE", "TRACK", "INDEX",
                      "FLAGS", "ISRC", "PREGAP", "POSTGAP"]

    cue = {}
    lines = [line.strip() for line in cue_stream]
    
    # Splits cue file on lines about tracks and lines about disk.
    # It is supposed that cue sheet contains only one FILE field
    pred = lambda line: line.find(track_keyword) == -1
    disk_info = list(itertools.takewhile(pred, lines))

    cue["disk_info"] = _parse_block(disk_info, disk_keywords, True)
    
    cue["tracks"] = []
    while True:
        lines = list(itertools.dropwhile(pred, lines))
        if not lines: break
        track_block = [lines[0]]
        lines = lines[1:]
        track_block += list(itertools.takewhile(pred, lines))
        cue["tracks"].append(_parse_block(track_block, track_keywords, False))

    # Some handmade fixes
    for track in cue["tracks"]:
        number, track_type = track["TRACK"].split()
        track["number"] = int(number)
        track["type"] = track_type
        del track["TRACK"]

    return cue


def parse(filename):
    def detect_charset(filename):
        stdout = run("file -I '%s'" % filename, True)
        line = stdout.split("\n")[0]
        index = line.find("charset")
        if index == -1:
            return None
        return line[index:].split("=")[1].split()[0].strip(";")

    def decode(filename, input_charset, output_charset):
        tempfile = "/tmp/.iTunesLoader"
        name, ext = os.path.splitext(filename)
        run("iconv -f '%s' -t '%s' '%s' > '%s'" % (input_charset, output_charset, filename, tempfile))
        shutil.move(tempfile, filename)

    charset = detect_charset(filename)
    if charset is not None and charset != "utf-8" and charset != "us-ascii" and charset != "ascii":
        decode(filename, charset, "utf-8")
    
    with open(filename) as f:
        cue = _parse_stream(f)
    return cue
