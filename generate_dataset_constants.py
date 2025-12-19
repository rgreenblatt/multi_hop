import json
from typing import Counter

# =============================================================================
# FACT TABLES
# =============================================================================

# Elements and atomic numbers (using elements 10-100, excluding first 9 for easier ones)
ELEMENTS_ALL = REMOVED

ELEMENTS_FILTERED = {k: v for k, v in ELEMENTS_ALL.items() if 11 <= v <= 100}
NUM_TO_ELEMENT = {v: k for k, v in ELEMENTS_ALL.items()}

# Miss America winners by year (1921-2024)
MISS_AMERICA = REMOVED

# Academy Award Best Actor winners by year (1935-2024)
OSCAR_BEST_ACTOR = REMOVED

# Oscar Best Actor birth years
OSCAR_BEST_ACTOR_BIRTH_YEAR = REMOVED

# Oscar Best Actor death years (only for those who have died)
OSCAR_BEST_ACTOR_DEATH_YEAR = REMOVED

# Oscar Best Actor birth day of month
OSCAR_BEST_ACTOR_BIRTH_DAY = REMOVED

# Oscar Best Actor by order (1st winner = 1941, 2nd = 1942, etc.)
OSCAR_BEST_ACTOR_BY_ORDER = REMOVED

# Oscar Best Actress winners by year
OSCAR_BEST_ACTRESS = REMOVED

# Oscar Best Actress birth years
OSCAR_BEST_ACTRESS_BIRTH_YEAR = REMOVED

# Oscar Best Actress birth day of month
OSCAR_BEST_ACTRESS_BIRTH_DAY = REMOVED

# Oscar Best Actress by order (starting from ceremony 10)
OSCAR_BEST_ACTRESS_BY_ORDER = REMOVED

# Oscar Best Supporting Actor winners by year
OSCAR_BEST_SUPPORTING_ACTOR = REMOVED

# Oscar Best Supporting Actor birth years
OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR = REMOVED

# Oscar Best Supporting Actor birth day of month
OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY = REMOVED

# Oscar Best Supporting Actor by order (starting from ceremony 10)
OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER = REMOVED

# Oscar Best Supporting Actress winners by year
OSCAR_BEST_SUPPORTING_ACTRESS = REMOVED

# Oscar Best Supporting Actress birth years
OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR = REMOVED

# Oscar Best Supporting Actress birth day of month
OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY = REMOVED

# Oscar Best Supporting Actress by order (starting from ceremony 10)
OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER = REMOVED

# Nobel Prize in Peace (single winners only)
NOBEL_PEACE = REMOVED

# Nobel Prize in Peace birth years (individual winners only)
NOBEL_PEACE_BIRTH_YEAR = REMOVED

# Nobel Prize in Peace birth day of month (individual winners only)
NOBEL_PEACE_BIRTH_DAY = REMOVED

# Nobel Prize in Chemistry (single winners only)
NOBEL_CHEMISTRY = REMOVED

# Nobel Prize in Chemistry birth years (single winners only)
NOBEL_CHEMISTRY_BIRTH_YEAR = REMOVED

# Nobel Prize in Chemistry birth day of month (single winners only)
NOBEL_CHEMISTRY_BIRTH_DAY = REMOVED

# Nobel Prize in Physics (single winners only)
NOBEL_PHYSICS = REMOVED

# Nobel Prize in Physics birth years (single winners only)
NOBEL_PHYSICS_BIRTH_YEAR = REMOVED

# Nobel Prize in Physics birth day of month (single winners only)
NOBEL_PHYSICS_BIRTH_DAY = REMOVED

# Nobel Prize in Literature (single winners only)
NOBEL_LITERATURE = REMOVED

# Nobel Prize in Literature birth years (single winners only)
NOBEL_LITERATURE_BIRTH_YEAR = REMOVED

# Nobel Prize in Literature birth day of month (single winners only)
NOBEL_LITERATURE_BIRTH_DAY = REMOVED

