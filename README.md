# 🏸 Badminton Game Manager

A Streamlit web application to manage badminton games with multiple courts and player rotations.

## Features

- **Two Player Levels**: Manage separate groups of players (Level 1 and Level 2)
- **Dynamic Player Management**: Add or remove players easily
- **Clear All Players**: Remove all players from a level with one click
- **Smart Court Assignment**: Automatically assigns players to courts (4 players per court)
- **Intelligent Shuffling**: Randomly shuffles players while avoiding repeated pairings
- **Pairing Memory**: Tracks who has played with whom and minimizes repeat matchups
- **Sitting Out Tracking**: Shows which players are sitting out each round
- **Match Counter**: Keeps track of match numbers
- **Persistent Storage**: Automatically saves your game state - never lose your progress!
- **Reset to Default**: Restore default players and clear history

## How It Works

- **Up to 4 courts** available
- **4 players per court** (2 vs 2)
- Remaining players **sit out** for that round
- Each shuffle creates new random teams

## Installation

1. Make sure you have Python installed (Python 3.8 or higher)

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

To run the application, use the following command in your terminal:

```bash
streamlit run app.py
```

The app will open automatically in your default web browser at `http://localhost:8501`

## How to Use

### Adding Players
1. Use the sidebar to select Level 1 or Level 2
2. Enter a player name in the text input
3. Click "➕ Add Player"

### Removing Players
1. Select the level in the sidebar
2. Choose a player from the dropdown
3. Click "🗑️ Remove Player"

### Starting a Match
1. Navigate to the Level 1 or Level 2 tab
2. Click "🔀 Shuffle & Assign Courts"
3. Players will be randomly assigned to courts
4. Players who don't fit on courts will be shown as "Sitting Out"

### Next Match
Simply click the shuffle button again to create a new random arrangement for the next match!

### Clear All Players
1. Select the level in the sidebar
2. Click "❌ Clear All Players" to remove all players at once

### Reset to Default
1. Select the level in the sidebar
2. Click "♻️ Reset to Default" to restore default players and clear history
3. This is useful when starting a new season or if you want to start fresh

## How Smart Pairing Works

The app uses an intelligent algorithm to minimize repeated pairings:

1. **Tracks All Pairings**: Every time players are on the same court, all their pairings are recorded (e.g., if players A, B, C, D play together, it tracks A-B, A-C, A-D, B-C, B-D, and C-D)

2. **Evaluates Multiple Options**: When shuffling, the app generates 50 different random arrangements

3. **Selects Best Option**: It scores each arrangement based on how many repeated pairings it contains and chooses the one with the fewest repeats

4. **Maintains Fairness**: While prioritizing new pairings, the system still uses randomization to ensure fair rotation and variety

This means players will get to play with different people as much as possible, making the games more interesting and fair over multiple sessions!

## Persistent Storage - Never Lose Your Progress! 💾

The app automatically saves your game state after every change, including:
- Player lists for both levels
- Current court assignments
- Match number
- Complete pairing history

**What this means for you:**
- 🔒 **Safe to close**: Close the app anytime - your setup is saved
- 🔄 **Automatic recovery**: Reopen the app and pick up exactly where you left off
- 📊 **History preserved**: All pairing history is maintained across sessions
- 🎯 **No manual saving**: Everything saves automatically

The game state is stored in a file called `badminton_game_state.json` in the same directory as the app. You can delete this file if you want to completely reset everything to factory defaults.

## Example Setup

**Level 1 Players (Default):**
- Masoud, Azadeh, Hamid, Massy, Mehdi, Honey

**Level 2 Players (Default):**
- Sheida, Mehrdad, Amir, Sara, Kian, Maryam, Ghoncheh, Ali, Iman, Shobair, Arash

## Tips

- The app handles any number of players (minimum 4 required to play)
- Players are randomly shuffled each time for fair rotation
- **Smart Pairing**: The app remembers who has played together and tries to create new pairings each match
- The match number increments automatically
- Player lists are maintained separately for each level
- If you have 20 players, 16 will play (on 4 courts) and 4 will sit out
- Use **Clear All Players** to quickly remove all names and start fresh
- Use **Reset to Default** if you want to restore original players and clear pairing memory (e.g., at the start of a new season)
- **Your progress is automatically saved** - feel free to close the app anytime
- If you accidentally close the app, don't worry! Just reopen it and everything will be exactly as you left it

## Customization

You can modify the default player names in `app.py` by editing the session state initialization:

```python
st.session_state.level1_players = ['Your', 'Custom', 'Names', 'Here']
st.session_state.level2_players = ['More', 'Custom', 'Names']
```

Enjoy your badminton games! 🏸

