# EDI

`EDI` (pronounced 'Ee-Dee' [ˈiːdiː]) is my personal Discord Bot.  
Its name and its personality is taken from the [Mass Effect](https://masseffect.fandom.com/wiki/EDI) universe.

## Dependencies

- [python3](https://www.python.org/) >= 3.6 : Use python3 instead of python2
- [discord.py](https://discordpy.readthedocs.io/en/stable) >= 1.7.3 : API wrapper for Discord
- [PyNaCl](https://pypi.org/project/PyNaCl/) >= 1.5.0 : Python binding for [libsodium](https://github.com/jedisct1/libsodium)
- [ffmpeg](https://www.ffmpeg.org/)

## Usage

From the command line, simply call the `EDI.py` file as follows:

```cmd
python3 EDI.py <token>
```

## Commands

List of bot commands with `!` prefix

### Basic commands

| Command          | Description                                        | Usage        | Example       |
| ---------------- | -------------------------------------------------- | ------------ | ------------- |
| hello &#124; hey | Mention and greet user                             | !hello       |               |
| roll &#124; dice | Roll some dice (1d6, 2d12, ...) and sum the result | !roll [expr] | !roll 2d6 + 5 |

### Voice commands

| Command | Description                                          | Usage           | Example       |
| ------- | ---------------------------------------------------- | --------------- | ------------- |
| join    | Join a voice channel<br />(channel name is optional) | !join [channel] | !join General |
| leave   | Leave a voice channel                                | !leave          |               |
