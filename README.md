# BlitzAndCrank PUBLIC V1
League of Legends Tracker Discord Bot

Discord bot that allows users to 
- Register their league accounts to a leader board
- Get information on their rank, summoner level, and most played champions
- Presented in a quick and easily digestable manner

# Why BlitzAndCrank?
Having to tab out of game, or open a new chrome tab, and then go to a seperate website to see information on league accounts can get annoying, so BlitzAndCranks aims to allow users to do it all within discord. Usually when playing league, players will have discord open, meaning they can quickly and easily open the discord overlay and pull up a user's account information, and ask for help on their current matchup, all without having to tab out of league.

# Tech Stack
- Written fully in python
- Uses pycord for the discord bot
- RiotWatcher Wrapper to get account information
- SQLite for storing accounts

# BlitzAndCrank in Use
## Unranked Users
<img width="417" height="517" alt="image" src="https://github.com/user-attachments/assets/7d6ebcb8-fa43-4e8d-a994-8ffbe0b80635" />
When using /solo_rank {summoner name #tag}, if the user is unranked for the current season, account level along with top 3 champion masteries are shown.

## Ranked Users
<img width="487" height="501" alt="image" src="https://github.com/user-attachments/assets/26c579af-6079-4518-b713-3c8015aba394" />
When using /solo_rank {summoner name #tag}, if the user is ranked, acount level, current rank, and total games played are shown.

## Leaderboard
<img width="380" height="220" alt="image" src="https://github.com/user-attachments/assets/bc10a013-7ee5-479c-9192-9aedb34eb9d2" />
Current leaderboard sorts by account level, as shown here.

## Video Demo
https://youtu.be/wC8dam8dcQ4
