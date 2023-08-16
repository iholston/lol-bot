<p align="center">
  <a href="https://github.com/iholston/lol-bot">
    <img src="https://github.com/iholston/lol-bot/assets/32341824/71f35164-c8a6-42ca-a254-68d8be92780e" alt="Logo">
  </a>
</p>

## Welcome to LoL Bot
- This is a python bot that uses the local League Client API to start games and plays them with a simple but effective game loop.
- This bot has leveled up [thousands of league accounts](https://www.playerauctions.com/lol-account/) and is still going strong.
- No pixel botting and/or image recognition makes it easy to run on any setup.

</br>
<p align="left">
  <img src="https://user-images.githubusercontent.com/32341824/231916860-8cdaa0bb-c808-48f7-8afe-5cd151501a98.gif")
</p>

## Current Features
- Start League and Login
- Start a Beginner Bot Game
- Buy items and somewhat intelligently push mid until the game is over
- End game, earn experience, collect rewards
- Loop 🥡🧋

## Requirements
- [League of Legends](https://signup.leagueoflegends.com/en-us/signup/download)
- [League of Legends Account](https://signup.leagueoflegends.com/en-us/signup/index)
- [Python >= 3.10](https://www.python.org/downloads/)

## Setup
- Ensure Python is added to your PATH, check "Add Python to PATH" when installing
- Clone/Download the repo
- Download [extra RAM](https://downloadmoreram.com/) (only if needed)
- Run Installer.bat or ```pip install -r requirements.txt```

## Optional Configuration
- For non-standard league install paths, update the league_dir in constants.py
- To continuously level new league accounts:
  - Implement account.py to connect to your database of league accounts
  - Make sure that "stay signed in" is not checked when league of legends starts. 
  - This allows the bot to log out of league by closing it, get new account credentials, restart league, log in with the new credentials, and start another leveling loop, cycling indefinitely
- To level accounts past level 30 or play in different game types update game data variables in constants.py
- For Virtual Machines, I recommend starting with [this forum](https://www.unknowncheats.me/forum/league-of-legends/480977-run-league-legends-virtual-machine-vmware.html). *Please Note*, I will not be fixing/troubleshooting VM related issues as there are far too many VM implementation/platform specific issues. 

## Disclaimer
Another LoL Bot isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.

This software works with other programs/services (League of Legends) so you take full responsibility for breaking their Terms of Service and full responsibility for the accounts that you’re using with this bot and agree to use it at your own risk.
