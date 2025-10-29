import streamlit as st
import random
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Badminton Game Manager",
    page_icon="🏸",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .court-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .sitting-out-card {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ffc107;
    }
    .player-tag {
        background-color: #e7f3ff;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px;
        display: inline-block;
    }
    .level-header {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
        margin: 20px 0 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Default player lists
DEFAULT_LEVEL1_PLAYERS = ['Masoud', 'Azadeh', 'Hamid', 'Massy', 'Mehdi', 'Honey']
DEFAULT_LEVEL2_PLAYERS = ['Sheida', 'Mehrdad', 'Amir', 'Sara', 'Kian', 'Maryam', 'Ghoncheh', 'Ali', 'Iman', 'Shobair', 'Arash']

# File to store game state
STATE_FILE = 'badminton_game_state.json'

def save_state():
    """Save the current game state to a JSON file"""
    state = {
        'level1_players': st.session_state.level1_players,
        'level2_players': st.session_state.level2_players,
        'current_assignments': st.session_state.current_assignments,
        'match_number': st.session_state.match_number,
        'pairing_history': {
            'Level 1': {str(k): v for k, v in st.session_state.pairing_history['Level 1'].items()},
            'Level 2': {str(k): v for k, v in st.session_state.pairing_history['Level 2'].items()}
        }
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_state():
    """Load game state from JSON file if it exists"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
                # Migrate old format to new format if needed
                if state.get('current_assignments') and 'level' in state.get('current_assignments', {}):
                    # Old format detected, convert to new format
                    old_assignment = state['current_assignments']
                    level = old_assignment.get('level', 'Level 1')
                    state['current_assignments'] = {
                        'Level 1': old_assignment if level == 'Level 1' else None,
                        'Level 2': old_assignment if level == 'Level 2' else None
                    }
                    # Remove the 'level' key from the assignment
                    if state['current_assignments']['Level 1']:
                        del state['current_assignments']['Level 1']['level']
                    if state['current_assignments']['Level 2']:
                        del state['current_assignments']['Level 2']['level']
                
                # Migrate match_number if it's a single number
                if isinstance(state.get('match_number'), int):
                    old_match = state['match_number']
                    state['match_number'] = {'Level 1': old_match, 'Level 2': 1}
                
                return state
        except:
            return None
    return None

def convert_pairing_history(pairing_dict):
    """Convert string keys back to tuples for pairing history"""
    result = {}
    for key, value in pairing_dict.items():
        # Convert string representation back to tuple
        # Keys are stored as "('Name1', 'Name2')"
        try:
            tuple_key = eval(key)
            result[tuple_key] = value
        except:
            pass
    return result

# Initialize session state
if 'initialized' not in st.session_state:
    # Try to load saved state
    saved_state = load_state()
    
    if saved_state:
        st.session_state.level1_players = saved_state.get('level1_players', DEFAULT_LEVEL1_PLAYERS.copy())
        st.session_state.level2_players = saved_state.get('level2_players', DEFAULT_LEVEL2_PLAYERS.copy())
        st.session_state.current_assignments = saved_state.get('current_assignments', {'Level 1': None, 'Level 2': None})
        st.session_state.match_number = saved_state.get('match_number', {'Level 1': 1, 'Level 2': 1})
        
        # Convert pairing history back to proper format
        pairing_hist = saved_state.get('pairing_history', {'Level 1': {}, 'Level 2': {}})
        st.session_state.pairing_history = {
            'Level 1': convert_pairing_history(pairing_hist.get('Level 1', {})),
            'Level 2': convert_pairing_history(pairing_hist.get('Level 2', {}))
        }
    else:
        # Use defaults
        st.session_state.level1_players = DEFAULT_LEVEL1_PLAYERS.copy()
        st.session_state.level2_players = DEFAULT_LEVEL2_PLAYERS.copy()
        st.session_state.current_assignments = {'Level 1': None, 'Level 2': None}
        st.session_state.match_number = {'Level 1': 1, 'Level 2': 1}
        st.session_state.pairing_history = {'Level 1': {}, 'Level 2': {}}
    
    st.session_state.initialized = True

# Helper functions
def get_pairings_from_court(court_players):
    """Get all unique pairings from a court (all players who played together)"""
    pairings = set()
    for i in range(len(court_players)):
        for j in range(i + 1, len(court_players)):
            pair = tuple(sorted([court_players[i], court_players[j]]))
            pairings.add(pair)
    return pairings

def score_arrangement(courts, pairing_history):
    """Score an arrangement based on how many repeated pairings it has (lower is better)"""
    score = 0
    for court in courts:
        pairings = get_pairings_from_court(court)
        for pair in pairings:
            if pair in pairing_history:
                # Penalize based on how many times they've played together
                score += pairing_history[pair]
    return score

def update_pairing_history(courts, pairing_history):
    """Update the pairing history with new pairings from this match"""
    for court in courts:
        pairings = get_pairings_from_court(court)
        for pair in pairings:
            if pair in pairing_history:
                pairing_history[pair] += 1
            else:
                pairing_history[pair] = 1
    return pairing_history

def shuffle_and_assign(players, level, num_attempts=50):
    """Shuffle players and assign them to courts, avoiding repeated pairings when possible"""
    if len(players) < 4:
        return None, None
    
    pairing_history = st.session_state.pairing_history[level]
    
    best_arrangement = None
    best_score = float('inf')
    
    # Try multiple random arrangements and pick the best one
    for _ in range(num_attempts):
        shuffled = random.sample(players, len(players))
        courts = []
        
        # Assign 4 players to each court (max 4 courts)
        for i in range(min(4, len(shuffled) // 4)):
            court_players = shuffled[i*4:(i+1)*4]
            courts.append(court_players)
        
        # Score this arrangement
        score = score_arrangement(courts, pairing_history)
        
        if score < best_score:
            best_score = score
            best_arrangement = (courts, shuffled)
    
    courts, shuffled = best_arrangement
    
    # Remaining players sit out
    players_playing = min(4, len(shuffled) // 4) * 4
    sitting_out = shuffled[players_playing:]
    
    # Update pairing history
    st.session_state.pairing_history[level] = update_pairing_history(courts, pairing_history)
    
    return courts, sitting_out

def display_court(court_number, players):
    """Display a court with its players"""
    st.markdown(f"""
        <div class="court-card">
            <h3>🏸 Court {court_number}</h3>
            <div>
                <strong>Team 1:</strong> {players[0]} & {players[1]}<br>
                <strong>Team 2:</strong> {players[2]} & {players[3]}
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_sitting_out(players):
    """Display players sitting out"""
    if players:
        players_str = ", ".join(players)
        st.markdown(f"""
            <div class="sitting-out-card">
                <h3>⏸️ Sitting Out</h3>
                <div>{players_str}</div>
            </div>
        """, unsafe_allow_html=True)

# Main app
st.title("🏸 Badminton Game Manager")
st.markdown("---")

# Sidebar for player management
with st.sidebar:
    st.header("⚙️ Player Management")
    
    level_tab = st.radio("Select Level", ["Level 1", "Level 2"], horizontal=True)
    
    st.markdown("### Add Player")
    new_player = st.text_input("Enter player name", key="new_player_input")
    
    if st.button("➕ Add Player", use_container_width=True):
        if new_player:
            if level_tab == "Level 1":
                if new_player not in st.session_state.level1_players:
                    st.session_state.level1_players.append(new_player)
                    save_state()
                    st.rerun()
                else:
                    st.warning("Player already exists!")
            else:
                if new_player not in st.session_state.level2_players:
                    st.session_state.level2_players.append(new_player)
                    save_state()
                    st.rerun()
                else:
                    st.warning("Player already exists!")
        else:
            st.warning("Please enter a name!")
    
    st.markdown("### Remove Player")
    players_list = st.session_state.level1_players if level_tab == "Level 1" else st.session_state.level2_players
    
    if players_list:
        player_to_remove = st.selectbox("Select player to remove", players_list, key="remove_player_select")
        
        if st.button("🗑️ Remove Player", use_container_width=True):
            if level_tab == "Level 1":
                st.session_state.level1_players.remove(player_to_remove)
            else:
                st.session_state.level2_players.remove(player_to_remove)
            save_state()
            st.rerun()
    else:
        st.info("No players to remove")
    
    st.markdown("---")
    st.markdown("### 🗑️ Clear All Players")
    
    if st.button("❌ Clear All Players", key="clear_all", use_container_width=True, type="secondary"):
        if level_tab == "Level 1":
            st.session_state.level1_players = []
        else:
            st.session_state.level2_players = []
        save_state()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Player Count")
    st.metric("Level 1 Players", len(st.session_state.level1_players))
    st.metric("Level 2 Players", len(st.session_state.level2_players))
    
    st.markdown("---")
    st.markdown("### 🔄 Reset to Default")
    if st.button("♻️ Reset to Default", key="reset_default", use_container_width=True, type="secondary"):
        if level_tab == "Level 1":
            st.session_state.level1_players = DEFAULT_LEVEL1_PLAYERS.copy()
            st.session_state.pairing_history['Level 1'] = {}
            st.session_state.current_assignments['Level 1'] = None
            st.session_state.match_number['Level 1'] = 1
        else:
            st.session_state.level2_players = DEFAULT_LEVEL2_PLAYERS.copy()
            st.session_state.pairing_history['Level 2'] = {}
            st.session_state.current_assignments['Level 2'] = None
            st.session_state.match_number['Level 2'] = 1
        save_state()
        st.rerun()

# Main content area
tab1, tab2 = st.tabs(["🏸 Level 1", "🏸 Level 2"])

with tab1:
    st.markdown('<div class="level-header">Level 1 Players</div>', unsafe_allow_html=True)
    
    # Display all Level 1 players
    if st.session_state.level1_players:
        cols = st.columns(5)
        for idx, player in enumerate(st.session_state.level1_players):
            with cols[idx % 5]:
                st.markdown(f'<div class="player-tag">{player}</div>', unsafe_allow_html=True)
    else:
        st.info("No players in Level 1. Add players using the sidebar.")
    
    st.markdown("---")
    
    # Shuffle button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔀 Shuffle & Assign Courts", key="shuffle_level1", use_container_width=True):
            if len(st.session_state.level1_players) >= 4:
                courts, sitting_out = shuffle_and_assign(st.session_state.level1_players, 'Level 1')
                st.session_state.current_assignments['Level 1'] = {
                    'courts': courts,
                    'sitting_out': sitting_out,
                    'match_number': st.session_state.match_number['Level 1']
                }
                st.session_state.match_number['Level 1'] += 1
                save_state()
                st.rerun()
            else:
                st.error("Need at least 4 players to start a game!")
    
    # Display current assignments
    if st.session_state.current_assignments['Level 1']:
        assignment = st.session_state.current_assignments['Level 1']
        st.markdown(f"### Match #{assignment['match_number']}")
        
        courts = assignment['courts']
        sitting_out = assignment['sitting_out']
        
        # Display courts in columns
        if courts:
            if len(courts) >= 2:
                col1, col2 = st.columns(2)
                for idx, court in enumerate(courts):
                    with col1 if idx % 2 == 0 else col2:
                        display_court(idx + 1, court)
            else:
                display_court(1, courts[0])
        
        # Display sitting out
        if sitting_out:
            display_sitting_out(sitting_out)

with tab2:
    st.markdown('<div class="level-header">Level 2 Players</div>', unsafe_allow_html=True)
    
    # Display all Level 2 players
    if st.session_state.level2_players:
        cols = st.columns(5)
        for idx, player in enumerate(st.session_state.level2_players):
            with cols[idx % 5]:
                st.markdown(f'<div class="player-tag">{player}</div>', unsafe_allow_html=True)
    else:
        st.info("No players in Level 2. Add players using the sidebar.")
    
    st.markdown("---")
    
    # Shuffle button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔀 Shuffle & Assign Courts", key="shuffle_level2", use_container_width=True):
            if len(st.session_state.level2_players) >= 4:
                courts, sitting_out = shuffle_and_assign(st.session_state.level2_players, 'Level 2')
                st.session_state.current_assignments['Level 2'] = {
                    'courts': courts,
                    'sitting_out': sitting_out,
                    'match_number': st.session_state.match_number['Level 2']
                }
                st.session_state.match_number['Level 2'] += 1
                save_state()
                st.rerun()
            else:
                st.error("Need at least 4 players to start a game!")
    
    # Display current assignments
    if st.session_state.current_assignments['Level 2']:
        assignment = st.session_state.current_assignments['Level 2']
        st.markdown(f"### Match #{assignment['match_number']}")
        
        courts = assignment['courts']
        sitting_out = assignment['sitting_out']
        
        # Display courts in columns
        if courts:
            if len(courts) >= 2:
                col1, col2 = st.columns(2)
                for idx, court in enumerate(courts):
                    with col1 if idx % 2 == 0 else col2:
                        display_court(idx + 1, court)
            else:
                display_court(1, courts[0])
        
        # Display sitting out
        if sitting_out:
            display_sitting_out(sitting_out)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "🏸 Badminton Game Manager | Manage your games efficiently"
    "</div>",
    unsafe_allow_html=True
)

