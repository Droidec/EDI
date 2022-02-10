# TODO

- Case insensitivity for `join` command
- Implement tracks queue for `CogVoice` (see local voice_bot source code)
- Integrate plexapi with a new `CogPlex` (async?) that inherits from `CogVoice` with bot.get_cog() with the following subcommands (see `commands.group`):
    - !plex list [section] [page] : Consult album names by section with pages
    - !plex search [section] [keyword] : Search album by keyword in a section
    - !plex info [section] [album] : Get album info in a Discord embed (see !embed)
    - !plex play [section] [album] : Play album tracks
N.B. For `section`, map user section with real section name (to avoid spaces)
- Test if bot.plex is None in `plex` command to deactivate subcommands if plexapi is not installed/initialized ?
- Implement the following commands for the voice player:
    - loop : To loop on a track
    - volume : to manage volume
    - clear : clear the queue but continue to play
    - remove : To remove a track at a specific position in the queue
- Fix warning that appear after 1 minute of inactivity in a voice channel
- Truncate each track ex. data[:30] + '...' if len(data) > 30 else data
- Try to search albums by key instead with plexapi
- Format duration to %H:%M:%S of a track if superior to 59 min 59 sec
- Truncate tracks names to avoid 1000 limit in embed fields
- When album info is displayed, set tracks in inline fields and limit the number of fields to avoid 6000 limit of embed
