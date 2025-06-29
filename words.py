import random

WORDS_BY_DIFFICULTY = {
    "easy": [
        # Level 1
        "Sunflower", "Fruits", "Camera", "Liquid", "Book", "Ocean", "Apple", "Planet",
        "Baby", "Pail", "Cabbage", "Towel", "Eyeglasses", "Pumpkins", "Tree", "Breakfast",
        "Stairs", "White", "Stirrup", "Beach",
        # Level 2
        "Berries", "Lemurs", "Knife", "Dessert", "Winter", "Flames", "Gymnastics", "Wedding",
        "Skates", "Pipe", "Peony", "Storm", "Chocolate", "Pineapple", "Cloud", "Glass",
        "Strawberry", "Mushrooms", "Broccoli", "Sun",
        # Level 3
        "Straw", "Figurines", "Scarf", "Thought", "Wallet", "Hedgehog", "Window", "Vitamins",
        "Spices", "Groundnut", "Equilibrium", "Door", "Nebula", "Banana", "Smile", "Wheel",
        "Tea", "Bear", "Nautilus", "Tuber",
        # Level 4
        "Lavender", "Snow", "Castle", "Police", "Knowledge", "Pizza", "Ink", "Bed",
        "Selfie", "Strings", "Eclipse", "Letter", "Tin", "Embers", "Balloon", "Foot",
        "Caviar",
    ],
    "medium": [
        # Level 9
        "Strawberry", "Kiss", "Feet", "Waist", "Candle", "Trumpet", "Pond", "Exotic",
        "Landmark", "Green", "Bridge", "Clothes", "Root", "Flatiron", "Artichoke", "Fountain",
        "Atlas", "Christmas", "Eiffel", "Artist",
        # Level 10
        "Supplies", "Dragonfly", "Pendulum", "Book", "Gift", "Vanilla", "Egypt", "Horse",
        "Two", "Mustard", "Puppy", "Purée", "Rust", "Stripes", "Stick", "Programming",
        "City", "Structure", "Heart", "Result",
        # Level 11
        "Dragon", "Potter", "Predator", "Western", "Sky", "Roof", "Indoor", "Bite",
        "Spiral", "Ornithology", "Nest", "Carbohydrate", "Twin", "Wings", "Grass", "Seeds",
        "Chair", "Corset", "Signs", "Fruit",
        # Level 12
        "Honeycomb", "Face", "Chain", "Sweet", "Stunt", "Back", "Agriculture", "Beans",
        "Sauce", "Knitting", "Waves", "Fur", "Transparency", "Aerial", "Square", "Tail",
        "Ferns", "Enclosure", "Cake", "White",
    ],
    "hard": [
        # Level 13
        "Tombstone", "Dress", "Windy", "Poppy", "Skin", "Crystal", "Train", "Belief",
        "Pasta", "Shed", "Whiskers", "Roof",
        # Level 18
        "Florist", "Kitchen", "Stalactite", "Apple", "Russia", "Cherry", "Door", "Tomato",
        "Packaging", "Bakery", "Temperature", "Hair", "Souvenirs", "Pouring", "Fog", "Champagne",
        "Fig", "Harp", "Surf", "Rice",
        # Level 19
        "Archive", "Macaron", "Insect", "Solo", "Horse", "Ribs", "Longship", "Rodent",
        "Thinking", "England", "Carrot", "Pocket", "Gnome", "Olive", "Capacitor", "Farm",
        "Childhood", "Copper", "Cross", "Kitchen",
        # Level 20
        "Danger", "Future", "Mane", "Gymnastics", "Pattern", "Probability", "Professional", "Moon",
        "Hat", "Graffiti", "Cards", "Shorts", "Space", "Star", "Music", "Takeoff",
        "Surface", "Bird", "Tradition", "Visor",
    ]
}

def get_random_word(difficulty: str) -> str:
    """
    Returns a random word from the list corresponding to the given difficulty.
    """
    word_list = WORDS_BY_DIFFICULTY.get(difficulty.lower())
    if not word_list:
        # Fallback to easy if difficulty is not found
        word_list = WORDS_BY_DIFFICULTY.get("easy")
    return random.choice(word_list)