# US State flowers
US_STATE_FLOWERS = REMOVED

# US House of Representatives seats by state (post-2020 census apportionment)
US_STATE_HOUSE_SEATS = REMOVED

# State legislature lower chamber seats by state
US_STATE_LEGISLATURE_HOUSE_SEATS = REMOVED

# US House of Representatives seats facts (for multi-hop questions)
US_HOUSE_SEATS_FACTS = [
    {
        "question": f"How many representatives does {state} have in the US House of Representatives?",
        "answer": seats,
        "category": "Politics",
    }
    for state, seats in US_STATE_HOUSE_SEATS.items()
]

# State legislature lower house seats facts (for multi-hop questions)
STATE_LEGISLATURE_HOUSE_SEATS_FACTS = [
    {
        "question": f"How many seats are in the lower house of {state}'s state legislature?",
        "answer": seats,
        "category": "Politics",
    }
    for state, seats in US_STATE_LEGISLATURE_HOUSE_SEATS.items()
]

# US State order joined union (1-50)
US_STATE_ORDER_JOINED = {
    "Delaware": 1,
    "Pennsylvania": 2,
    "New Jersey": 3,
    "Georgia": 4,
    "Connecticut": 5,
    "Massachusetts": 6,
    "Maryland": 7,
    "South Carolina": 8,
    "New Hampshire": 9,
    "Virginia": 10,
    "New York": 11,
    "North Carolina": 12,
    "Rhode Island": 13,
    "Vermont": 14,
    "Kentucky": 15,
    "Tennessee": 16,
    "Ohio": 17,
    "Louisiana": 18,
    "Indiana": 19,
    "Mississippi": 20,
    "Illinois": 21,
    "Alabama": 22,
    "Maine": 23,
    "Missouri": 24,
    "Arkansas": 25,
    "Michigan": 26,
    "Florida": 27,
    "Texas": 28,
    "Iowa": 29,
    "Wisconsin": 30,
    "California": 31,
    "Minnesota": 32,
    "Oregon": 33,
    "Kansas": 34,
    "West Virginia": 35,
    "Nevada": 36,
    "Nebraska": 37,
    "Colorado": 38,
    "North Dakota": 39,
    "South Dakota": 40,
    "Montana": 41,
    "Washington": 42,
    "Idaho": 43,
    "Wyoming": 44,
    "Utah": 45,
    "Oklahoma": 46,
    "New Mexico": 47,
    "Arizona": 48,
    "Alaska": 49,
    "Hawaii": 50,
}

# Reverse mapping: order number -> state name
US_STATE_BY_ORDER = {order: state for state, order in US_STATE_ORDER_JOINED.items()}

US_STATE_TO_COUNTIES = {
    "Alabama": 67,
    "Alaska": 29,  # 19 organized boroughs + 1 unorganized borough divided into census areas
    "Arizona": 15,
    "Arkansas": 75,
    "California": 58,
    "Colorado": 64,
    "Connecticut": 8,
    "Delaware": 3,
    "Florida": 67,
    "Georgia": 159,
    "Hawaii": 5,
    "Idaho": 44,
    "Illinois": 102,
    "Indiana": 92,
    "Iowa": 99,
    "Kansas": 105,
    "Kentucky": 120,
    "Louisiana": 64,  # parishes
    "Maine": 16,
    "Maryland": 24,  # 23 counties + 1 independent city (Baltimore)
    "Massachusetts": 14,
    "Michigan": 83,
    "Minnesota": 87,
    "Mississippi": 82,
    "Missouri": 115,  # 114 counties + 1 independent city (St. Louis)
    "Montana": 56,
    "Nebraska": 93,
    "Nevada": 17,  # 16 counties + 1 independent city (Carson City)
    "New Hampshire": 10,
    "New Jersey": 21,
    "New Mexico": 33,
    "New York": 62,
    "North Carolina": 100,
    "North Dakota": 53,
    "Ohio": 88,
    "Oklahoma": 77,
    "Oregon": 36,
    "Pennsylvania": 67,
    "Rhode Island": 5,
    "South Carolina": 46,
    "South Dakota": 66,
    "Tennessee": 95,
    "Texas": 254,
    "Utah": 29,
    "Vermont": 14,
    "Virginia": 133,  # 95 counties + 38 independent cities
    "Washington": 39,
    "West Virginia": 55,
    "Wisconsin": 72,
    "Wyoming": 23,
}

