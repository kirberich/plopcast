# Plopcast - it plops your podcasts

```
       ___                                            __      
      /\_ \                                          /\ \__   
 _____\//\ \     ___   _____     ___     __      ____\ \ ,_\  
/\ '__`\\ \ \   / __`\/\ '__`\  /'___\ /'__`\   /',__\\ \ \/  
\ \ \L\ \\_\ \_/\ \L\ \ \ \L\ \/\ \__//\ \L\.\_/\__, `\\ \ \_ 
 \ \ ,__//\____\ \____/\ \ ,__/\ \____\ \__/.\_\/\____/ \ \__\
  \ \ \/ \/____/\/___/  \ \ \/  \/____/\/__/\/_/\/___/   \/__/
   \ \_\                 \ \_\                                
    \/_/                  \/_/
```

Plopcast is simple tool for downloading podcasts. It supports

* Downloading from an RSS feed
* Limiting the number of recent episodes to download
* Downloading only new episodes
* Simple templates for setting file name from publishing date, episode title and original filename
* Setting the file modification times to the publishing time of the episode
* dry runs and verbose/quiet output to see what will and won't be downloaded
* Sanitising filenames to make sure they work on Fat32 file systems like MP3 players

## Installation
There's currently no nice user-friendly installation - if anyone is interested in actually using this let me know and I will make the installation easier!

* Clone the repo
* Install python 3.12 or higher
* Install poetry (`pipx install poetry`)
* Run `poetry install` within the project directory
* Run `poetry run plopcast --help` or activate the project's virtualenv and simply run `plopcast --help`

## Usage
```
plopcast \
--url=https://somewhere.url/feed.rss \
--output-dir=/whereever/you/want \
--max-episodes=5 \
--overwrite \
--no-set-modification-time \
--file-prefix-template="{date:%Y-%m-%d %H:%M:%S} {title} {original_prefix}
```

### File name templating
To configure how the downloaded files are named, use `--file-prefix-template` - this lets you specify a string with a number of predefined variables (in curly brackets) to set the filename. The default is `{date:%Y-%m-%d} {title}`, resulting in a filename like `2026-01-10 Episode title.mp3`.

The template only sets the filename excluding the extension, the extension is always taken from the downloaded file.

The available variables that can be used for formatting are:

* `title` - the episode title
* `original_prefix` - the prefix of the podcast mp3 as it was downloaded
* `date` - the episodes publishing date and time. This can be formatted using python string formatting, but in short
  * %Y - Year
  * %m - month
  * %d - day
  * %H - hour
  * %M - minute
  * %S - second
  
### Modification times
If you don't want the files to given a modification time matching the episode publishing date, and instead be the time when the file was downloaded, pass `--no-set-modification-time`

## Excluded features
* Plopcast only ever downloads a single feed - for multiple feeds, simply run the command multiple times, for example from a script or a cronjob
* There is no support for creating playlists, as this is better done with a small separate shell script
