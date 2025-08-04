# Student ID: S10275182A
# Name: Lam Thong Wan
# Class: PRG1
# Date: 23 July 2025
# Description of the game: 
# Develop a computer strategy role-playing game called Sundrop Caves. 
# Objective of the game:
# Exploring the mine and collect mines, sell the mine orbs to get GP to either upgrade their bag capacity or upgrade the pickaxe to get more valuable mines
# Once the player got at least 500 GP, they win the game

from random import randint
import json
import os

# Steps:
# W	= Up	
# A	= Left	
# S	= Down	
# D	= Right

# Constant Variables
TURNS_PER_DAY = 20
WIN_GP = 500

# Map and game state
player = {}
game_map = []
fog = []
portal_position = {'x': -1, 'y': -1}
MAP_WIDTH = 0
MAP_HEIGHT = 0

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
price_mineral = {'copper': (1, 3),'silver': (5, 8),'gold': (10, 18)}
produce_mineral = {'copper': (1, 3),'silver': (1, 2),'gold': (1, 1)}
pickaxe_price = [50, 150] #For upgrading the pickaxe

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(filename, map_struct):
    global MAP_WIDTH, MAP_HEIGHT
    # Read the file
    with open("level1.txt", 'r') as map_file:
        map_struct.clear()

        # TODO: Add your map loading code here
        for line in map_file:
            row = list(line.rstrip('\n'))
            map_struct.append(row)

    MAP_HEIGHT = len(map_struct)
    MAP_WIDTH = len(map_struct[0]) if MAP_HEIGHT > 0 else 0

# This function clears the fog of war at the 3x3 square around the player while discovering the mine
def clear_fog(current_fog, current_player):
    global MAP_WIDTH, MAP_HEIGHT
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx = current_player['x'] + dx
            ny = current_player['y'] + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                current_fog[ny][nx] = False

