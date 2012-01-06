#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#Simple cue files parser
#
#To use call function parse(cue_file_pointer)
#
#@author: Daenoor <da3n00r@gmail.com>
#@version: 1.0
#@type module
 
import string

##
#Split line of cue file into parts
#@param line Line to split
#@return list of parts 
def _split(line):
  fields = []
  field = ""
  quote = False
  
  for i in range(0, len(line)):
    ch = line[i]
    if ch in string.whitespace:
      if quote:
        field += ch
      elif field:
        fields.append(field)
        field = ""
    elif ch == '"':
      if quote:
        if i+1 < len(line) and line[i+1] == '"':
          i += 1
          field += ch
        else:
          quote = False
      elif not field:
        quote = True
      else:
        field += ch
    else:
      field += ch
  if field:
    fields.append(field)
  
  return fields

##
#Splits cue into two parts: information about disk
#and information about tracks
#@param file: cue file pointer to parse
#@return: two lists with cue parts 
def getDiskInfo(cue_fp):
  disk = []
  tracks = []
  diskScope = True
  for line in cue_fp:
    if line.find("TRACK") > 0:
      diskScope = False
      tracks.append(line.strip())
    else:
      if diskScope:
        disk.append(line.strip())
      else:
        tracks.append(line.strip())
  return [disk, tracks]

##
#Parses cue file
#@param file: cue file pointer
#@return: dictionary with cue information    
def parse(cue_fp):
  cue = {}
  cue['tracks'] = []
  
  [disk, tracks] = getDiskInfo(cue_fp)
  for line in disk:
    fields = _split(line)
    param = fields[0].upper()
    if len(fields)>1:
      if param == "PERFORMER":
        cue['album_artist'] = fields[1]
      elif param == "TITLE":
        cue['album'] = fields[1]
      elif param == "FILE":
        cue['file'] = fields[1]
      elif param == "CATALOG":
        cue['catalog'] = fields[1]
      elif param == "REM":
        if len(fields)>2:
          cue[fields[1].lower()] = ' '.join(fields[2:])
  track = {}
  for line in tracks:
    fields = _split(line)
    param = fields[0].upper()
    if len(fields)>1:
      if param == "TRACK":
        if len(track):
          cue['tracks'].append(track)
        track = {}
        track['number'] = fields[1]
      elif param == "TITLE":
        track['title'] = fields[1]
      elif param == "PERFORMER":
        track['artist'] = fields[1]
  if len(track):
    cue['tracks'].append(track)
  return cue

