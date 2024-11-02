import random
import math
import numpy as np
import matplotlib.pyplot as plt

cards = {
    "♢": {"all": (0, 25), "mewtwo": (0, 25), "charizard": (0, 25), "pikachu": (0, 25)},
    "♢♢": {"all": (0, 18), "mewtwo": (0, 17), "charizard": (0, 17), "pikachu": (0, 17)},
    "♢♢♢": {"all": (), "mewtwo": (0, 14), "charizard": (0, 14), "pikachu": (0, 14)},
    "♢♢♢♢": {"all": (), "mewtwo": (0, 5), "charizard": (0, 5), "pikachu": (0, 5)},
    "☆": {"all": (), "mewtwo": (0, 8), "charizard": (0, 8), "pikachu": (0, 8)},
    "☆☆": {"all": (), "mewtwo": (0, 9), "charizard": (0, 10), "pikachu": (0, 10)},
    "☆☆☆": {"all": (), "mewtwo": (0, 1), "charizard": (0, 1), "pikachu": (0, 1)},
    "♛": {"all": (0, 3), "mewtwo": (), "charizard": (), "pikachu": ()},
}

packs = {
    "mewtwo": {},
    "charizard": {},
    "pikachu": {},
}

odds_normal_123 = {"♢": 1}
odds_rare_12345 = {"☆": 0.42105, "☆☆": 0.47368, "☆☆☆": 0.05263, "♛": 0.05263}

pack_odds = {
    "regular": {
        1: odds_normal_123,
        2: odds_normal_123,
        3: odds_normal_123,
        4: {"♢♢": 0.9, "♢♢♢": 0.05, "♢♢♢♢": 0.01666, "☆": 0.02572, "☆☆": 0.005, "☆☆☆": 0.00222, "♛": 0.0004},
        5: {"♢♢": 0.6, "♢♢♢": 0.2, "♢♢♢♢": 0.06664, "☆": 0.10288, "☆☆": 0.02, "☆☆☆": 0.00888, "♛": 0.0016},
    },
    "rare": {1: odds_rare_12345, 2: odds_rare_12345, 3: odds_rare_12345, 4: odds_rare_12345, 5: odds_rare_12345},
}


def create_cards():
    card_num = 0
    for rarity in cards:
        for key, value in cards[rarity].items():
            new_value = []
            if value:
                for i in range(value[1]):
                    new_value.append(card_num)
                    card_num += 1
            cards[rarity][key] = new_value


def create_packs():
    base_dict = {"♢":[], "♢♢":[], "♢♢♢":[], "♢♢♢♢":[], "☆":[], "☆☆":[], "☆☆☆":[], "♛":[]}
    for pack_name, pack in packs.items():
        pack = base_dict.copy()
        for rarity in pack:
            for key, value in cards[rarity].items():
                if key in (pack_name, "all"):
                    pack[rarity].extend(value)
        packs[pack_name] = pack
    

def get_empty_collection():
    """
    collection = {
    0: {
        "rarity": "♢",
        "pack": "all",
        "count": 0
    },
    1: {
        "rarity": "♢",
        "pack": "all",
        "count": 0
    },
    224: ...
    }
    """
    collection = {}
    for rarity in cards:
        for key, value in cards[rarity].items():
            for i in value:
                collection[i] = {
                    "rarity": rarity,
                    "pack": key,
                    "count": 0
                }
    return collection


def get_pack_rarity():
    r = random.random()
    if r < 0.0005:
        return "rare"
    else:
        return "regular"


def open_pack(pack_name):
    pack_cards = []
    pack_rarity = get_pack_rarity()
    pack_info = packs[pack_name]
    num_cards_pack = len(pack_odds[pack_rarity])
    random_numbers = [random.random() for _ in range(num_cards_pack)]
    for i in range(num_cards_pack):
        odds = pack_odds[pack_rarity][i + 1]
        cumulative_probability = 0.0
        for rarity, chance in odds.items():
            cumulative_probability += chance
            if random_numbers[i] < cumulative_probability:
                possible_cards = pack_info[rarity]
                picked_card = random.choice(possible_cards)
                pack_cards.append(picked_card)
                break
    return pack_cards