counts_of_county_numbers = Counter(US_STATE_TO_COUNTIES.values())
COUNTIES_TO_US_STATE = {v: k for k, v in US_STATE_TO_COUNTIES.items() if counts_of_county_numbers[v] == 1}


# Day of month each state joined the union
US_STATE_JOINED_DAY = {
    "Delaware": 7,
    "Pennsylvania": 12,
    "New Jersey": 18,
    "Georgia": 2,
    "Connecticut": 9,
    "Massachusetts": 6,
    "Maryland": 28,
    "South Carolina": 23,
    "New Hampshire": 21,
    "Virginia": 25,
    "New York": 26,
    "North Carolina": 21,
    "Rhode Island": 29,
    "Vermont": 4,
    "Kentucky": 1,
    "Tennessee": 1,
    "Ohio": 1,
    "Louisiana": 30,
    "Indiana": 11,
    "Mississippi": 10,
    "Illinois": 3,
    "Alabama": 14,
    "Maine": 15,
    "Missouri": 10,
    "Arkansas": 15,
    "Michigan": 26,
    "Florida": 3,
    "Texas": 29,
    "Iowa": 28,
    "Wisconsin": 29,
    "California": 9,
    "Minnesota": 11,
    "Oregon": 14,
    "Kansas": 29,
    "West Virginia": 20,
    "Nevada": 31,
    "Nebraska": 1,
    "Colorado": 1,
    "North Dakota": 2,
    "South Dakota": 2,
    "Montana": 8,
    "Washington": 11,
    "Idaho": 3,
    "Wyoming": 10,
    "Utah": 4,
    "Oklahoma": 16,
    "New Mexico": 6,
    "Arizona": 14,
    "Alaska": 3,
    "Hawaii": 21,
}

# US State mottos
US_STATE_MOTTOS = {
    "Alabama": "We Dare Defend Our Rights",
    "Alaska": "North to the Future",
    "Arizona": "Ditat Deus",
    "Arkansas": "Regnat Populus",
    "California": "Eureka",
    "Colorado": "Nil Sine Numine",
    "Connecticut": "Qui Transtulit Sustinet",
    "Delaware": "Liberty and Independence",
    "Florida": "In God We Trust",
    "Georgia": "Wisdom, Justice, and Moderation",
    "Hawaii": "Ua Mau ke Ea o ka Aina i ka Pono",
    "Idaho": "Esto Perpetua",
    "Illinois": "State Sovereignty, National Union",
    "Indiana": "The Crossroads of America",
    "Iowa": "Our Liberties We Prize and Our Rights We Will Maintain",
    "Kansas": "Ad Astra per Aspera",
    "Kentucky": "United We Stand, Divided We Fall",
    "Louisiana": "Union, Justice, and Confidence",
    "Maine": "Dirigo",
    "Maryland": "Fatti Maschii, Parole Femine",
    "Massachusetts": "Ense Petit Placidam Sub Libertate Quietem",
    "Michigan": "Si Quaeris Peninsulam Amoenam Circumspice",
    "Minnesota": "L'Étoile du Nord",
    "Mississippi": "Virtute et Armis",
    "Missouri": "Salus Populi Suprema Lex Esto",
    "Montana": "Oro y Plata",
    "Nebraska": "Equality Before the Law",
    "Nevada": "All for Our Country",
    "New Hampshire": "Live Free or Die",
    "New Jersey": "Liberty and Prosperity",
    "New Mexico": "Crescit Eundo",
    "New York": "Excelsior",
    "North Carolina": "Esse Quam Videri",
    "North Dakota": "Liberty and Union Now and Forever, One and Inseparable",
    "Ohio": "With God All Things Are Possible",
    "Oklahoma": "Labor Omnia Vincit",
    "Oregon": "Alis Volat Propriis",
    "Pennsylvania": "Virtue, Liberty, and Independence",
    "Rhode Island": "Hope",
    "South Carolina": "Dum Spiro Spero",
    "South Dakota": "Under God the People Rule",
    "Tennessee": "Agriculture and Commerce",
    "Texas": "Friendship",
    "Utah": "Industry",
    "Vermont": "Freedom and Unity",
    "Virginia": "Sic Semper Tyrannis",
    "Washington": "Al-ki",
    "West Virginia": "Montani Semper Liberi",
    "Wisconsin": "Forward",
    "Wyoming": "Equal Rights",
    "District of Columbia": "Justitia Omnibus",
}


