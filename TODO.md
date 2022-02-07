# TODO

- Case insensitivity for `join` command
- Implement tracks queue for `CogVoice` (see local voice_bot source code)
- Integrate plexapi with a new `CogPlex` (async?) that inherits from `CogVoice` with bot.get_cog() with the following subcommands (see `commands.group`):
    - !plex list [section] [page] : Consult album names by section with pages
    - !plex search [section] [keyword] : Search album by keyword in a section
    - !plex info [section] [album] : Get album info in a Discord embed (see !embed)
    - !plex play [section] [album] : Play album tracks
N.B. For `section`, map user section with real section name (to avoid spaces)
