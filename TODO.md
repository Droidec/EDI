# TODO

- Case insensitivity for `join` command
- Test if bot.plex is None in `plex` command to deactivate subcommands if plexapi is not installed/initialized ?
- Implement the following commands for the voice player:
    - loop : To loop on a track
    - skip multiple tracks at once
    - remove : To remove a track at a specific position in the queue
- Fix warning that appear after 1 minute of inactivity in a voice channel
- Truncate each track ex. data[:30] + '...' if len(data) > 30 else data
- Try to search albums by key instead with plexapi
- Format duration to %H:%M:%S of a track if superior to 59 min 59 sec
- Truncate tracks names to avoid 1000 limit in embed fields
- When album info is displayed, set tracks in inline fields and limit the number of fields to avoid 6000 limit of embed