def complete_collection():
    from collections import defaultdict

    collection = get_empty_collection()
    packs_opened = 0

    # Initialize missing cards per pack using sets for O(1) operations
    missing_per_pack = defaultdict(set)
    all_missing = set()

    for card_num, card_info in collection.items():
        pack = card_info["pack"]
        if card_info["count"] == 0:
            missing_per_pack[pack].add(card_num)
            all_missing.add(card_num)

    # Function to process opened pack
    def process_pack(pack_name):
        nonlocal packs_opened
        pack_cards = open_pack(pack_name)
        packs_opened += 1
        for card in pack_cards:
            if collection[card]["count"] == 0:
                collection[card]["count"] += 1
                # Remove from specific pack's missing set
                pack_of_card = collection[card]["pack"]
                if card in missing_per_pack[pack_of_card]:
                    missing_per_pack[pack_of_card].remove(card)
                # Remove from all missing if no longer missing
                all_missing.discard(card)
            else:
                collection[card]["count"] += 1

    # Complete each pack individually
    for pack in packs:
        while missing_per_pack[pack]:
            process_pack(pack)
        print(f"{pack.capitalize()} completed. Packs opened: {packs_opened}")

    # Complete all remaining missing cards
    while all_missing:
        process_pack("mewtwo")
    print(f"All cards completed. Packs opened: {packs_opened}")

    return packs_opened


def get_avg_packs_to_complete(simulations=500):
    total_packs = 0
    max_packs = 0
    min_packs = math.inf
    num_packs_list = []

    for i in range(simulations):
        num_packs = complete_collection()
        num_packs_list.append(num_packs)
        total_packs += num_packs
        if num_packs > max_packs:
            max_packs = num_packs
        if num_packs < min_packs:
            min_packs = num_packs

    avg_packs = total_packs / simulations
    
    # Define bins in increments of 1000 from 0 to max_packs
    bin_size = 200
    bins = np.arange(0, max_packs + bin_size, bin_size)

    # Calculate frequencies for each bin
    frequencies, _ = np.histogram(num_packs_list, bins=bins)
    bin_centers = bins[:-1] + bin_size / 2  # Center of each bin for plotting

    # Plotting the line graph with a dark theme
    plt.figure(figsize=(10, 6), facecolor='#222222')
    plt.plot(bin_centers, frequencies, linestyle='-', color='#1f77b4', linewidth=2)

    # Dark theme modifications
    plt.gca().set_facecolor('#222222')  # Set the plot background color
    plt.xlabel('Opened packs', color='white')
    plt.ylabel('Frequency', color='white')
    plt.title(f'Packs opened to get all different cards ({simulations} simulations)', color='white')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)

    # Add the average text in the top right corner with a distinct background
    plt.text(
        0.95, 0.95, f"Average: {round(avg_packs)} packs (≈${round(0.8695*avg_packs)})", 
        transform=plt.gca().transAxes, 
        ha='right', va='top', 
        fontsize=12, color='white',
        bbox=dict(facecolor='#444444', alpha=0.8, edgecolor='none')
    )

    # Change the color of ticks
    plt.xticks(color='white')
    plt.yticks(color='white')
    
    plt.show()
    
    return avg_packs, max_packs, min_packs




def main():
    create_cards()
    create_packs()
    collection = get_empty_collection()

    avg_packs, max_packs, min_packs = get_avg_packs_to_complete()
    print("\nResults:")
    print(f"Avg packs to complete collection: {avg_packs} (${0.14491304347*avg_packs})")
    print(f"Max packs to complete collection: {max_packs}")
    print(f"Min packs to complete collection: {min_packs}")


main()