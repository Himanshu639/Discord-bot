# Clicker -  The Discord Bot

Welcome to the Clicker Discord Bot! This bot allows you to play music in voice channels of any Discord server. It utilizes Python modules and APIs to get working which are listed below. I have added features for an enhanced music experience.

## About 

This my First Discord Bot Project which is a music bot. I wanted to create a bot that enhances the music experience within Discord servers. With this bot, you can seamlessly play music in voice channels. I hosted this bot on replit.com which is an online integrated development environment which lets us create online projects called Repls.

## Features

- Play any song in voice channels of Discord servers.
- Fetch song recommendations using the Spotify API.
- Utilize yt-dlp module to retrieve songs from various sources.
- Display synchronized lyrics for the currently playing song.

## Modules/APIs

I required following dependencies to run the bot:

- Python 3.11
- requests - HTTP library for making requests in Python
- [pycord](https://github.com/Pycord-Development/pycord) - Discord API wrapper for Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube-DL fork for downloading videos
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) - Module for searching YouTube videos
- [spotify-api](https://developer.spotify.com/documentation/web-api/) - Spotify Web API for music recommendations
- [synced-lyrics](https://github.com/lo3me/syncedlyrics) - Module for fetching synchronized lyrics

## Setup

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/yourusername/discord-music-bot.git
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure the necessary API keys and tokens for Spotify API and other modules.

4. Run the bot:

   ```
   python bot.py
   ```

## Usage

- `/play <song>` - Play the specified song in the voice channel.
- `/skip` - Skip the currently playing song.
- `/leave` - Stop the music playback and disconnect the bot from the voice channel.
- `/get-lyrics` - Display synchronized lyrics for the currently playing song.
- `/recommendations` - Toggles the recommendation ON or OFF.

## Screenshot

![Screenshot of Bot Commands](https://github.com/Himanshu639/Discord-bot/blob/main/Screenshot%202024-01-28%20205615.png)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Himanshu639/Discord-bot/blob/main/LICENSE.md) file for details.
