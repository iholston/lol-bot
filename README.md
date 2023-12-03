<p align="center">
  <a href="https://github.com/iholston/lol-bot">
    <img src="https://github.com/iholston/lol-bot/assets/32341824/71f35164-c8a6-42ca-a254-68d8be92780e" alt="Logo">
  </a>
</p>

## Welcome to LoL Bot
- This is a python bot that uses the local League Client API to start games and plays them with a simple but effective game loop
- This bot has leveled up [thousands of league accounts](https://www.playerauctions.com/lol-account/) and is still going strong
- No pixel botting and/or image recognition makes it easy to run on any setup
- New [GUI](https://imgur.com/a/8PlsMmi) and .exe with v2.0.0+


</br>
<p align="left">
  <img src="https://user-images.githubusercontent.com/32341824/231916860-8cdaa0bb-c808-48f7-8afe-5cd151501a98.gif">
</p>

## Current Features
- Start League and Login
- Start a Bot Game
- Buy items and somewhat intelligently push mid until the game is over
- End game, earn experience, collect rewards
- Loop 🥡🧋

## Usage
- Download the [latest release](https://github.com/iholston/lol-bot/releases)
- Run LoLBot.exe 👍

## League Account Requirements
League accounts should have already completed:
- Riot Promise
- Set Username
- Skipped Tutorials

NOTE: The bot will automatically change your league settings/configuration and the game window (not the client) should open as a 1024x768 window

## Development Requirements
- [Python >= 3.10](https://www.python.org/downloads/)  
- [League of Legends](https://signup.leagueoflegends.com/en-us/signup/download)  
- [League of Legends Account](https://signup.leagueoflegends.com/en-us/signup/index)  

## Development Setup
Clone the repo or download the [latest release](https://github.com/iholston/lol-bot/releases)
```sh
pip install -r requirements.txt
```
In some cases, it may be necessary to download and install [Microsoft C and C++ (MSVC) runtime libraries](https://learn.microsoft.com/en-GB/cpp/windows/latest-supported-vc-redist?view=msvc-170)

## Packaging to .exe
```sh
pip install pyinstaller
```
```sh
pyinstaller --onefile --noconsole --name "LoLBot" --icon=lolbot/resources/images/a.ico --add-data "lolbot/resources:lolbot/resources" main.pyw
```

## Optional Configuration
For Virtual Machine setups, I recommend starting with [this forum](https://www.unknowncheats.me/forum/league-of-legends/480977-run-league-legends-virtual-machine-vmware.html). *Note:* I will not be fixing/troubleshooting VM related issues as there are far too many VM implementation/platform specific issues

## Disclaimer
Another LoL Bot isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.

This software works with other programs/services (League of Legends) so you take full responsibility for breaking their Terms of Service and full responsibility for the accounts that you’re using with this bot and agree to use it at your own risk
