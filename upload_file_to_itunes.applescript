on run audio_file
    tell application "iTunes"
        launch
        set mac_audio_file to audio_file as POSIX file
        add mac_audio_file
    end tell
end run
