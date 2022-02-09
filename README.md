# EDI

`EDI` (pronounced 'Ee-Dee' [ˈiːdiː]) is my personal Discord Bot.  
Its name and its personality is taken from the [Mass Effect](https://masseffect.fandom.com/wiki/EDI) universe.

## Dependencies

- [python3](https://www.python.org/) >= 3.9 : Use python3 instead of python2
- [async-timeout](https://pypi.org/project/async-timeout/) >= 3.0.1 : Asyncio-compatible timeout context manager
- [discord.py](https://discordpy.readthedocs.io/en/stable) >= 1.7.3 : API wrapper for Discord
- [PyNaCl](https://pypi.org/project/PyNaCl/) >= 1.5.0 : Python binding for [libsodium](https://github.com/jedisct1/libsodium)
- [plexapi](https://pypi.org/project/PlexAPI/) >= 4.9.1 : API wrapper for PleX Servers
- [colorthief](https://github.com/fengsp/color-thief-py) >= 0.2.1 : A Python module for grabbing the color palette from an image
- [ffmpeg](https://www.ffmpeg.org/) : Collection of audio and video decoders/encoders

## Usage

From the command line, simply call the `EDI.py` file as follows:

```cmd
python3 EDI.py <PleX Server base URL> <PleX account token> <Discord bot token>
```

## Commands

List of bot commands with `!` prefix

### Basic commands

| Command          | Description                                        | Usage        | Example       |
| ---------------- | -------------------------------------------------- | ------------ | ------------- |
| hello &#124; hey | Mention and greet user                             | !hello       |               |
| roll &#124; dice | Roll some dice (1d6, 2d12, ...) and sum the result | !roll [expr] | !roll 2d6 + 5 |

### Voice commands

| Command | Description                      | Usage           | Example                                  |
| ------- | -------------------------------- | --------------- | ---------------------------------------- |
| join    | Join a voice channel             | !join [channel] | !join General                            |
| play    | Play audio from local filesystem | !play \<path\>  | !play C:\Users\derov\Downloads\input.mp3 |
| pause   | Pause audio                      | !pause          |                                          |
| resume  | Resume audio                     | !resume         |                                          |
| stop    | Stop audio                       | !stop           |                                          |
| leave   | Leave a voice channel            | !leave          |                                          |

### PleX Server group commands

| Subcommand | Description                 | Usage                                | Example                   |
| ---------- | --------------------------- | ------------------------------------ | ------------------------- |
| list       | List album names by section | !plex list \<section\> [page]        | !plex list Games 5        |
| search     | Search album by keyword     | !plex search \<section\> \<keyword\> | !plex search Games Hitman |
| info       | Consult album info          | !plex info \<section\> \<album\>     | !plex info Games Abzû     |
