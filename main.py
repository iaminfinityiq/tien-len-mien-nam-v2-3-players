# tiến lên miền nam 2 (3 players mode)

from __future__ import annotations
from os import system
from sys import exit
from typing import List, Callable
from random import randint
import json
from pyperclip import copy

def cls() -> None:
    system("clear")

def petc() -> None:
    input("Press enter to continue...")

cache: set[str] = set()
def random_planet_name() -> str:
    while True:
        name: str = ""
        for i in range(5):
            name += chr(randint(ord("A"), ord("Z")))
        
        number_index: str = str(randint(1, 99))
        if len(number_index) == 1:
            number_index = "0" + number_index
        
        name += number_index
        if name not in cache:
            cache.add(name)
            return name

class Option:
    def __init__(self, game: Game, name: str, functionality: Callable, planet: Planet) -> None:
        self.game = game
        self.name = name
        self.functionality = functionality
        self.planet = planet
    
    def do(self) -> str:
        return self.functionality(self.game, self.planet)

def move(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    player.move(planet)
    return f"You have successfully moved to {planet.name}"

def upgrade_damage(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    old: int = player.damage
    player.damage = int(player.damage * 1.2)
    return f"You have successfully increased {player.damage - old} damage"

def upgrade_poison(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    old: int = player.poison_damage
    player.poison_damage = int(player.poison_damage * 1.2)
    return f"You have successfully increased {player.poison_damage - old} poison damage"

def upgrade_max_hp(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    ratio: float = player.hp/player.max_hp
    old: int = player.max_hp
    player.max_hp = int(player.max_hp * 1.1)
    player.hp = int(ratio * player.max_hp)
    return f"Your max HP has increased from {old} HP to {player.max_hp} HP"

def upgrade_heal(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    old: int = player.heal_amount
    player.heal_amount = int(player.heal_amount * 1.5)
    return f"You can now heal from {old} HP to {player.heal_amount} HP per heal"

def heal(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    old: int = player.hp
    player.heal()
    return f"You have healed {player.hp - old} HP"

def attack(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    deaths: str = ""
    for other in planet.players:
        if other is not player and not other.dead():
            dead: str = player.attack(other)
            if other.dead():
                deaths += f"{dead}\n"
    
    return f"{deaths}You have attacked all of the players standing at {planet.name}"

def poison(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    for other in planet.players:
        if other is not player and not other.dead():
            player.poison(other)
    
    return f"You have poisoned all of the players standing at {planet.name}"

def elon_musk_button(game: Game, planet: Planet) -> str:
    planet.rovers += 1
    return f"You have successfully sent a rover to {planet.name}"

def attack_tower(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    message: str | None = player.attack(planet)
    if message is None:
        return f"You have successfully attacked {planet.name}'s tower"
    
    return message

def poison_tower(game: Game, planet: Planet) -> str:
    player: Player = game.players[game.turn]
    player.poison(planet)
    return f"You have successfully poisoned {planet.name}'s tower"

class Player:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.hp: int = 10000
        self.max_hp: int = 10000
        self.damage: int = 100
        self.poison_damage: int = 10
        self.poisoned_damage: int = 0
        self.heal_amount: int = 10
        self.at: Planet | None = None
        self.death_time: int = 0
        self.in_home_tower: int = 0
    
    def dead(self) -> bool:
        return self.hp <= 0
    
    def respawn(self) -> None:
        self.hp = self.max_hp
        self.in_home_tower = 0
    
    def attacked(self, damage: int) -> None:
        self.hp -= damage
        if self.dead():
            self.death_time = 10
            self.move(None)
    
    def attack(self, other: Player | Planet) -> str | None:
        other.attacked(self.damage)
        if other.dead():
            if isinstance(other, Player):
                return f"{self.name} has beaten {other.name} to death!"
        
            old_owner: Player | None = other.tower_owner
            other.tower_owner = self
            if old_owner is None:
                return f"{self.name}, you have earned {other.name}"
            
            return f"{other.tower_owner.name}, you have lost {other.name}\n{self.name}, you have earned {other.name}"
    
    def poisoned(self, poison_damage: int) -> None:
        self.poisoned_damage += poison_damage
        
    def poison(self, other: Player | Planet) -> None:
        other.poisoned(self.poison_damage)
        if isinstance(other, Planet):
            other.who_poisoned_last = self
    
    def get_poisoned(self) -> str | None:
        if self.at.rovers > 0 and self.poisoned_damage == 0:
            self.poisoned_damage = 10
            damage: int = 10
        else:
            damage: int = self.poisoned_damage * 2**self.at.rovers
        
        place_before_death: Planet | None = self.at
        self.attacked(damage)
        if self.dead():
            return f"{self.name} has died from poison{f' along with the damage from {place_before_death.rovers} rovers at {place_before_death.name}' if place_before_death.rovers > 0 else ''}"
    
    def heal(self) -> None:
        self.hp += self.heal_amount
        self.hp = min(self.hp, self.max_hp)
    
    def move(self, planet: Planet | None) -> None:
        if self.at is not None:
            self.at.players.remove(self)
        
        if planet is not None:
            planet.players += [self]
        
        self.at = planet

class Planet:
    def __init__(self, name: str, tower_owner: Player | None = None, players: List[Player] | None = None, paths: List[Planet] | None = None) -> None:
        self.name: str = name
        self.tower_owner: Player | None = tower_owner
        self.hp: int = 100000
        self.poisoned_damage: int = 0
        self.who_poisoned_last: Player | None = None
        self.rovers: int = 0
        if players is None:
            self.players: List[Player | None] = []
        else:
            self.players: List[Player | None] = players
        
        if paths is None:
            self.paths: List[Planet] = []
        else:
            self.paths: List[Planet] = paths
    
    def add_path(self, planet: Planet) -> None:
        self.paths += [planet]
        planet.paths += [self]
    
    def dead(self) -> bool:
        return self.hp <= 0
    
    def respawn(self) -> None:
        self.hp = 100000
        self.rovers = 0
        
    def attacked(self, damage: int) -> None:
        self.hp -= damage
    
    def transfer_ownership_through_poison(self) -> str | None:
        if not self.dead():
            return
        
        self.respawn()
        if self.tower_owner is not None:
            message: str = f"{self.tower_owner.name}, you have lost {self.name}"
        else:
            message: str = ""
        
        if self.tower_owner is self.who_poisoned_last:
            self.tower_owner = None
            self.who_poisoned_last = None
        else:
            self.tower_owner = self.who_poisoned_last
            message += f"{'\n' if message != '' else ''}{self.who_poisoned_last.name}, you have earned {self.name}"
        
        if message == "":
            return
        
        return message
        
    def get_poisoned(self) -> str | None:
        if self.rovers > 0 and self.poisoned_damage == 0:
            self.poisoned_damage = 10
            damage: int = 10
        else:
            damage: int = self.poisoned_damage * 2**self.rovers
        
        self.attacked(damage)
        return self.transfer_ownership_through_poison()
    
    def attack(self) -> str | None:
        if self.tower_owner is None:
            return
        
        message: str = ""
        for player in self.players:
            if player is self.tower_owner:
                continue
            
            player.attacked(1000)
            if player.dead():
                message += f"{'\n' if message != '' else ''}{player.name} has been wrecked by the defense of {self.tower_owner.name}'s {self.name}"
        
        if message == "":
            return
        
        return message
    
    def poisoned(self, poison_damage: int) -> None:
        self.poisoned_damage += poison_damage

class Game:
    def __init__(self, planet_names: List[Planet], p1: Player, p2: Player, p3: Player) -> None:
        self.planet_names: List[Planet] = planet_names
        self.players: List[Player] = [p1, p2, p3]
        self.turn: int = 0
        self.generate_map()
        for i, player in enumerate(self.players):
            player.move(self.spawn_points[i])
    
    def before_turn(self) -> None:
        cls()
        for i, planet in enumerate(self.spawn_points):
            if self.players[i] is not None and planet.tower_owner is not self.players[i]:
                print(f"{self.players[i].name} has lost their capital tower, thus eliminated from the game")
                petc()
                self.players[i] = None
        
        for i, player in enumerate(self.players):
            if player is not None and player.dead():
                player.death_time -= 1
                if player.death_time == 0:
                    player.respawn()
                    player.move(self.spawn_points[i])
                    print(f"{player.name} has revived!")
                    petc()

                continue
            
            death_message: str | None = player.get_poisoned()
            if death_message is not None:
                print(death_message)
                petc()
        
        for planet in self.spawn_points:
            message: str | None = planet.get_poisoned()
            if message is not None:
                print(message)
                petc()
            
            message = planet.paths[0].get_poisoned()
            if message is not None:
                print(message)
                petc()
        
        message = self.center.get_poisoned()
        if message is not None:
            print(message)
            petc()
        
        for planet in self.spawn_points:
            message: str | None = planet.attack()
            if message is not None:
                print(message)
                petc()
            
            message = planet.paths[0].attack()
            if message is not None:
                print(message)
                petc()
        
        message = self.center.attack()
        if message is not None:
            print(message)
            petc()
        
        for player in self.players:
            if player.dead():
                continue
            
            if player is player.at.tower_owner:
                player.in_home_tower += 1
            else:
                player.in_home_tower = 0
    
    def perform_turn(self) -> None:
        cls()
        player: Player = self.players[self.turn]
        if player is None:
            self.turn += 1
            self.turn %= 3
            return
        
        planet: Planet = player.at
        if player.dead():
            self.turn += 1
            self.turn %= 3
            print(f"{player.name}, you are currently dead, please wait for a moment to respawn")
            petc()
            return
        
        print(f"It's currently {player.name}'s turn. Please pass the device to them")
        petc()
        
        while True:
            cls()
            print(f"""{player.name}, you are at {planet.name}. Here are your stats:
HP: {player.hp} HP/{player.max_hp} HP
Damage: {player.damage} HP
Poison damage: {player.poison_damage} HP
Taking {10 if player.poisoned_damage == 0 and planet.rovers > 0 else player.poisoned_damage * 2**planet.rovers} HP per turn from poison
Planet's tower HP: {planet.hp} HP/100000 HP
Rovers in planet: {planet.rovers}

Currently, you can perform the following actions:""")
            options: List[Option] = []
            for path in planet.paths:
                options += [Option(self, f"Move to {path.name}", move, path)]
            
            if planet.tower_owner is player:
                options += [Option(self, f"Increase 20% damage ({player.damage} -> {int(player.damage * 1.2)})", upgrade_damage, planet)]
                options += [Option(self, f"Increase 20% poison damage ({player.poison_damage} -> {int(player.poison_damage * 1.2)})", upgrade_poison, planet)]
                options += [Option(self, f"Increase 10% max HP ({player.max_hp} -> {int(player.max_hp * 1.1)})", upgrade_max_hp, planet)]
                options += [Option(self, f"Increase 50% heal amount ({player.heal_amount} -> {int(player.heal_amount * 1.5)})", upgrade_heal, planet)]
                options += [Option(self, f"Heal ({player.hp} -> {min(player.hp + player.heal_amount, player.max_hp)})", heal, planet)]
            else:
                options += [Option(self, f"Attack the tower ({planet.hp} -> {'FATAL' if planet.hp - player.damage <= 0 else planet.hp - player.damage})", attack_tower, planet)]
                options += [Option(self, f"Poison tower ({planet.poisoned_damage} -> {planet.poisoned_damage + player.poison_damage})", poison_tower, planet)]
            
            for other in planet.players:
                if other is not player and not other.dead():
                    options += [Option(self, f"Attack all players at your planet (apart from you)", attack, planet)]
                    options += [Option(self, f"Poison all players at your planet (apart from you)", poison, planet)]
                    break
            
            for other in self.players:
                if other.in_home_tower >= 10 and other is not player and not other.dead():
                    options += [Option(self, f"Elon Musk button ({other.name} has stayed in their towers for {other.in_home_tower} consecutive turns)", elon_musk_button, other.at)]

            for i, option in enumerate(options):
                print(f"[{i+1}] {option.name}")
            
            inp: str = input(f"\nPlease enter a number from 1 to {len(options)} corresponding to your choice: ")
            try:
                choice: int = int(inp)
                if choice < 1 or choice > len(options):
                    print("Invalid number!")
                    petc()
                    continue
                
                option: Option = options[choice-1]
                result: str | None = option.do()
                if result is not None:
                    print(result)
                    petc()
                
                break
            except Exception as e:
                print("Invalid number!", e)
                petc()
                continue
        
        self.turn += 1
        self.turn %= 3
    
    def generate_map(self) -> None:
        planet_idx: int = 0
        self.spawn_points: List[Planet] = []
        for i in range(3):
            self.spawn_points += [Planet(self.planet_names[planet_idx], self.players[i])]
            planet_idx += 1
        
        for i, planet in enumerate(self.spawn_points):
            planet.add_path(Planet(self.planet_names[planet_idx], self.players[i]))
            planet_idx += 1
        
        self.center: Planet = Planet(self.planet_names[planet_idx])
        for planet in self.spawn_points:
            planet.paths[0].add_path(self.center)

def encode_game(game: Game) -> str:
    planets = []
    visited = set()

    def dfs(planet: Planet) -> None:
        if id(planet) in visited:
            return

        visited.add(id(planet))
        planets.append(planet)

        for path in planet.paths:
            dfs(path)

    for spawn in game.spawn_points:
        dfs(spawn)

    planet_ids = {
        planet: i
        for i, planet in enumerate(planets)
    }

    player_ids = {
        player: i
        for i, player in enumerate(game.players)
        if player is not None
    }

    data = {
        "turn": game.turn,
        "players": [],
        "planets": [],
        "spawn_points": [
            planet_ids[planet]
            for planet in game.spawn_points
        ],
        "center": planet_ids[game.center]
    }

    for player in game.players:
        if player is None:
            data["players"].append(None)
            continue

        data["players"].append({
            "name": player.name,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "damage": player.damage,
            "poison_damage": player.poison_damage,
            "poisoned_damage": player.poisoned_damage,
            "heal_amount": player.heal_amount,
            "death_time": player.death_time,
            "in_home_tower": player.in_home_tower,
            "at": None if player.at is None else planet_ids[player.at]
        })

    for planet in planets:
        data["planets"].append({
            "name": planet.name,
            "hp": planet.hp,
            "poisoned_damage": planet.poisoned_damage,
            "rovers": planet.rovers,
            "tower_owner": None if planet.tower_owner is None else player_ids[planet.tower_owner],
            "who_poisoned_last": None if planet.who_poisoned_last is None else player_ids[planet.who_poisoned_last],
            "paths": [
                planet_ids[path]
                for path in planet.paths
            ]
        })

    return json.dumps(data, separators=(",", ":"))

def decode_game(encoded: str) -> Game:
    data = json.loads(encoded)

    players = []

    for player_data in data["players"]:
        if player_data is None:
            players.append(None)
            continue

        player = Player(player_data["name"])

        player.hp = player_data["hp"]
        player.max_hp = player_data["max_hp"]
        player.damage = player_data["damage"]
        player.poison_damage = player_data["poison_damage"]
        player.poisoned_damage = player_data["poisoned_damage"]
        player.heal_amount = player_data["heal_amount"]
        player.death_time = player_data["death_time"]
        player.in_home_tower = player_data["in_home_tower"]

        players.append(player)

    planets = []

    for planet_data in data["planets"]:
        planet = Planet(planet_data["name"])

        planet.hp = planet_data["hp"]
        planet.poisoned_damage = planet_data["poisoned_damage"]
        planet.rovers = planet_data["rovers"]

        planets.append(planet)

    for planet, planet_data in zip(planets, data["planets"]):
        planet.paths = [
            planets[idx]
            for idx in planet_data["paths"]
        ]

        if planet_data["tower_owner"] is not None:
            planet.tower_owner = players[planet_data["tower_owner"]]

        if planet_data["who_poisoned_last"] is not None:
            planet.who_poisoned_last = players[planet_data["who_poisoned_last"]]

    for player, player_data in zip(players, data["players"]):
        if player is None:
            continue

        if player_data["at"] is not None:
            planet = planets[player_data["at"]]
            player.at = planet
            planet.players.append(player)

    game = Game.__new__(Game)

    game.players = players
    game.turn = data["turn"]

    game.spawn_points = [
        planets[idx]
        for idx in data["spawn_points"]
    ]

    game.center = planets[data["center"]]

    game.planet_names = [
        planet.name
        for planet in planets
    ]

    return game

decoded: str = input("Do you have an encoded save code of an unfinished game? ")
if decoded:
    game: Game = decode_game(decoded)
else:
    planet_names: List[str] = [random_planet_name() for i in range(7)]

    print("Welcome to Tiến lên miền Nam. Before we play, let's go over the rules of the game")
    petc()

    cls()
    print("First of all, 3 players are required to play the game")
    petc()

    cls()
    print("First of all, 3 players are required to play the game")
    p1: Player = Player(input("P1: "))
    p2: Player = Player(input("P2: "))
    p3: Player = Player(input("P3: "))
    petc()

    cls()
    print(f"""The map we are playing will be as follows:
    {planet_names[0]} <=> {planet_names[3]} <=> {planet_names[6]} <=> {planet_names[4]} <=> {planet_names[1]}
                            ^
                            |
                            v
                            {planet_names[5]}
                            ^
                            |
                            v
                            {planet_names[2]}
    There are 7 planets in our map, each has a unique name which is randomly generated for each game. Each planet has a tower, towers from planets {planet_names[0]} and {planet_names[3]} are {p1.name}'s, towers from planets {planet_names[1]} and {planet_names[4]} are {p2.name}'s, and towers from planets {planet_names[2]} and {planet_names[5]} are {p3.name}'s. {planet_names[6]}'s tower is neutral""")
    petc()

    cls()
    print("""There are 3 cases that can happen when you are on a planet:
    1. You are on a planet which has your tower
    2. You are on a planet which has your opponent's tower
    3. You are on a planet which has no tower owner""")
    petc()

    cls()
    print("If you are on a planet which has your tower, you get to heal and upgrade yourself")
    petc()

    cls()
    print("However, if you are on a planet which has your opponent's tower, you can neither heal nor upgrade yourself and also take damage from the tower. But you also have a choice to attack the tower, and maybe you will capture it depending on its HP")
    petc()

    cls()
    print("But if you are on a planet with a neutral tower, you can neither heal nor upgrade yourself, but you don't take damage too. You also have a choice to attack the tower, depending on the HP to see if you can capture it")
    petc()

    cls()
    print(f"Each player also have a capital tower, which determines if they will win or lose. {p1.name}'s capital tower is at {planet_names[0]}, {p2.name}'s capital tower is at {planet_names[1]}, and {p3.name}'s capital tower is at {planet_names[2]}")
    petc()

    cls()
    print("If your capital tower is captured, you will be eliminated from the game. You win if you are the last one standing")
    petc()

    cls()
    print("Good luck...")
    petc()

    game: Game = Game(planet_names, p1, p2, p3)

try:
    while True:
        alive_count: int = 0
        that_player: Player | None = None
        for player in game.players:
            if player is not None:
                alive_count += 1
                that_player = player
        
        if alive_count == 1:
            print(f"{that_player.name} won!")
            exit(0)
        
        if alive_count == 0:
            print("It's a tie!")
            exit(0)
        
        game.before_turn()
        game.perform_turn()
except KeyboardInterrupt:
    copy(encode_game(game))
    print("Your code has been saved to the clipboard!")
    exit(0)
