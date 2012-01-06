on run args
    set filename to (item 1 of args)
    set artist_name to (item 2 of args)
    set album_name to (item 3 of args)
    set genre_name to (item 4 of args)
    set track_name to (item 5 of args)
    set track_count to (item 6 of args)
    set track_index to (item 7 of args)
    tell application "iTunes"
        set oldfi to fixed indexing
        set fixed indexing to true
        set t to last file track
        set artist of t to artist_name
        set album of t to album_name
        set name of t to track_name
        set genre of t to genre_name
        set track count of t to track_count
        set track number of t to track_index
        set fixed indexing to oldfi
    end tell
end run
