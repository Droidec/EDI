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
    "BOT_TOKEN": "The Discord bot token here"
}
```

## Commands

`EDI` uses slash commands.

### Basic commands

| Command | Description              | Usage  | Example |
| ------- | ------------------------ | ------ | ------- |
| hello   | Mentions and greets user | /hello |         |