# Load facts
with open("data/age_facts.json") as f:
    AGE_FACTS = json.load(f)
    AGE_FACTS = [
        fact
        for fact in AGE_FACTS
        if all(x not in fact["question"] for x in ["Agnes Pockels", "Antonín Dvořák", "Fred Sersen", "L. B. Abbott"])
    ]
with open("data/static_facts.json") as f:
    STATIC_FACTS = json.load(f)

# Create mappings by answer value for quick lookup
AGE_FACTS_BY_VALUE = {}
for fact in AGE_FACTS:
    val = fact["answer"]
    if val not in AGE_FACTS_BY_VALUE:
        AGE_FACTS_BY_VALUE[val] = []
    AGE_FACTS_BY_VALUE[val].append(fact)

STATIC_FACTS_BY_VALUE = {}
for fact in STATIC_FACTS:
    val = fact["answer"]
    if val not in STATIC_FACTS_BY_VALUE:
        STATIC_FACTS_BY_VALUE[val] = []
    STATIC_FACTS_BY_VALUE[val].append(fact)


def generate_single_hop_questions():
    """Generate all single-hop fact questions for verification.

    Returns a dict mapping fact_type -> list of (question, answer) tuples.
    """
    single_hops = {}

    # Element atomic numbers
    single_hops["element_atomic_number"] = [
        (f"What is the atomic number of {element}?", atomic_num) for element, atomic_num in ELEMENTS_ALL.items()
    ]

    # State order joined union
    single_hops["state_order"] = [
        (f"What number state was {state} when that state joined the union?", order)
        for state, order in US_STATE_ORDER_JOINED.items()
    ]

    # State by order (reverse mapping)
    single_hops["order_state"] = [
        (f"What US state was number {order} to join the union?", state) for order, state in US_STATE_BY_ORDER.items()
    ]

    # State mottos
    single_hops["state_motto"] = [
        (f"What is the state motto of {state}?", motto) for state, motto in US_STATE_MOTTOS.items()
    ]

    # State flowers
    single_hops["state_flower"] = [
        (f"What is the state flower of {state}?", flower) for state, flower in US_STATE_FLOWERS.items()
    ]

    single_hops["state_num_counties"] = [
        (f"How many county-equivalents are in {state}?", counties) for state, counties in US_STATE_TO_COUNTIES.items()
    ]

    # single_hops["counties_state"] = [
    #     (f"Which state has {counties} county-equivalents?", state) for counties, state in COUNTIES_TO_US_STATE.items()
    # ]

    # State joined day
    single_hops["state_joined_day"] = [
        (f"On what day of the month did {state} join the union?", day) for state, day in US_STATE_JOINED_DAY.items()
    ]

    # State House of Representatives seats
    single_hops["state_house_seats"] = [
        (f"How many representatives does {state} have in the US House of Representatives?", seats)
        for state, seats in US_STATE_HOUSE_SEATS.items()
    ]

    # State legislature house seats
    single_hops["state_legislature_house_seats"] = [
        (f"How many seats are in the lower house of {state}'s state legislature?", seats)
        for state, seats in US_STATE_LEGISLATURE_HOUSE_SEATS.items()
    ]

    # Miss America by year
    single_hops["year_miss_america"] = [
        (f"Who was Miss America for {year}?", winner) for year, winner in MISS_AMERICA.items()
    ]

    # # Miss America birth years
    # single_hops["miss_america_birth_year"] = [
    #     (f"In what year was {winner} born?", year)
    #     for winner, year in MISS_AMERICA_BIRTH_YEAR.items()
    # ]

    # Oscar Best Actor by year
    single_hops["year_oscar_best_actor"] = [
        (f"Who won the Academy Award for Best Actor for a film released in {year}?", actor)
        for year, actor in OSCAR_BEST_ACTOR.items()
    ]

    # Oscar Best Actor birth years
    single_hops["oscar_best_actor_birth_year"] = [
        (f"In what year was {actor} born?", year) for actor, year in OSCAR_BEST_ACTOR_BIRTH_YEAR.items()
    ]

    # Oscar Best Actor death years
    single_hops["oscar_best_actor_death_year"] = [
        (f"In what year did {actor} die?", year) for actor, year in OSCAR_BEST_ACTOR_DEATH_YEAR.items()
    ]

    # Oscar Best Actor birth day of month
    single_hops["oscar_best_actor_birth_day"] = [
        (f"On what day of the month was {actor} born?", day) for actor, day in OSCAR_BEST_ACTOR_BIRTH_DAY.items()
    ]

    # Oscar Best Actor by order
    single_hops["oscar_best_actor_by_order"] = [
        (
            f"Who won best actor at the {order}{['st', 'nd', 'rd'][order-1] if order <= 3 else 'th'} Academy Awards?",
            actor,
        )
        for order, actor in OSCAR_BEST_ACTOR_BY_ORDER.items()
    ]

    # Oscar Best Actress by year
    single_hops["year_oscar_best_actress"] = [
        (f"Who won the Academy Award for Best Actress for a film released in {year}?", actress)
        for year, actress in OSCAR_BEST_ACTRESS.items()
    ]

    # Oscar Best Actress birth years
    single_hops["oscar_best_actress_birth_year"] = [
        (f"In what year was {actress} born?", year) for actress, year in OSCAR_BEST_ACTRESS_BIRTH_YEAR.items()
    ]

    # Oscar Best Actress birth day of month
    single_hops["oscar_best_actress_birth_day"] = [
        (f"On what day of the month was {actress} born?", day) for actress, day in OSCAR_BEST_ACTRESS_BIRTH_DAY.items()
    ]

    # Oscar Best Actress by order
    single_hops["oscar_best_actress_by_order"] = [
        (
            f"Who won best actress at the {order}{['st', 'nd', 'rd'][order-1] if order <= 3 else 'th'} Academy Awards?",
            actress,
        )
        for order, actress in OSCAR_BEST_ACTRESS_BY_ORDER.items()
    ]

    # Oscar Best Supporting Actor by year
    single_hops["year_oscar_best_supporting_actor"] = [
        (f"Who won the Academy Award for Best Supporting Actor for a film released in {year}?", actor)
        for year, actor in OSCAR_BEST_SUPPORTING_ACTOR.items()
    ]

    # Oscar Best Supporting Actor birth years
    single_hops["oscar_best_supporting_actor_birth_year"] = [
        (f"In what year was {actor} born?", year) for actor, year in OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR.items()
    ]

    # Oscar Best Supporting Actor birth day of month
    single_hops["oscar_best_supporting_actor_birth_day"] = [
        (f"On what day of the month was {actor} born?", day) for actor, day in OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY.items()
    ]

    # Oscar Best Supporting Actor by order
    single_hops["oscar_best_supporting_actor_by_order"] = [
        (
            f"Who won best supporting actor at the {order}{['st', 'nd', 'rd'][order-1] if order <= 3 else 'th'} Academy Awards?",
            actor,
        )
        for order, actor in OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER.items()
    ]

    # Oscar Best Supporting Actress by year
    single_hops["year_oscar_best_supporting_actress"] = [
        (f"Who won the Academy Award for Best Supporting Actress for a film released in {year}?", actress)
        for year, actress in OSCAR_BEST_SUPPORTING_ACTRESS.items()
    ]

    # Oscar Best Supporting Actress birth years
    single_hops["oscar_best_supporting_actress_birth_year"] = [
        (f"In what year was {actress} born?", year) for actress, year in OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR.items()
    ]

    # Oscar Best Supporting Actress birth day of month
    single_hops["oscar_best_supporting_actress_birth_day"] = [
        (f"On what day of the month was {actress} born?", day) for actress, day in OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY.items()
    ]

    # Oscar Best Supporting Actress by order
    single_hops["oscar_best_supporting_actress_by_order"] = [
        (
            f"Who won best supporting actress at the {order}{['st', 'nd', 'rd'][order-1] if order <= 3 else 'th'} Academy Awards?",
            actress,
        )
        for order, actress in OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER.items()
    ]

    # Nobel Prize in Peace by year
    single_hops["year_nobel_peace"] = [
        (f"Who won the Nobel Peace Prize in {year}?", winner) for year, winner in NOBEL_PEACE.items()
    ]

    # Nobel Prize in Peace birth years
    single_hops["nobel_peace_birth_year"] = [
        (f"In what year was {winner} born?", year) for winner, year in NOBEL_PEACE_BIRTH_YEAR.items()
    ]

    # Nobel Prize in Peace birth day of month
    single_hops["nobel_peace_birth_day"] = [
        (f"On what day of the month was {winner} born?", day) for winner, day in NOBEL_PEACE_BIRTH_DAY.items()
    ]

    # Nobel Prize in Chemistry by year
    single_hops["year_nobel_chemistry"] = [
        (f"Who won the Nobel Prize in Chemistry in {year}?", winner) for year, winner in NOBEL_CHEMISTRY.items()
    ]

    # Nobel Prize in Chemistry birth years
    single_hops["nobel_chemistry_birth_year"] = [
        (f"In what year was {winner} born?", year) for winner, year in NOBEL_CHEMISTRY_BIRTH_YEAR.items()
    ]

    # Nobel Prize in Chemistry birth day of month
    single_hops["nobel_chemistry_birth_day"] = [
        (f"On what day of the month was {winner} born?", day) for winner, day in NOBEL_CHEMISTRY_BIRTH_DAY.items()
    ]

    # Nobel Prize in Physics by year
    single_hops["year_nobel_physics"] = [
        (f"Who won the Nobel Prize in Physics in {year}?", winner) for year, winner in NOBEL_PHYSICS.items()
    ]

    # Nobel Prize in Physics birth years
    single_hops["nobel_physics_birth_year"] = [
        (f"In what year was {winner} born?", year) for winner, year in NOBEL_PHYSICS_BIRTH_YEAR.items()
    ]

    # Nobel Prize in Physics birth day of month
    single_hops["nobel_physics_birth_day"] = [
        (f"On what day of the month was {winner} born?", day) for winner, day in NOBEL_PHYSICS_BIRTH_DAY.items()
    ]

    # Nobel Prize in Literature by year
    single_hops["year_nobel_literature"] = [
        (f"Who won the Nobel Prize in Literature in {year}?", winner) for year, winner in NOBEL_LITERATURE.items()
    ]

    # Nobel Prize in Literature birth years
    single_hops["nobel_literature_birth_year"] = [
        (f"In what year was {winner} born?", year) for winner, year in NOBEL_LITERATURE_BIRTH_YEAR.items()
    ]

    # Nobel Prize in Literature birth day of month
    single_hops["nobel_literature_birth_day"] = [
        (f"On what day of the month was {winner} born?", day) for winner, day in NOBEL_LITERATURE_BIRTH_DAY.items()
    ]

    # Age facts
    single_hops["age_fact"] = [(fact["question"], fact["answer"]) for fact in AGE_FACTS]

    # Static facts
    single_hops["static_fact"] = [(fact["question"], fact["answer"]) for fact in STATIC_FACTS]

    return single_hops


