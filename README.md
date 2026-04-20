# BlitzAndCrank PUBLIC V1
League of Legends Tracker Discord Bot

Discord bot that allows users to 
- Register their league accounts to a leader board
- Get information on their rank, summoner level, and most played champions
- Presented in a quick and easily digestable manner

# Tech Stack
- Written fully in python
- Uses pycord for the discord bot
- RiotWatcher Wrapper to get account information
- SQLite for storing accounts

# BlitzAndCrank in Use
## Unranked Users
<img width="477" height="547" alt="image" src="https://github.com/user-attachments/assets/1505f90c-c68a-4483-872a-e399e380bdb7" />
When using /solo_rank {summoner name #tag}, if the user is unranked for the current season, account level along with top 3 champion masteries are shown.

## Ranked Users
<img width="487" height="501" alt="image" src="https://github.com/user-attachments/assets/26c579af-6079-4518-b713-3c8015aba394" />
When using /solo_rank {summoner name #tag}, if the user is ranked, acount level, current rank, and total games played are shown.

## Leaderboard
<img width="380" height="220" alt="image" src="https://github.com/user-attachments/assets/bc10a013-7ee5-479c-9192-9aedb34eb9d2" />
Current leaderboard sorts by account level, as shown here.
