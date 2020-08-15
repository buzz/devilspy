# devilspy

devilspy is a window matching utility, allowing the user to perform
actions on windows as they are created.

It draws inspiration from [Devilspie2](https://www.nongnu.org/devilspie2/) which
unfortunately is unmaintained.

The idea is to automate actions on windows, like *Always have my browser on
workspace 3* and *The IRC client I want to have maximized*, and so on. To
achieve this every new window that is created will be tested against a set of
rules. If one rule matches a number of custom actions are performed.

## Installation

Clone this repository.

```
$ ./setup.py install
```

Or, even better, use the [AUR package](TODO) if you're on Arch Linux.

## Usage

Start devilspy on the command line to identify new windows.

```
$ devilspy --print-window-info
```

Usually you want to start devilspy in the background with your login session
once you have your rules setup. Use *Startup applications*, *Autostart* or
similar, depending on your Desktop Environment.

```
$ devilspy --fork
```

## Configuration

devilspy takes a declarative approach to configuration. Create a config file
`~/.config/devilspy/config.yml` in the following form.

```yaml
KEY:
  match:
    MATCHER: [...]
    [...]
  actions:
    ACTION: [...]
    [...]
[...]
```

`KEY` is an arbitrary name for the entry. Every entry can have a number of
matchers and actions.

### Example config

```yaml
browser:
  match:
    class_group_name:
      - Chromium
      - firefox
  actions:
    workspace: 2
    activate_workspace: 2
irc:
  match:
    class_group_name: Hexchat
  actions:
    maximize: true
```

## License

GNU General Public License v2.0
