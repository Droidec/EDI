# EDI

`EDI` (pronounced 'Ee-Dee' [ˈiːdiː]) is my personal Discord Bot.  
Its name is taken from the [Mass Effect](https://masseffect.fandom.com/wiki/EDI) universe.

## Dependencies

- [python3](https://www.python.org/) >= 3.11: High-level programming language
- [py-cord](https://docs.pycord.dev) >= 2.4.0: Python API wrapper for Discord

## Usage

From the command line, simply call the `edi.py` file as follows:

```cmd
python3 edi.py <json_configuration_file>
```

## JSON configuration file

`EDI` needs a JSON configuration file to start:

```json
{
    "LOG_LEVEL": "The log level to use at startup: INFO, DEBUG, ERROR...",
    "BOT_TOKEN": "The Discord bot token goes here"
}
```

## Commands

`EDI` uses slash commands.

### Basic commands

Theses commands are loaded by `EDI` in any circumstances.

| Command | Description                                | Usage    |
| ------- | ------------------------------------------ | -------- |
| hello   | Say hello to EDI                           | /hello   |
| help    | View basic help and information about EDI  | /help    |
| test    | For development purpose only (owner only)  | /test    |
| version | View EDI running version                   | /version |

### Fun commands (extension)

Theses commands are used to play with `EDI`.

| Command | Description   | Usage                 | Example                     |
| ------- | ------------- | --------------------- | --------------------------- |
| roll    | Roll the dice | /roll <sides> <count> | /roll `sides:d6` `count:5`  |