#This function is when N (New Game) is chosen at the main menu to start a new game
def initialize_game():
    global player, game_map, fog, portal_position, MAP_WIDTH, MAP_HEIGHT

    # Initialize map
    load_map("level1.txt", game_map)

    # Initialize fog map
    fog = [[True for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # Initialize player
    player['name'] = input("Greetings, miner! What is your name? ") 
    print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!") 

    #Setting up the things needed for the user
    player['x'] = 0
    player['y'] = 0
    player['ore'] = {'copper': 0, 'silver': 0, 'gold': 0} 
    player['GP'] = 0
    player['day'] = 1 
    player['steps_taken_total'] = 0 
    player['turns_left_today'] = TURNS_PER_DAY
    player['backpack_capacity'] = 10 
    player['pickaxe_level'] = 1 

    # Clear fog at starting position
    clear_fog(fog, player)
    
    # Reset portal position
    portal_position['x'] = -1
    portal_position['y'] = -1

# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):
    print("\n--- Full Map View ---")
    for y in range(MAP_HEIGHT):
        row = ''
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                row += 'M'  # Player position
            elif fog[y][x]:
                row += '?'  # Fog
            else:
                row += game_map[y][x]
        print(row)

# This function draws the map in the mine
def display_map_in_mine(current_game_map, current_fog, current_player, current_portal_pos):
    print("\n")
    print(f"DAY {current_player['day']}")
    print("+---+" )
    # Print 3x3 view around us in the mine
    for dy in range(-1, 2):
        row_str = "|"
        for dx in range(-1, 2):
            nx = current_player['x'] + dx
            ny = current_player['y'] + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                if nx == current_player['x'] and ny == current_player['y']:
                    row_str += 'M' 
                elif current_fog[ny][nx]:
                    row_str += '?' # Fogged area in the map
                elif current_portal_pos['x'] == nx and current_portal_pos['y'] == ny:
                    row_str += 'P' # Portal stone location 
                else:
                    row_str += current_game_map[ny][nx]
            else:
                row_str += '#'
        print(row_str + "|")
    print("+---+" )
    
    print(f"Turns left: {current_player['turns_left_today']} Load {sum(current_player['ore'].values())}/{current_player['backpack_capacity']} Steps: {current_player['steps_taken_total']}") 
    print("(WASD) to move") 
    print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu") 

# Main Menu (For Viewing)
def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(V)iew Top Scores")
    print("(Q)uit")
    print("------------------")

# Town Menu (For Viewing)
def show_town_menu():
    print(f"\nDAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")

# This function shows the information for the player
def show_player_information(player): 
    print("\n----- Player Information -----") 
    print(f"Name: {player['name']}")
    print(f"Portal position: ({player['x']}, {player['y']})") 
    
    # Pickaxe level display
    pickaxe_desc = {1: "copper", 2: "silver", 3: "gold"}
    print(f"Pickaxe level: {player['pickaxe_level']} ({pickaxe_desc.get(player['pickaxe_level'], 'unknown')})") 
    print("--------------------------------")
    print(f"Load: {sum(player['ore'].values())} / {player['backpack_capacity']}") 
    print("--------------------------------")
    print(f"GP: {player['GP']}") 
    print(f"Steps taken: {player['steps_taken_total']}") 
    print("------------------------------")

#This function is to load the game for past progress
def load_game():
    filename = "savefile.json"
    
    if not os.path.exists(filename):
        print("No saved game found!")
        return handle_main_menu()
    
    with open(filename, "r") as f:
        data = json.load(f)
    
    player = data["player"]
    mine_map = data["mine_map"]
    fog_map = data["fog_map"]
    current_day = data["current_day"]
    
    print(f"Welcome back, {player['name']}! Loaded game from Day {current_day}.")
    
    return player, mine_map, fog_map, current_day

# This function saves the game
def save_game(game_map, fog, player):
    save_data = {'map': game_map,'fog': fog,'player': player}

    with open('savegame.json', 'w') as save_file:
        json.dump(save_data, save_file)

    print("Game saved successfully.")

# Main Menu function (Able to choose)
def handle_main_menu():
    show_main_menu()
    choice = input("Your choice? ").strip().upper() 

    if choice == 'N' or choice.upper() == "N":
        initialize_game()
        return 'town'
    elif choice == 'L' or choice.upper() == "L":
        load_game()
    elif choice == 'Q' or choice.upper() == "Q":
        return 'quit'
    elif choice == "V" or choice.upper() == "V":
        return 
    else:
        print("Invalid choice. Please choose N, L, Q or O.")
        return 'main_menu'

#This function is to save the score of the player once they achieve the game goal
def save_score(player):
    scores_file = "scores.json"

    #record in the file
    new_score = {
        "name": player["name"],
        "GP": player["GP"],
        "days": player["day"],
        "steps": player["steps_taken_total"]
    }

    # If file exists, load scores; else start with empty list
    if os.path.exists(scores_file):
        with open(scores_file, "r") as f:
            scores = json.load(f)
    else:
        scores = []

    # Add the new score in the file
    scores.append(new_score)

    # Save back to the file
    with open(scores_file, "w") as f:
        json.dump(scores, f, indent=4)

    print("Score saved!")

#This function shows the top scores for each game that player done
def show_top_scores():
    if not os.path.exists("scores.json"):
        print("\nNo scores yet.")
        return

    with open("scores.json", "r") as file:
        scores = json.load(file)
        print("\n-- Scores --")
        for s in scores:
            print(s)

# Town Menu function (Able to choose)
def handle_town_menu():
    global player, game_map, fog, portal_position
    
    # Auto-sell ore when in town
    if sum(player['ore'].values()) > 0:
        sell_ore()
        
    show_town_menu()
    choice = input("Your choice? ").strip().upper()

    if choice == 'B' or choice.upper() == "B":
        handle_shop_menu()
        return 'town'
    
    elif choice == 'I' or choice.upper() == "I":
        show_player_information(player)
        return 'town'
    
    elif choice == 'M' or choice.upper() == "M":
        draw_map(game_map, fog, player) 
        return 'town'
    
    elif choice == 'E' or choice.upper() == "E":
        if portal_position['x'] != -1 and portal_position['y'] != -1:
            player['x'] = portal_position['x']
            player['y'] = portal_position['y']
        clear_fog(fog, player)
        return 'mine'
    
    elif choice == 'V' or choice.upper() == "V":
        # TODO: Implement save_game()
        save_game(game_map, fog, player)
        print("Game saved.") 
        return 'town'
    
    elif choice == 'Q' or choice.upper() == "Q":
        return 'main_menu'
    
    else:
        print("Invalid choice. Please choose B, I, M, E, V, or Q.")
        return 'town'

# Selling the orbs (auto) after mining
def sell_ore():
    global player
    total_sold_gp = 0

    print("\nSelling ore...")
    for mineral_type in minerals:
        if player['ore'][mineral_type] > 0:
            min_price, max_price = price_mineral[mineral_type]
            price_per_piece = randint(min_price, max_price)
            gp_earned = player['ore'][mineral_type] * price_per_piece
            total_sold_gp += gp_earned
            print(f"You sell {player['ore'][mineral_type]} {mineral_type} ore for {gp_earned} GP.") 
            player['ore'][mineral_type] = 0  # Reset ore count after selling

    player['GP'] += total_sold_gp
    print(f"You now have {player['GP']} GP!")
    check_win_condition()

#Check whether the user have 500 GP, if yes we win
def check_win_condition():
    global player
    if player['GP'] >= WIN_GP: 
        print("\n-------------------------------------------------------------")
        print(f"Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!") 
        print("You now have enough to retire and play video games every day.") 
        print(f"And it only took you {player['day']} days and {player['steps_taken_total']} steps! You win!")
        print("-------------------------------------------------------------")
        #Save the file once you win

    return 'town' # Stay in town if not won

# Shop menu function (Able to choose)
def handle_shop_menu():
    global player
    while True:
        print("\n----------------------- Shop Menu -------------------------") 
        
        # Pickaxe upgrade option (Advanced feature)
        pickaxe_upgrade_text = ""
        if player['pickaxe_level'] == 1:
            pickaxe_upgrade_text = f"(P)ickaxe upgrade to Level 2 to mine silver ore for {pickaxe_price[0]} GP" 
        elif player['pickaxe_level'] == 2:
            pickaxe_upgrade_text = f"(P)ickaxe upgrade to Level 3 to mine gold ore for {pickaxe_price[1]} GP" 
        else:
            pickaxe_upgrade_text = "(P)ickaxe is already max level" 

        print(pickaxe_upgrade_text)
        
        # Backpack upgrade option
        backpack_upgrade_cost = player['backpack_capacity'] * 2 
        print(f"(B)ackpack upgrade to carry {player['backpack_capacity'] + 2} items for {backpack_upgrade_cost} GP") 
        print("(L)eave shop") 
        print("-----------------------------------------------------------")
        print(f"GP: {player['GP']}") 
        print("-----------------------------------------------------------")

        choice = input("Your choice? ").strip().upper() 

        if choice == 'P' or choice.upper() == "P":
            upgrade_pickaxe()
        elif choice == 'B' or choice.upper() == "B": 
            upgrade_backpack()
        elif choice == 'L' or choice.upper() == "L":
            break # Exit shop menu 
        else:
            print("Invalid choice. Please choose P, B, or L.")

# Upgrade backpack in the shop 
def upgrade_backpack():
    global player
    upgrade_cost = player['backpack_capacity'] * 2 
    if player['GP'] >= upgrade_cost:
        player['GP'] -= upgrade_cost
        player['backpack_capacity'] += 2 
        print(f"Congratulations! You can now carry {player['backpack_capacity']} items!") 
    else:
        print(f"Not enough GP! You need {upgrade_cost} GP to upgrade.")

# Upgrade pickaxe in the shop
def upgrade_pickaxe():
    global player
    if player['pickaxe_level'] == 1:
        cost = pickaxe_price[0] # Use 50 GP 
        if player['GP'] >= cost:
            player['GP'] -= cost
            player['pickaxe_level'] = 2
            print("Congratulations! You can now mine silver!")

        else:
            print(f"Not enough GP! You need {cost} GP to upgrade to Level 2.")

    elif player['pickaxe_level'] == 2:
        cost = pickaxe_price[1] # Use 150 GP 
        if player['GP'] >= cost:
            player['GP'] -= cost
            player['pickaxe_level'] = 3
            print("Congratulations! You can now mine gold!")

        else:
            print(f"Not enough GP! You need {cost} GP to upgrade to Level 3.")

    else:
        print("Your pickaxe is already at the maximum level (Level 3).")

# Mining Menu Function (Walks around in the mine)
def handle_mine_menu():
    global player, game_map, fog, portal_position
    
    # Display Viewportal
    display_map_in_mine(game_map, fog, player, portal_position)
    action = input("Action? ").strip().upper() 

    # All actions in the mine, successful or not, consume a turn 
    if player['turns_left_today'] > 0:
        player['turns_left_today'] -= 1
        
    if action in ['W', 'A', 'S', 'D']:
        move_player(action)

    elif action == 'M':
        draw_map(game_map, fog, player)

    elif action == 'I':
        show_player_information(player)

    elif action == 'P':
        use_portal_stone()
        return 'town'
    
    elif action == 'Q':
        return handle_main_menu()
    
    else:
        print("Invalid action. Please choose W, A, S, D, M, I, P, or Q.")

    # Check if turns ran out
    if player['turns_left_today'] <= 0:
        print("You are exhausted.") 
        print("You place your portal stone here and zap back to town..") 
        use_portal_stone()
        return 'town' # Automatically return to town if turns run out 
    
    return 'mine'

# Moving the player around in the mine
def move_player(direction):
    global player, game_map, fog

    current_x, current_y = player['x'], player['y']
    new_x, new_y = current_x, current_y

    if direction == 'W' or direction.upper() == "W":
        new_y -= 1
    elif direction == 'A' or direction.upper() == "A":
        new_x -= 1
    elif direction == 'S' or direction.upper()== "S":
        new_y += 1
    elif direction == 'D' or direction.upper() == "D":
        new_x += 1

    # Check boundaries 
    if not (0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT):
        print("Cannot move past the edge of the map.")
        return

    target_cell = game_map[new_y][new_x]

    # Check if target is a mineral node and backpack is full 
    if target_cell in ['C', 'S', 'G'] and sum(player['ore'].values()) >= player['backpack_capacity']:
        print("You can't carry any more, so you can't go that way.")

    # Check pickaxe level for mining
    if target_cell in ['C', 'S', 'G']:
        required_level = 0
        if target_cell == 'C':
            required_level = 1

        elif target_cell == 'S':
            required_level = 2

        elif target_cell == 'G':
            required_level = 3
        
        if player['pickaxe_level'] < required_level:
            print(f"Your pickaxe is not strong enough to mine {mineral_names[target_cell]} ore (requires Level {required_level}).")
            return # Stay on the spot if pickaxe level is insufficient to mine

    # If done checking the target, update player position to move
    player['x'] = new_x
    player['y'] = new_y
    player['steps_taken_total'] += 1

    # Clear fog around new position
    clear_fog(fog, player)

    # Handle stepping on Town 'T' 
    if target_cell == 'T':
        print("You've returned to town.")
        use_portal_stone() # Resets position to 0,0 as the user use the protal
        return

    # Take the orb if stepping on a mineral node 
    if target_cell in ['C', 'S', 'G']:
        mine_ore(target_cell)
        game_map[new_y][new_x] = ' ' # Replace mined node with empty space

# Mining Orbs function (Idenitfy which mine orb we mine)
def mine_ore(mineral_symbol):
    global player
    mineral_type = mineral_names[mineral_symbol]
    min_pieces, max_pieces = produce_mineral[mineral_type]
    
    # Calculate how many pieces can actually be picked up
    space_left = player['backpack_capacity'] - sum(player['ore'].values())
    
    if space_left <= 0:
        print("Your backpack is full! Cannot mine any more.")
        return 

    pieces_mined = randint(min_pieces, max_pieces)
    actual_pieces_mined = min(pieces_mined, space_left)

    if actual_pieces_mined > 0:
        player['ore'][mineral_type] += actual_pieces_mined
        print(f"You mined {actual_pieces_mined} piece(s) of {mineral_type}.") 

        if actual_pieces_mined < pieces_mined:
            print(f"...but you can only carry {space_left} more piece(s)!") 

    else:
        print(f"You tried to mine {mineral_type}, but your backpack is full.")

# Using the portal
def use_portal_stone():
    global player, portal_position
    
    # Set portal position
    portal_position['x'] = player['x']
    portal_position['y'] = player['y']
    
    # Return player to town (0,0) and advance day 
    player['x'] = 0
    player['y'] = 0
    player['day'] += 1 
    player['turns_left_today'] = TURNS_PER_DAY
    
    # Clear fog at town location
    clear_fog(fog, player)

# Main game loop
def main():
    global player, game_map, fog, portal_position
    
    print("---------------- Welcome to Sundrop Caves! ----------------") 
    print("You spent all your money to get the deed to a mine, a small") 
    print("  backpack, a simple pickaxe and a magical portal stone.") 
    print()
    print("How quickly can you get the 500 GP you need to retire") 
    print("  and live happily ever after?") 
    print("-----------------------------------------------------------")

    current_game_state = 'main_menu'

    while True:
        if current_game_state == 'main_menu':
            current_game_state = handle_main_menu()
        elif current_game_state == 'town':
            current_game_state = handle_town_menu()
        elif current_game_state == 'mine':
            current_game_state = handle_mine_menu()
        elif current_game_state == 'quit':
            print("Exiting game. Goodbye!")
            break

#Run the code
if __name__ == "__main__":
    main()