# =============================================================================
# MAPPING REGISTRY
# =============================================================================
# Registry mapping each mapping_id to its dict and descriptive title.
# Used for including lookup tables in evaluation prompts.


def get_mapping_registry():
    """
    Returns a dict mapping mapping_id -> {"data": dict, "title": str}.
    The data dict maps keys to values for the lookup.
    """
    registry = {}

    # Element mappings
    registry["element_to_atomic_number"] = {
        "data": ELEMENTS_ALL,
        "title": "Element Name to Atomic Number",
    }
    registry["atomic_number_to_element"] = {
        "data": NUM_TO_ELEMENT,
        "title": "Atomic Number to Element Name",
    }

    # US State order mappings
    registry["state_order_to_state"] = {
        "data": US_STATE_BY_ORDER,
        "title": "Order Joined Union to US State",
    }

    # US State property mappings
    registry["state_to_flower"] = {
        "data": US_STATE_FLOWERS,
        "title": "US State to State Flower",
    }
    registry["state_to_motto"] = {
        "data": US_STATE_MOTTOS,
        "title": "US State to State Motto",
    }
    registry["state_to_counties"] = {
        "data": US_STATE_TO_COUNTIES,
        "title": "US State to Number of County-Equivalents",
    }

    # Miss America mappings
    registry["year_to_miss_america"] = {
        "data": MISS_AMERICA,
        "title": "Year to Miss America Winner",
    }

    # Oscar Best Actor mappings
    registry["year_to_oscar_best_actor"] = {
        "data": OSCAR_BEST_ACTOR,
        "title": "Year to Oscar Best Actor Winner",
    }
    registry["oscar_best_actor_to_birth_year"] = {
        "data": OSCAR_BEST_ACTOR_BIRTH_YEAR,
        "title": "Oscar Best Actor to Birth Year",
    }
    registry["oscar_best_actor_to_birth_day"] = {
        "data": OSCAR_BEST_ACTOR_BIRTH_DAY,
        "title": "Oscar Best Actor to Birth Day of Month",
    }
    registry["order_to_oscar_best_actor"] = {
        "data": OSCAR_BEST_ACTOR_BY_ORDER,
        "title": "Academy Awards Number to Best Actor Winner",
    }

    # Oscar Best Actress mappings
    registry["year_to_oscar_best_actress"] = {
        "data": OSCAR_BEST_ACTRESS,
        "title": "Year to Oscar Best Actress Winner",
    }
    registry["oscar_best_actress_to_birth_year"] = {
        "data": OSCAR_BEST_ACTRESS_BIRTH_YEAR,
        "title": "Oscar Best Actress to Birth Year",
    }
    registry["oscar_best_actress_to_birth_day"] = {
        "data": OSCAR_BEST_ACTRESS_BIRTH_DAY,
        "title": "Oscar Best Actress to Birth Day of Month",
    }
    registry["order_to_oscar_best_actress"] = {
        "data": OSCAR_BEST_ACTRESS_BY_ORDER,
        "title": "Academy Awards Number to Best Actress Winner",
    }

    # Oscar Best Supporting Actor mappings
    registry["year_to_oscar_best_supporting_actor"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTOR,
        "title": "Year to Oscar Best Supporting Actor Winner",
    }
    registry["oscar_best_supporting_actor_to_birth_year"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR,
        "title": "Oscar Best Supporting Actor to Birth Year",
    }
    registry["oscar_best_supporting_actor_to_birth_day"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY,
        "title": "Oscar Best Supporting Actor to Birth Day of Month",
    }
    registry["order_to_oscar_best_supporting_actor"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER,
        "title": "Academy Awards Number to Best Supporting Actor Winner",
    }

    # Oscar Best Supporting Actress mappings
    registry["year_to_oscar_best_supporting_actress"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTRESS,
        "title": "Year to Oscar Best Supporting Actress Winner",
    }
    registry["oscar_best_supporting_actress_to_birth_year"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR,
        "title": "Oscar Best Supporting Actress to Birth Year",
    }
    registry["oscar_best_supporting_actress_to_birth_day"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY,
        "title": "Oscar Best Supporting Actress to Birth Day of Month",
    }
    registry["order_to_oscar_best_supporting_actress"] = {
        "data": OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER,
        "title": "Academy Awards Number to Best Supporting Actress Winner",
    }

    # Nobel Peace Prize mappings
    registry["year_to_nobel_peace"] = {
        "data": NOBEL_PEACE,
        "title": "Year to Nobel Peace Prize Winner",
    }
    registry["nobel_peace_to_birth_year"] = {
        "data": NOBEL_PEACE_BIRTH_YEAR,
        "title": "Nobel Peace Prize Winner to Birth Year",
    }
    registry["nobel_peace_to_birth_day"] = {
        "data": NOBEL_PEACE_BIRTH_DAY,
        "title": "Nobel Peace Prize Winner to Birth Day of Month",
    }

    # Nobel Chemistry Prize mappings
    registry["year_to_nobel_chemistry"] = {
        "data": NOBEL_CHEMISTRY,
        "title": "Year to Nobel Prize in Chemistry Winner",
    }
    registry["nobel_chemistry_to_birth_year"] = {
        "data": NOBEL_CHEMISTRY_BIRTH_YEAR,
        "title": "Nobel Chemistry Winner to Birth Year",
    }
    registry["nobel_chemistry_to_birth_day"] = {
        "data": NOBEL_CHEMISTRY_BIRTH_DAY,
        "title": "Nobel Chemistry Winner to Birth Day of Month",
    }

    # Nobel Physics Prize mappings
    registry["year_to_nobel_physics"] = {
        "data": NOBEL_PHYSICS,
        "title": "Year to Nobel Prize in Physics Winner",
    }
    registry["nobel_physics_to_birth_year"] = {
        "data": NOBEL_PHYSICS_BIRTH_YEAR,
        "title": "Nobel Physics Winner to Birth Year",
    }
    registry["nobel_physics_to_birth_day"] = {
        "data": NOBEL_PHYSICS_BIRTH_DAY,
        "title": "Nobel Physics Winner to Birth Day of Month",
    }

    # Nobel Literature Prize mappings
    registry["year_to_nobel_literature"] = {
        "data": NOBEL_LITERATURE,
        "title": "Year to Nobel Prize in Literature Winner",
    }
    registry["nobel_literature_to_birth_year"] = {
        "data": NOBEL_LITERATURE_BIRTH_YEAR,
        "title": "Nobel Literature Winner to Birth Year",
    }
    registry["nobel_literature_to_birth_day"] = {
        "data": NOBEL_LITERATURE_BIRTH_DAY,
        "title": "Nobel Literature Winner to Birth Day of Month",
    }

    # Age facts (question -> answer)
    registry["age_facts"] = {
        "data": {fact["question"]: fact["answer"] for fact in AGE_FACTS},
        "title": "Age-Related Facts",
    }

    # Static facts (question -> answer)
    registry["static_facts"] = {
        "data": {fact["question"]: fact["answer"] for fact in STATIC_FACTS},
        "title": "Static Facts",
    }

    # US House seats facts
    registry["us_house_seats"] = {
        "data": US_STATE_HOUSE_SEATS,
        "title": "US State to House of Representatives Seats",
    }

    # State legislature house seats
    registry["state_legislature_house_seats"] = {
        "data": US_STATE_LEGISLATURE_HOUSE_SEATS,
        "title": "US State to State Legislature Lower House Seats",
    }

    return registry


# Export a singleton for convenience
MAPPING_REGISTRY = get_mapping_registry()
