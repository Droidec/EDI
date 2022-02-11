# EDI

`EDI` (pronounced 'Ee-Dee' [ˈiːdiː]) is my personal Discord Bot.  
Its name and its personality is taken from the [Mass Effect](https://masseffect.fandom.com/wiki/EDI) universe.

## Dependencies

- [python3](https://www.python.org/) >= 3.9 : Use python3 instead of python2
- [async-timeout](https://pypi.org/project/async-timeout/) >= 3.0.1 : Asyncio-compatible timeout context manager
- [discord.py](https://discordpy.readthedocs.io/en/stable) >= 1.7.3 : API wrapper for Discord
- [PyNaCl](https://pypi.org/project/PyNaCl/) >= 1.5.0 : Python binding for [libsodium](https://github.com/jedisct1/libsodium)
- [plexapi](https://pypi.org/project/PlexAPI/) >= 4.9.1 : API wrapper for Plex Servers
- [colorthief](https://github.com/fengsp/color-thief-py) >= 0.2.1 : A Python module for grabbing the color palette from an image
- [ffmpeg](https://www.ffmpeg.org/) : Collection of audio and video decoders/encoders

## Usage

From the command line, simply call the `EDI.py` file as follows:

```cmd
python3 EDI.py <Plex Server base URL> <Plex account token> <Discord bot token>
```

## Commands

List of bot commands with `!` prefix

### Basic commands

| Command          | Description                                         | Usage        | Example       |
| ---------------- | --------------------------------------------------- | ------------ | ------------- |
| hello &#124; hey | Mentions and greets user                            | !hello       |               |
| roll &#124; dice | Rolls some dice (1d6, 2d12, ...) and sum the result | !roll [expr] | !roll 2d6 + 5 |

### Voice commands

`EDI` features a voice player to play audio from various sources

| Command | Description                         | Usage           | Example                                  |
| ------- | ----------------------------------- | --------------- | ---------------------------------------- |
| join    | Joins a voice channel               | !join [channel] | !join General                            |
| np      | Shows the current track played      | !np             |                                          |
| queue   | Shows the player queue              | !queue          |                                          |
| volume  | Gets or changes audio/player volume | !volume [vol]   | !volume 50                               |
| pause   | Pauses audio                        | !pause          |                                          |
| resume  | Resumes audio                       | !resume         |                                          |
| skip    | Skips to next track in the queue    | !skip [step]    | !skip 2                                  |
| remove  | Removes specified track from queue  | !remove [pos]   | !remove 5                                |
| clear   | Clears the queue                    | !clear          |                                          |
| stop    | Clears the queue and stops audio    | !stop           |                                          |
| leave   | Leaves voice channel                | !leave          |                                          |

### Plex Server group commands

`EDI` can search/play tracks on my Plex Server with the `plex` command

| Subcommand | Description                   | Usage                                | Example                   |
| ---------- | ----------------------------- | ------------------------------------ | ------------------------- |
| list       | Lists album names by section  | !plex list \<section\> [page]        | !plex list Games 5        |
| search     | Searches album by keyword     | !plex search \<section\> \<keyword\> | !plex search Games Hitman |
| info       | Consults album info           | !plex info \<section\> \<album\>     | !plex info Games Abzû     |
| play       | Add album to the player queue | !plex play \<section\> \<album\>     | !plex play Games Abzû     |
