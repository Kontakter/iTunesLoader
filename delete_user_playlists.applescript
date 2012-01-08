tell application "iTunes"
    set shift to 0
    repeat with i from 1 to count of playlists
        if i - shift > (count of playlists) then
            exit repeat
        end if
        set p to playlist (i - shift)
        if special kind of p is none then
            delete p
            set shift to shift + 1
        end if
    end repeat
end tell
