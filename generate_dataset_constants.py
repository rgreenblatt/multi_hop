import json
from typing import Counter

# =============================================================================
# FACT TABLES
# =============================================================================

# Elements and atomic numbers (using elements 10-100, excluding first 9 for easier ones)
ELEMENTS_ALL = {
    "Hydrogen": 1,
    "Helium": 2,
    "Lithium": 3,
    "Beryllium": 4,
    "Boron": 5,
    "Carbon": 6,
    "Nitrogen": 7,
    "Oxygen": 8,
    "Fluorine": 9,
    "Neon": 10,
    "Sodium": 11,
    "Magnesium": 12,
    "Aluminum": 13,
    "Silicon": 14,
    "Phosphorus": 15,
    "Sulfur": 16,
    "Chlorine": 17,
    "Argon": 18,
    "Potassium": 19,
    "Calcium": 20,
    "Scandium": 21,
    "Titanium": 22,
    "Vanadium": 23,
    "Chromium": 24,
    "Manganese": 25,
    "Iron": 26,
    "Cobalt": 27,
    "Nickel": 28,
    "Copper": 29,
    "Zinc": 30,
    "Gallium": 31,
    "Germanium": 32,
    "Arsenic": 33,
    "Selenium": 34,
    "Bromine": 35,
    "Krypton": 36,
    "Rubidium": 37,
    "Strontium": 38,
    "Yttrium": 39,
    "Zirconium": 40,
    "Niobium": 41,
    "Molybdenum": 42,
    "Technetium": 43,
    "Ruthenium": 44,
    "Rhodium": 45,
    "Palladium": 46,
    "Silver": 47,
    "Cadmium": 48,
    "Indium": 49,
    "Tin": 50,
    "Antimony": 51,
    "Tellurium": 52,
    "Iodine": 53,
    "Xenon": 54,
    "Cesium": 55,
    "Barium": 56,
    "Lanthanum": 57,
    "Cerium": 58,
    "Praseodymium": 59,
    "Neodymium": 60,
    "Promethium": 61,
    "Samarium": 62,
    "Europium": 63,
    "Gadolinium": 64,
    "Terbium": 65,
    "Dysprosium": 66,
    "Holmium": 67,
    "Erbium": 68,
    "Thulium": 69,
    "Ytterbium": 70,
    "Lutetium": 71,
    "Hafnium": 72,
    "Tantalum": 73,
    "Tungsten": 74,
    "Rhenium": 75,
    "Osmium": 76,
    "Iridium": 77,
    "Platinum": 78,
    "Gold": 79,
    "Mercury": 80,
    "Thallium": 81,
    "Lead": 82,
    "Bismuth": 83,
    "Polonium": 84,
    "Astatine": 85,
    "Radon": 86,
    "Francium": 87,
    "Radium": 88,
    "Actinium": 89,
    "Thorium": 90,
    "Protactinium": 91,
    "Uranium": 92,
    "Neptunium": 93,
    "Plutonium": 94,
    "Americium": 95,
    "Curium": 96,
    "Berkelium": 97,
    "Californium": 98,
    "Einsteinium": 99,
    "Fermium": 100,
    "Mendelevium": 101,
    "Nobelium": 102,
    "Lawrencium": 103,
    "Rutherfordium": 104,
    "Dubnium": 105,
    "Seaborgium": 106,
    "Bohrium": 107,
    "Hassium": 108,
    "Meitnerium": 109,
    "Darmstadtium": 110,
    "Roentgenium": 111,
    "Copernicium": 112,
    "Nihonium": 113,
    "Flerovium": 114,
    "Moscovium": 115,
    "Livermorium": 116,
    "Tennessine": 117,
    "Oganesson": 118,
}

ELEMENTS_FILTERED = {k: v for k, v in ELEMENTS_ALL.items() if 11 <= v <= 100}
NUM_TO_ELEMENT = {v: k for k, v in ELEMENTS_ALL.items()}

# Miss America winners by year (1921-2024)
MISS_AMERICA = {
    1921: "Margaret Gorman",
    1922: "Mary Katherine Campbell",
    1923: "Mary Katherine Campbell",
    1924: "Ruth Malcomson",
    1925: "Fay Lanphier",
    1926: "Norma Smallwood",
    1927: "Lois Delander",
    1933: "Marian Bergeron",
    1935: "Henrietta Leaver",
    1936: "Rose Coyle",
    1937: "Bette Cooper",
    1938: "Marilyn Meseke",
    1939: "Patricia Donnelly",
    1940: "Frances Burke",
    1941: "Rosemary LaPlanche",
    1942: "Jo-Carroll Dennison",
    1943: "Jean Bartel",
    1944: "Venus Ramey",
    1945: "Bess Myerson",
    1946: "Marilyn Buferd",
    1947: "Barbara Walker",
    1948: "Bebe Shopp",
    1949: "Jacque Mercer",
    1951: "Yolande Betbeze",
    1952: "Colleen Kay Hutchins",
    1953: "Neva Jane Langley",
    1954: "Evelyn Ay",
    1955: "Lee Meriwether",
    1956: "Sharon Ritchie",
    1957: "Marian McKnight",
    1958: "Marilyn Van Derbur",
    1959: "Mary Ann Mobley",
    1960: "Lynda Lee Mead",
    1961: "Nancy Fleming",
    1962: "Maria Fletcher",
    1963: "Jacquelyn Mayer",
    1964: "Donna Axum",
    1965: "Vonda Kay Van Dyke",
    1966: "Deborah Bryant",
    1967: "Jane Jayroe",
    1968: "Debra Barnes",
    1969: "Judith Ford",
    1970: "Pamela Eldred",
    1971: "Phyllis George",
    1972: "Laurie Lea Schaefer",
    1973: "Terry Anne Meeuwsen",
    1974: "Rebecca King",
    1975: "Shirley Cothran",
    1976: "Tawny Godin",
    1977: "Dorothy Benham",
    1978: "Susan Perkins",
    1979: "Kylene Barker",
    1980: "Cheryl Prewitt",
    1981: "Susan Powell",
    1982: "Elizabeth Ward",
    1983: "Debra Maffett",
    1984: "Vanessa Williams",
    1985: "Sharlene Wells",
    1986: "Susan Akin",
    1987: "Kellye Cash",
    1988: "Kaye Lani Rae Rafko",
    1989: "Gretchen Carlson",
    1990: "Debbye Turner",
    1991: "Marjorie Vincent",
    1992: "Carolyn Sapp",
    1993: "Leanza Cornett",
    1994: "Kimberly Aiken",
    1995: "Heather Whitestone",
    1996: "Shawntel Smith",
    1997: "Tara Dawn Holland",
    1998: "Kate Shindle",
    1999: "Nicole Johnson",
    2000: "Heather French",
    2001: "Angela Perez Baraquio",
    2002: "Katie Harman",
    2003: "Erika Harold",
    2004: "Ericka Dunlap",
    2005: "Deidre Downs",
    2006: "Jennifer Berry",
    2007: "Lauren Nelson",
    2008: "Kirsten Haglund",
    2009: "Katie Stam",
    2010: "Caressa Cameron",
    2011: "Teresa Scanlan",
    2012: "Laura Kaeppeler",
    2013: "Mallory Hagan",
    2014: "Nina Davuluri",
    2015: "Kira Kazantsev",
    2016: "Betty Cantrell",
    2017: "Savvy Shields",
    2018: "Cara Mund",
    2019: "Nia Franklin",
    2020: "Camille Schrier",
}

# Academy Award Best Actor winners by year (1935-2024)
OSCAR_BEST_ACTOR = {
    # 1935: "Clark Gable",
    # 1936: "Paul Muni",
    # 1937: "Spencer Tracy",
    # 1938: "Spencer Tracy",
    # 1939: "Robert Donat",
    # 1940: "James Stewart",
    1941: "Gary Cooper",
    1942: "James Cagney",
    1943: "Paul Lukas",
    1944: "Bing Crosby",
    1945: "Ray Milland",
    1946: "Fredric March",
    1947: "Ronald Colman",
    1948: "Laurence Olivier",
    1949: "Broderick Crawford",
    1950: "José Ferrer",
    1951: "Humphrey Bogart",
    1952: "Gary Cooper",
    1953: "William Holden",
    1954: "Marlon Brando",
    1955: "Ernest Borgnine",
    1956: "Yul Brynner",
    1957: "Alec Guinness",
    1958: "David Niven",
    1959: "Charlton Heston",
    1960: "Burt Lancaster",
    1961: "Maximilian Schell",
    1962: "Gregory Peck",
    1963: "Sidney Poitier",
    1964: "Rex Harrison",
    1965: "Lee Marvin",
    1966: "Paul Scofield",
    1967: "Rod Steiger",
    1968: "Cliff Robertson",
    1969: "John Wayne",
    1970: "George C. Scott",
    1971: "Gene Hackman",
    1972: "Marlon Brando",
    1973: "Jack Lemmon",
    1974: "Art Carney",
    1975: "Jack Nicholson",
    1976: "Peter Finch",
    1977: "Richard Dreyfuss",
    1978: "Jon Voight",
    1979: "Dustin Hoffman",
    1980: "Robert De Niro",
    1981: "Henry Fonda",
    1982: "Ben Kingsley",
    1983: "Robert Duvall",
    1984: "F. Murray Abraham",
    1985: "William Hurt",
    1986: "Paul Newman",
    1987: "Michael Douglas",
    1988: "Dustin Hoffman",
    1989: "Daniel Day-Lewis",
    1990: "Jeremy Irons",
    1991: "Anthony Hopkins",
    1992: "Al Pacino",
    1993: "Tom Hanks",
    1994: "Tom Hanks",
    1995: "Nicolas Cage",
    1996: "Geoffrey Rush",
    1997: "Jack Nicholson",
    1998: "Roberto Benigni",
    1999: "Kevin Spacey",
    2000: "Russell Crowe",
    2001: "Denzel Washington",
    2002: "Adrien Brody",
    2003: "Sean Penn",
    2004: "Jamie Foxx",
    2005: "Philip Seymour Hoffman",
    2006: "Forest Whitaker",
    2007: "Daniel Day-Lewis",
    2008: "Sean Penn",
    2009: "Jeff Bridges",
    2010: "Colin Firth",
    2011: "Jean Dujardin",
    2012: "Daniel Day-Lewis",
    2013: "Matthew McConaughey",
    2014: "Eddie Redmayne",
    2015: "Leonardo DiCaprio",
    2016: "Casey Affleck",
    2017: "Gary Oldman",
    2018: "Rami Malek",
    2019: "Joaquin Phoenix",
    2020: "Anthony Hopkins",
    2021: "Will Smith",
    # 2022: "Brendan Fraser",
    # 2023: "Cillian Murphy",
}

# Oscar Best Actor birth years
OSCAR_BEST_ACTOR_BIRTH_YEAR = {
    "Clark Gable": 1901,
    "Paul Muni": 1895,
    "Spencer Tracy": 1900,
    "Robert Donat": 1905,
    "James Stewart": 1908,
    "Gary Cooper": 1901,
    "James Cagney": 1899,
    "Paul Lukas": 1894,
    "Bing Crosby": 1903,
    "Ray Milland": 1907,
    "Fredric March": 1897,
    "Ronald Colman": 1891,
    "Laurence Olivier": 1907,
    "Broderick Crawford": 1911,
    "José Ferrer": 1912,
    "Humphrey Bogart": 1899,
    "William Holden": 1918,
    "Marlon Brando": 1924,
    "Ernest Borgnine": 1917,
    "Yul Brynner": 1920,
    "Alec Guinness": 1914,
    "David Niven": 1910,
    "Charlton Heston": 1923,
    "Burt Lancaster": 1913,
    "Maximilian Schell": 1930,
    "Gregory Peck": 1916,
    "Sidney Poitier": 1927,
    "Rex Harrison": 1908,
    "Lee Marvin": 1924,
    "Paul Scofield": 1922,
    "Rod Steiger": 1925,
    "Cliff Robertson": 1923,
    "John Wayne": 1907,
    "George C. Scott": 1927,
    "Gene Hackman": 1930,
    "Jack Lemmon": 1925,
    "Art Carney": 1918,
    "Jack Nicholson": 1937,
    "Peter Finch": 1916,
    "Richard Dreyfuss": 1947,
    "Jon Voight": 1938,
    "Dustin Hoffman": 1937,
    "Robert De Niro": 1943,
    "Henry Fonda": 1905,
    "Ben Kingsley": 1943,
    "Robert Duvall": 1931,
    "F. Murray Abraham": 1939,
    "William Hurt": 1950,
    "Paul Newman": 1925,
    "Michael Douglas": 1944,
    "Daniel Day-Lewis": 1957,
    "Jeremy Irons": 1948,
    "Anthony Hopkins": 1937,
    "Al Pacino": 1940,
    "Tom Hanks": 1956,
    "Nicolas Cage": 1964,
    "Geoffrey Rush": 1951,
    "Roberto Benigni": 1952,
    "Kevin Spacey": 1959,
    "Russell Crowe": 1964,
    "Denzel Washington": 1954,
    "Adrien Brody": 1973,
    "Sean Penn": 1960,
    "Jamie Foxx": 1967,
    "Philip Seymour Hoffman": 1967,
    "Forest Whitaker": 1961,
    "Jeff Bridges": 1949,
    "Colin Firth": 1960,
    "Jean Dujardin": 1972,
    "Matthew McConaughey": 1969,
    "Eddie Redmayne": 1982,
    "Leonardo DiCaprio": 1974,
    "Casey Affleck": 1975,
    "Gary Oldman": 1958,
    "Rami Malek": 1981,
    "Joaquin Phoenix": 1974,
    "Brendan Fraser": 1968,
    "Cillian Murphy": 1976,
    "Will Smith": 1968,
}

# Oscar Best Actor death years (only for those who have died)
OSCAR_BEST_ACTOR_DEATH_YEAR = {
    "Clark Gable": 1960,
    "Paul Muni": 1967,
    "Spencer Tracy": 1967,
    "Robert Donat": 1958,
    "James Stewart": 1997,
    "Gary Cooper": 1961,
    "James Cagney": 1986,
    "Paul Lukas": 1971,
    "Bing Crosby": 1977,
    "Ray Milland": 1986,
    "Fredric March": 1975,
    "Ronald Colman": 1958,
    "Laurence Olivier": 1989,
    "Broderick Crawford": 1986,
    "José Ferrer": 1992,
    "Humphrey Bogart": 1957,
    "William Holden": 1981,
    "Marlon Brando": 2004,
    "Ernest Borgnine": 2012,
    "Yul Brynner": 1985,
    "Alec Guinness": 2000,
    "David Niven": 1983,
    "Charlton Heston": 2008,
    "Burt Lancaster": 1994,
    "Maximilian Schell": 2014,
    "Gregory Peck": 2003,
    "Sidney Poitier": 2022,
    "Rex Harrison": 1990,
    "Lee Marvin": 1987,
    "Paul Scofield": 2008,
    "Rod Steiger": 2002,
    "Cliff Robertson": 2011,
    "John Wayne": 1979,
    "George C. Scott": 1999,
    "Jack Lemmon": 2001,
    "Art Carney": 2003,
    "Peter Finch": 1977,
    "Paul Newman": 2008,
    "Henry Fonda": 1982,
    "William Hurt": 2022,
    "Philip Seymour Hoffman": 2014,
}

# Oscar Best Actor birth day of month
OSCAR_BEST_ACTOR_BIRTH_DAY = {
    "Clark Gable": 1,
    "Paul Muni": 22,
    "Spencer Tracy": 5,
    "Robert Donat": 18,
    "James Stewart": 20,
    "Gary Cooper": 7,
    "James Cagney": 17,
    "Paul Lukas": 26,
    "Bing Crosby": 3,
    "Ray Milland": 3,
    "Fredric March": 31,
    "Ronald Colman": 9,
    "Laurence Olivier": 22,
    "Broderick Crawford": 9,
    "José Ferrer": 8,
    "Humphrey Bogart": 25,
    "William Holden": 17,
    "Marlon Brando": 3,
    "Ernest Borgnine": 24,
    "Yul Brynner": 11,
    "Alec Guinness": 2,
    "David Niven": 1,
    "Charlton Heston": 4,
    "Burt Lancaster": 2,
    "Maximilian Schell": 8,
    "Gregory Peck": 5,
    "Sidney Poitier": 20,
    "Rex Harrison": 5,
    "Lee Marvin": 19,
    "Paul Scofield": 21,
    "Rod Steiger": 14,
    "Cliff Robertson": 9,
    "John Wayne": 26,
    "George C. Scott": 18,
    "Gene Hackman": 30,
    "Jack Lemmon": 8,
    "Art Carney": 4,
    "Jack Nicholson": 22,
    "Peter Finch": 28,
    "Richard Dreyfuss": 29,
    "Jon Voight": 29,
    "Dustin Hoffman": 8,
    "Robert De Niro": 17,
    "Henry Fonda": 16,
    "Ben Kingsley": 31,
    "Robert Duvall": 5,
    "F. Murray Abraham": 24,
    "William Hurt": 20,
    "Paul Newman": 26,
    "Michael Douglas": 25,
    "Daniel Day-Lewis": 29,
    "Jeremy Irons": 19,
    "Anthony Hopkins": 31,
    "Al Pacino": 25,
    "Tom Hanks": 9,
    "Nicolas Cage": 7,
    "Geoffrey Rush": 6,
    "Roberto Benigni": 27,
    "Kevin Spacey": 26,
    "Russell Crowe": 7,
    "Denzel Washington": 28,
    "Adrien Brody": 14,
    "Sean Penn": 17,
    "Jamie Foxx": 13,
    "Philip Seymour Hoffman": 23,
    "Forest Whitaker": 15,
    "Jeff Bridges": 4,
    "Colin Firth": 10,
    "Jean Dujardin": 19,
    "Matthew McConaughey": 4,
    "Eddie Redmayne": 6,
    "Leonardo DiCaprio": 11,
    "Casey Affleck": 12,
    "Gary Oldman": 21,
    "Rami Malek": 12,
    "Joaquin Phoenix": 28,
    "Brendan Fraser": 3,
    "Cillian Murphy": 25,
    "Will Smith": 25,
}

# Oscar Best Actor by order (1st winner = 1941, 2nd = 1942, etc.)
OSCAR_BEST_ACTOR_BY_ORDER = {
    10: "Spencer Tracy",  # Captains Courageous (1938 ceremony for 1937 films)
    11: "Spencer Tracy",  # Boys Town
    12: "Robert Donat",  # Goodbye, Mr. Chips
    13: "James Stewart",  # The Philadelphia Story
    14: "Gary Cooper",  # Sergeant York
    15: "James Cagney",  # Yankee Doodle Dandy
    16: "Paul Lukas",  # Watch on the Rhine
    17: "Bing Crosby",  # Going My Way
    18: "Ray Milland",  # The Lost Weekend
    19: "Fredric March",  # The Best Years of Our Lives
    20: "Ronald Colman",  # A Double Life
    21: "Laurence Olivier",  # Hamlet
    22: "Broderick Crawford",  # All the King's Men
    23: "José Ferrer",  # Cyrano de Bergerac
    24: "Humphrey Bogart",  # The African Queen
    25: "Gary Cooper",  # High Noon
    26: "William Holden",  # Stalag 17
    27: "Marlon Brando",  # On the Waterfront
    28: "Ernest Borgnine",  # Marty
    29: "Yul Brynner",  # The King and I
    30: "Alec Guinness",  # The Bridge on the River Kwai
    31: "David Niven",  # Separate Tables
    32: "Charlton Heston",  # Ben-Hur
    33: "Burt Lancaster",  # Elmer Gantry
    34: "Maximilian Schell",  # Judgment at Nuremberg
    35: "Gregory Peck",  # To Kill a Mockingbird
    36: "Sidney Poitier",  # Lilies of the Field
    37: "Rex Harrison",  # My Fair Lady
    38: "Lee Marvin",  # Cat Ballou
    39: "Paul Scofield",  # A Man for All Seasons
    40: "Rod Steiger",  # In the Heat of the Night
    41: "Cliff Robertson",  # Charly
    42: "John Wayne",  # True Grit
    43: "George C. Scott",  # Patton (declined)
    44: "Gene Hackman",  # The French Connection
    45: "Marlon Brando",  # The Godfather (declined)
    46: "Jack Lemmon",  # Save the Tiger
    47: "Art Carney",  # Harry and Tonto
    48: "Jack Nicholson",  # One Flew Over the Cuckoo's Nest
    49: "Peter Finch",  # Network (posthumous)
    50: "Richard Dreyfuss",  # The Goodbye Girl
    51: "Jon Voight",  # Coming Home
    52: "Dustin Hoffman",  # Kramer vs. Kramer
    53: "Robert De Niro",  # Raging Bull
    54: "Henry Fonda",  # On Golden Pond
    55: "Ben Kingsley",  # Gandhi
    56: "Robert Duvall",  # Tender Mercies
    57: "F. Murray Abraham",  # Amadeus
    58: "William Hurt",  # Kiss of the Spider Woman
    59: "Paul Newman",  # The Color of Money
    60: "Michael Douglas",  # Wall Street
    61: "Dustin Hoffman",  # Rain Man
    62: "Daniel Day-Lewis",  # My Left Foot
    63: "Jeremy Irons",  # Reversal of Fortune
    64: "Anthony Hopkins",  # The Silence of the Lambs
    65: "Al Pacino",  # Scent of a Woman
    66: "Tom Hanks",  # Philadelphia
    67: "Tom Hanks",  # Forrest Gump
    68: "Nicolas Cage",  # Leaving Las Vegas
    69: "Geoffrey Rush",  # Shine
    70: "Jack Nicholson",  # As Good as It Gets
    71: "Roberto Benigni",  # Life Is Beautiful
    72: "Kevin Spacey",  # American Beauty
    73: "Russell Crowe",  # Gladiator
    74: "Denzel Washington",  # Training Day
    75: "Adrien Brody",  # The Pianist
    76: "Sean Penn",  # Mystic River
    77: "Jamie Foxx",  # Ray
    78: "Philip Seymour Hoffman",  # Capote
    79: "Forest Whitaker",  # The Last King of Scotland
    80: "Daniel Day-Lewis",  # There Will Be Blood
    81: "Sean Penn",  # Milk
    82: "Jeff Bridges",  # Crazy Heart
    83: "Colin Firth",  # The King's Speech
    84: "Jean Dujardin",  # The Artist
    85: "Daniel Day-Lewis",  # Lincoln
    86: "Matthew McConaughey",  # Dallas Buyers Club
    87: "Eddie Redmayne",  # The Theory of Everything
    88: "Leonardo DiCaprio",  # The Revenant
    89: "Casey Affleck",  # Manchester by the Sea
    90: "Gary Oldman",  # Darkest Hour
    91: "Rami Malek",  # Bohemian Rhapsody
    92: "Joaquin Phoenix",  # Joker
    93: "Anthony Hopkins",  # The Father
    94: "Will Smith",  # King Richard
    95: "Brendan Fraser",  # The Whale
    # 96: "Cillian Murphy",  # Oppenheimer
    # 97: "Adrien Brody",  # The Brutalist
}

# Oscar Best Actress winners by year
OSCAR_BEST_ACTRESS = {
    1940: "Ginger Rogers",  # Kitty Foyle
    1941: "Joan Fontaine",  # Suspicion
    1942: "Greer Garson",  # Mrs. Miniver
    1943: "Jennifer Jones",  # The Song of Bernadette
    1944: "Ingrid Bergman",  # Gaslight
    1945: "Joan Crawford",  # Mildred Pierce
    1946: "Olivia de Havilland",  # To Each His Own
    1947: "Loretta Young",  # The Farmer's Daughter
    1948: "Jane Wyman",  # Johnny Belinda
    1949: "Olivia de Havilland",  # The Heiress
    1950: "Judy Holliday",  # Born Yesterday
    1951: "Vivien Leigh",  # A Streetcar Named Desire
    1952: "Shirley Booth",  # Come Back, Little Sheba
    1953: "Audrey Hepburn",  # Roman Holiday
    1954: "Grace Kelly",  # The Country Girl
    1955: "Anna Magnani",  # The Rose Tattoo
    1956: "Ingrid Bergman",  # Anastasia
    1957: "Joanne Woodward",  # The Three Faces of Eve
    1958: "Susan Hayward",  # I Want to Live!
    1959: "Simone Signoret",  # Room at the Top
    1960: "Elizabeth Taylor",  # BUtterfield 8
    1961: "Sophia Loren",  # Two Women
    1962: "Anne Bancroft",  # The Miracle Worker
    1963: "Patricia Neal",  # Hud
    1964: "Julie Andrews",  # Mary Poppins
    1965: "Julie Christie",  # Darling
    1966: "Elizabeth Taylor",  # Who's Afraid of Virginia Woolf?
    1967: "Katharine Hepburn",  # Guess Who's Coming to Dinner
    1969: "Maggie Smith",  # The Prime of Miss Jean Brodie
    1970: "Glenda Jackson",  # Women in Love
    1971: "Jane Fonda",  # Klute
    1972: "Liza Minnelli",  # Cabaret
    1973: "Glenda Jackson",  # A Touch of Class
    1974: "Ellen Burstyn",  # Alice Doesn't Live Here Anymore
    1975: "Louise Fletcher",  # One Flew Over the Cuckoo's Nest
    1976: "Faye Dunaway",  # Network
    1977: "Diane Keaton",  # Annie Hall
    1978: "Jane Fonda",  # Coming Home
    1979: "Sally Field",  # Norma Rae
    1980: "Sissy Spacek",  # Coal Miner's Daughter
    1981: "Katharine Hepburn",  # On Golden Pond
    1982: "Meryl Streep",  # Sophie's Choice
    1983: "Shirley MacLaine",  # Terms of Endearment
    1984: "Sally Field",  # Places in the Heart
    1985: "Geraldine Page",  # The Trip to Bountiful
    1986: "Marlee Matlin",  # Children of a Lesser God
    1987: "Cher",  # Moonstruck
    1988: "Jodie Foster",  # The Accused
    1989: "Jessica Tandy",  # Driving Miss Daisy
    1990: "Kathy Bates",  # Misery
    1991: "Jodie Foster",  # The Silence of the Lambs
    1992: "Emma Thompson",  # Howards End
    1993: "Holly Hunter",  # The Piano
    1994: "Jessica Lange",  # Blue Sky
    1995: "Susan Sarandon",  # Dead Man Walking
    1996: "Frances McDormand",  # Fargo
    1997: "Helen Hunt",  # As Good as It Gets
    1998: "Gwyneth Paltrow",  # Shakespeare in Love
    1999: "Hilary Swank",  # Boys Don't Cry
    2000: "Julia Roberts",  # Erin Brockovich
    2001: "Halle Berry",  # Monster's Ball
    2002: "Nicole Kidman",  # The Hours
    2003: "Charlize Theron",  # Monster
    2004: "Hilary Swank",  # Million Dollar Baby
    2005: "Reese Witherspoon",  # Walk the Line
    2006: "Helen Mirren",  # The Queen
    2007: "Marion Cotillard",  # La Vie en Rose
    2008: "Kate Winslet",  # The Reader
    2009: "Sandra Bullock",  # The Blind Side
    2010: "Natalie Portman",  # Black Swan
    2011: "Meryl Streep",  # The Iron Lady
    2012: "Jennifer Lawrence",  # Silver Linings Playbook
    2013: "Cate Blanchett",  # Blue Jasmine
    2014: "Julianne Moore",  # Still Alice
    2015: "Brie Larson",  # Room
    2016: "Emma Stone",  # La La Land
    2017: "Frances McDormand",  # Three Billboards Outside Ebbing, Missouri
    2018: "Olivia Colman",  # The Favourite
    2019: "Renée Zellweger",  # Judy
    2020: "Frances McDormand",  # Nomadland
    2021: "Jessica Chastain",  # The Eyes of Tammy Faye
    # 2022: "Michelle Yeoh",  # Everything Everywhere All at Once
    # 2023: "Emma Stone",  # Poor Things
    # 2024: "Mikey Madison",  # Anora
}

# Oscar Best Actress birth years
OSCAR_BEST_ACTRESS_BIRTH_YEAR = {
    "Ginger Rogers": 1911,
    "Joan Fontaine": 1917,
    "Greer Garson": 1904,
    "Jennifer Jones": 1919,
    "Ingrid Bergman": 1915,
    "Joan Crawford": 1904,
    "Olivia de Havilland": 1916,
    "Loretta Young": 1913,
    "Jane Wyman": 1917,
    "Judy Holliday": 1921,
    "Vivien Leigh": 1913,
    "Shirley Booth": 1898,
    "Audrey Hepburn": 1929,
    "Grace Kelly": 1929,
    "Anna Magnani": 1908,
    "Joanne Woodward": 1930,
    "Susan Hayward": 1917,
    "Simone Signoret": 1921,
    "Elizabeth Taylor": 1932,
    "Sophia Loren": 1934,
    "Anne Bancroft": 1931,
    "Patricia Neal": 1926,
    "Julie Andrews": 1935,
    "Julie Christie": 1940,
    "Katharine Hepburn": 1907,
    "Barbra Streisand": 1942,
    "Maggie Smith": 1934,
    "Glenda Jackson": 1936,
    "Jane Fonda": 1937,
    "Liza Minnelli": 1946,
    "Ellen Burstyn": 1932,
    "Louise Fletcher": 1934,
    "Faye Dunaway": 1941,
    "Diane Keaton": 1946,
    "Sissy Spacek": 1949,
    "Meryl Streep": 1949,
    "Shirley MacLaine": 1934,
    "Sally Field": 1946,
    "Geraldine Page": 1924,
    "Marlee Matlin": 1965,
    "Cher": 1946,
    "Jodie Foster": 1962,
    "Jessica Tandy": 1909,
    "Kathy Bates": 1948,
    "Emma Thompson": 1959,
    "Holly Hunter": 1958,
    "Jessica Lange": 1949,
    "Susan Sarandon": 1946,
    "Frances McDormand": 1957,
    "Helen Hunt": 1963,
    "Gwyneth Paltrow": 1972,
    "Hilary Swank": 1974,
    "Julia Roberts": 1967,
    "Halle Berry": 1966,
    "Nicole Kidman": 1967,
    "Charlize Theron": 1975,
    "Reese Witherspoon": 1976,
    "Helen Mirren": 1945,
    "Marion Cotillard": 1975,
    "Kate Winslet": 1975,
    "Sandra Bullock": 1964,
    "Natalie Portman": 1981,
    "Jennifer Lawrence": 1990,
    "Cate Blanchett": 1969,
    "Julianne Moore": 1960,
    "Brie Larson": 1989,
    "Emma Stone": 1988,
    "Olivia Colman": 1974,
    "Renée Zellweger": 1969,
    "Jessica Chastain": 1977,
    "Michelle Yeoh": 1962,
}

# Oscar Best Actress birth day of month
OSCAR_BEST_ACTRESS_BIRTH_DAY = {
    "Ginger Rogers": 16,
    "Joan Fontaine": 22,
    "Greer Garson": 29,
    "Jennifer Jones": 2,
    "Ingrid Bergman": 29,
    "Joan Crawford": 23,
    "Olivia de Havilland": 1,
    "Loretta Young": 6,
    "Jane Wyman": 5,
    "Judy Holliday": 21,
    "Vivien Leigh": 5,
    "Shirley Booth": 30,
    "Audrey Hepburn": 4,
    "Grace Kelly": 12,
    "Anna Magnani": 7,
    "Joanne Woodward": 27,
    "Susan Hayward": 30,
    "Simone Signoret": 25,
    "Elizabeth Taylor": 27,
    "Sophia Loren": 20,
    "Anne Bancroft": 17,
    "Patricia Neal": 20,
    "Julie Andrews": 1,
    "Julie Christie": 14,
    "Katharine Hepburn": 12,
    "Barbra Streisand": 24,
    "Maggie Smith": 28,
    "Glenda Jackson": 9,
    "Jane Fonda": 21,
    "Liza Minnelli": 12,
    "Ellen Burstyn": 7,
    "Louise Fletcher": 22,
    "Faye Dunaway": 14,
    "Diane Keaton": 5,
    "Sissy Spacek": 25,
    "Meryl Streep": 22,
    "Shirley MacLaine": 24,
    "Sally Field": 6,
    "Geraldine Page": 22,
    "Marlee Matlin": 24,
    "Cher": 20,
    "Jodie Foster": 19,
    "Jessica Tandy": 7,
    "Kathy Bates": 28,
    "Emma Thompson": 15,
    "Holly Hunter": 20,
    "Jessica Lange": 20,
    "Susan Sarandon": 4,
    "Frances McDormand": 23,
    "Helen Hunt": 15,
    "Gwyneth Paltrow": 27,
    "Hilary Swank": 30,
    "Julia Roberts": 28,
    "Halle Berry": 14,
    "Nicole Kidman": 20,
    "Charlize Theron": 7,
    "Reese Witherspoon": 22,
    "Helen Mirren": 26,
    "Marion Cotillard": 30,
    "Kate Winslet": 5,
    "Sandra Bullock": 26,
    "Natalie Portman": 9,
    "Jennifer Lawrence": 15,
    "Cate Blanchett": 14,
    "Julianne Moore": 3,
    "Brie Larson": 1,
    "Emma Stone": 6,
    "Olivia Colman": 30,
    "Renée Zellweger": 25,
    "Jessica Chastain": 24,
    "Michelle Yeoh": 6,
}

# Oscar Best Actress by order (starting from ceremony 10)
OSCAR_BEST_ACTRESS_BY_ORDER = {
    10: "Luise Rainer",  # The Good Earth
    11: "Bette Davis",  # Jezebel
    12: "Vivien Leigh",  # Gone with the Wind
    13: "Ginger Rogers",  # Kitty Foyle
    14: "Joan Fontaine",  # Suspicion
    15: "Greer Garson",  # Mrs. Miniver
    16: "Jennifer Jones",  # The Song of Bernadette
    17: "Ingrid Bergman",  # Gaslight
    18: "Joan Crawford",  # Mildred Pierce
    19: "Olivia de Havilland",  # To Each His Own
    20: "Loretta Young",  # The Farmer's Daughter
    21: "Jane Wyman",  # Johnny Belinda
    22: "Olivia de Havilland",  # The Heiress
    23: "Judy Holliday",  # Born Yesterday
    24: "Vivien Leigh",  # A Streetcar Named Desire
    25: "Shirley Booth",  # Come Back, Little Sheba
    26: "Audrey Hepburn",  # Roman Holiday
    27: "Grace Kelly",  # The Country Girl
    28: "Anna Magnani",  # The Rose Tattoo
    29: "Ingrid Bergman",  # Anastasia
    30: "Joanne Woodward",  # The Three Faces of Eve
    31: "Susan Hayward",  # I Want to Live!
    32: "Simone Signoret",  # Room at the Top
    33: "Elizabeth Taylor",  # BUtterfield 8
    34: "Sophia Loren",  # Two Women
    35: "Anne Bancroft",  # The Miracle Worker
    36: "Patricia Neal",  # Hud
    37: "Julie Andrews",  # Mary Poppins
    38: "Julie Christie",  # Darling
    39: "Elizabeth Taylor",  # Who's Afraid of Virginia Woolf?
    40: "Katharine Hepburn",  # Guess Who's Coming to Dinner
    42: "Maggie Smith",  # The Prime of Miss Jean Brodie
    43: "Glenda Jackson",  # Women in Love
    44: "Jane Fonda",  # Klute
    45: "Liza Minnelli",  # Cabaret
    46: "Glenda Jackson",  # A Touch of Class
    47: "Ellen Burstyn",  # Alice Doesn't Live Here Anymore
    48: "Louise Fletcher",  # One Flew Over the Cuckoo's Nest
    49: "Faye Dunaway",  # Network
    50: "Diane Keaton",  # Annie Hall
    51: "Jane Fonda",  # Coming Home
    52: "Sally Field",  # Norma Rae
    53: "Sissy Spacek",  # Coal Miner's Daughter
    54: "Katharine Hepburn",  # On Golden Pond
    55: "Meryl Streep",  # Sophie's Choice
    56: "Shirley MacLaine",  # Terms of Endearment
    57: "Sally Field",  # Places in the Heart
    58: "Geraldine Page",  # The Trip to Bountiful
    59: "Marlee Matlin",  # Children of a Lesser God
    60: "Cher",  # Moonstruck
    61: "Jodie Foster",  # The Accused
    62: "Jessica Tandy",  # Driving Miss Daisy
    63: "Kathy Bates",  # Misery
    64: "Jodie Foster",  # The Silence of the Lambs
    65: "Emma Thompson",  # Howards End
    66: "Holly Hunter",  # The Piano
    67: "Jessica Lange",  # Blue Sky
    68: "Susan Sarandon",  # Dead Man Walking
    69: "Frances McDormand",  # Fargo
    70: "Helen Hunt",  # As Good as It Gets
    71: "Gwyneth Paltrow",  # Shakespeare in Love
    72: "Hilary Swank",  # Boys Don't Cry
    73: "Julia Roberts",  # Erin Brockovich
    74: "Halle Berry",  # Monster's Ball
    75: "Nicole Kidman",  # The Hours
    76: "Charlize Theron",  # Monster
    77: "Hilary Swank",  # Million Dollar Baby
    78: "Reese Witherspoon",  # Walk the Line
    79: "Helen Mirren",  # The Queen
    80: "Marion Cotillard",  # La Vie en Rose
    81: "Kate Winslet",  # The Reader
    82: "Sandra Bullock",  # The Blind Side
    83: "Natalie Portman",  # Black Swan
    84: "Meryl Streep",  # The Iron Lady
    85: "Jennifer Lawrence",  # Silver Linings Playbook
    86: "Cate Blanchett",  # Blue Jasmine
    87: "Julianne Moore",  # Still Alice
    88: "Brie Larson",  # Room
    89: "Emma Stone",  # La La Land
    90: "Frances McDormand",  # Three Billboards Outside Ebbing, Missouri
    91: "Olivia Colman",  # The Favourite
    92: "Renée Zellweger",  # Judy
    93: "Frances McDormand",  # Nomadland
    94: "Jessica Chastain",  # The Eyes of Tammy Faye
    95: "Michelle Yeoh",  # Everything Everywhere All at Once
    # 96: "Emma Stone",  # Poor Things
    # 97: "Mikey Madison",  # Anora
}

# Oscar Best Supporting Actor winners by year
OSCAR_BEST_SUPPORTING_ACTOR = {
    1940: "Walter Brennan",  # The Westerner
    1941: "Donald Crisp",  # How Green Was My Valley
    1942: "Van Heflin",  # Johnny Eager
    1943: "Charles Coburn",  # The More the Merrier
    1944: "Barry Fitzgerald",  # Going My Way
    1945: "James Dunn",  # A Tree Grows in Brooklyn
    1946: "Harold Russell",  # The Best Years of Our Lives
    1947: "Edmund Gwenn",  # Miracle on 34th Street
    1948: "Walter Huston",  # The Treasure of the Sierra Madre
    1949: "Dean Jagger",  # Twelve O'Clock High
    1950: "George Sanders",  # All About Eve
    1951: "Karl Malden",  # A Streetcar Named Desire
    1952: "Anthony Quinn",  # Viva Zapata!
    1953: "Frank Sinatra",  # From Here to Eternity
    1954: "Edmond O'Brien",  # The Barefoot Contessa
    1955: "Jack Lemmon",  # Mister Roberts
    1956: "Anthony Quinn",  # Lust for Life
    1957: "Red Buttons",  # Sayonara
    1958: "Burl Ives",  # The Big Country
    1959: "Hugh Griffith",  # Ben-Hur
    1960: "Peter Ustinov",  # Spartacus
    1961: "George Chakiris",  # West Side Story
    1962: "Ed Begley",  # Sweet Bird of Youth
    1963: "Melvyn Douglas",  # Hud
    1964: "Peter Ustinov",  # Topkapi
    1965: "Martin Balsam",  # A Thousand Clowns
    1966: "Walter Matthau",  # The Fortune Cookie
    1967: "George Kennedy",  # Cool Hand Luke
    1968: "Jack Albertson",  # The Subject Was Roses
    1969: "Gig Young",  # They Shoot Horses, Don't They?
    1970: "John Mills",  # Ryan's Daughter
    1971: "Ben Johnson",  # The Last Picture Show
    1972: "Joel Grey",  # Cabaret
    1973: "John Houseman",  # The Paper Chase
    1974: "Robert De Niro",  # The Godfather Part II
    1975: "George Burns",  # The Sunshine Boys
    1976: "Jason Robards",  # All the President's Men
    1977: "Jason Robards",  # Julia
    1978: "Christopher Walken",  # The Deer Hunter
    1979: "Melvyn Douglas",  # Being There
    1980: "Timothy Hutton",  # Ordinary People
    1981: "John Gielgud",  # Arthur
    1982: "Louis Gossett Jr.",  # An Officer and a Gentleman
    1983: "Jack Nicholson",  # Terms of Endearment
    1984: "Haing S. Ngor",  # The Killing Fields
    1985: "Don Ameche",  # Cocoon
    1986: "Michael Caine",  # Hannah and Her Sisters
    1987: "Sean Connery",  # The Untouchables
    1988: "Kevin Kline",  # A Fish Called Wanda
    1989: "Denzel Washington",  # Glory
    1990: "Joe Pesci",  # Goodfellas
    1991: "Jack Palance",  # City Slickers
    1992: "Gene Hackman",  # Unforgiven
    1993: "Tommy Lee Jones",  # The Fugitive
    1994: "Martin Landau",  # Ed Wood
    1995: "Kevin Spacey",  # The Usual Suspects
    1996: "Cuba Gooding Jr.",  # Jerry Maguire
    1997: "Robin Williams",  # Good Will Hunting
    1998: "James Coburn",  # Affliction
    1999: "Michael Caine",  # The Cider House Rules
    2000: "Benicio del Toro",  # Traffic
    2001: "Jim Broadbent",  # Iris
    2002: "Chris Cooper",  # Adaptation
    2003: "Tim Robbins",  # Mystic River
    2004: "Morgan Freeman",  # Million Dollar Baby
    2005: "George Clooney",  # Syriana
    2006: "Alan Arkin",  # Little Miss Sunshine
    2007: "Javier Bardem",  # No Country for Old Men
    2008: "Heath Ledger",  # The Dark Knight (posthumous)
    2009: "Christoph Waltz",  # Inglourious Basterds
    2010: "Christian Bale",  # The Fighter
    2011: "Christopher Plummer",  # Beginners
    2012: "Christoph Waltz",  # Django Unchained
    2013: "Jared Leto",  # Dallas Buyers Club
    2014: "J.K. Simmons",  # Whiplash
    2015: "Mark Rylance",  # Bridge of Spies
    2016: "Mahershala Ali",  # Moonlight
    2017: "Sam Rockwell",  # Three Billboards Outside Ebbing, Missouri
    2018: "Mahershala Ali",  # Green Book
    2019: "Brad Pitt",  # Once Upon a Time in Hollywood
    2020: "Daniel Kaluuya",  # Judas and the Black Messiah
    2021: "Troy Kotsur",  # CODA
    # 2022: "Ke Huy Quan",  # Everything Everywhere All at Once
    # 2023: "Robert Downey Jr.",  # Oppenheimer
    # 2024: "Kieran Culkin",  # A Real Pain
}

# Oscar Best Supporting Actor birth years
OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR = {
    "Walter Brennan": 1894,
    "Donald Crisp": 1882,
    "Van Heflin": 1910,
    "Charles Coburn": 1877,
    "Barry Fitzgerald": 1888,
    "James Dunn": 1901,
    "Harold Russell": 1914,
    "Edmund Gwenn": 1877,
    "Walter Huston": 1883,
    "Dean Jagger": 1903,
    "George Sanders": 1906,
    "Karl Malden": 1912,
    "Anthony Quinn": 1915,
    "Frank Sinatra": 1915,
    "Edmond O'Brien": 1915,
    "Jack Lemmon": 1925,
    "Red Buttons": 1919,
    "Burl Ives": 1909,
    "Hugh Griffith": 1912,
    "Peter Ustinov": 1921,
    "Ed Begley": 1901,
    "Melvyn Douglas": 1901,
    "Martin Balsam": 1919,
    "Walter Matthau": 1920,
    "George Kennedy": 1925,
    "Jack Albertson": 1907,
    "Gig Young": 1913,
    "John Mills": 1908,
    "Joel Grey": 1932,
    "John Houseman": 1902,
    "Robert De Niro": 1943,
    "Jason Robards": 1922,
    "Christopher Walken": 1943,
    "Timothy Hutton": 1960,
    "John Gielgud": 1904,
    "Louis Gossett Jr.": 1936,
    "Jack Nicholson": 1937,
    "Haing S. Ngor": 1940,
    "Don Ameche": 1908,
    "Michael Caine": 1933,
    "Sean Connery": 1930,
    "Kevin Kline": 1947,
    "Denzel Washington": 1954,
    "Joe Pesci": 1943,
    "Jack Palance": 1919,
    "Gene Hackman": 1930,
    "Tommy Lee Jones": 1946,
    "Martin Landau": 1928,
    "Kevin Spacey": 1959,
    "Cuba Gooding Jr.": 1968,
    "Robin Williams": 1951,
    "James Coburn": 1928,
    "Benicio del Toro": 1967,
    "Jim Broadbent": 1949,
    "Chris Cooper": 1951,
    "Tim Robbins": 1958,
    "Morgan Freeman": 1937,
    "George Clooney": 1961,
    "Alan Arkin": 1934,
    "Javier Bardem": 1969,
    "Heath Ledger": 1979,
    "Christoph Waltz": 1956,
    "Christian Bale": 1974,
    "Christopher Plummer": 1929,
    "Jared Leto": 1971,
    "J.K. Simmons": 1955,
    "Mark Rylance": 1960,
    "Mahershala Ali": 1974,
    "Sam Rockwell": 1968,
    "Brad Pitt": 1963,
    "Daniel Kaluuya": 1989,
    "Troy Kotsur": 1968,
    "Ke Huy Quan": 1971,
    "Robert Downey Jr.": 1965,
}

# Oscar Best Supporting Actor birth day of month
OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY = {
    "Walter Brennan": 25,
    "Donald Crisp": 27,
    "Van Heflin": 13,
    "Charles Coburn": 19,
    "Barry Fitzgerald": 10,
    "James Dunn": 2,
    "Harold Russell": 14,
    "Edmund Gwenn": 26,
    "Dean Jagger": 7,
    "George Sanders": 3,
    "Karl Malden": 22,
    "Anthony Quinn": 21,
    "Frank Sinatra": 12,
    "Edmond O'Brien": 10,
    "Jack Lemmon": 8,
    "Red Buttons": 5,
    "Burl Ives": 14,
    "Hugh Griffith": 30,
    "Peter Ustinov": 16,
    "George Chakiris": 16,
    "Ed Begley": 25,
    "Melvyn Douglas": 5,
    "Martin Balsam": 4,
    "Walter Matthau": 1,
    "George Kennedy": 18,
    "Jack Albertson": 16,
    "Gig Young": 4,
    "John Mills": 22,
    "Joel Grey": 11,
    "John Houseman": 22,
    "Robert De Niro": 17,
    "Jason Robards": 26,
    "Christopher Walken": 31,
    "Timothy Hutton": 16,
    "John Gielgud": 14,
    "Louis Gossett Jr.": 27,
    "Jack Nicholson": 22,
    "Haing S. Ngor": 22,
    "Don Ameche": 31,
    "Michael Caine": 14,
    "Sean Connery": 25,
    "Kevin Kline": 24,
    "Denzel Washington": 28,
    "Joe Pesci": 9,
    "Jack Palance": 18,
    "Gene Hackman": 30,
    "Tommy Lee Jones": 15,
    "Martin Landau": 20,
    "Kevin Spacey": 26,
    "Cuba Gooding Jr.": 2,
    "Robin Williams": 21,
    "James Coburn": 31,
    "Benicio del Toro": 19,
    "Jim Broadbent": 24,
    "Chris Cooper": 9,
    "Tim Robbins": 16,
    "Morgan Freeman": 1,
    "George Clooney": 6,
    "Alan Arkin": 26,
    "Javier Bardem": 1,
    "Heath Ledger": 4,
    "Christoph Waltz": 4,
    "Christian Bale": 30,
    "Christopher Plummer": 13,
    "Jared Leto": 26,
    "J.K. Simmons": 9,
    "Mark Rylance": 18,
    "Mahershala Ali": 16,
    "Sam Rockwell": 5,
    "Brad Pitt": 18,
    "Daniel Kaluuya": 24,
    "Troy Kotsur": 24,
    "Ke Huy Quan": 20,
    "Robert Downey Jr.": 4,
}

# Oscar Best Supporting Actor by order (starting from ceremony 10)
OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER = {
    9: "Walter Brennan",  # Come and Get It
    10: "Joseph Schildkraut",  # The Life of Emile Zola
    11: "Walter Brennan",  # Kentucky
    12: "Thomas Mitchell",  # Stagecoach
    13: "Walter Brennan",  # The Westerner
    14: "Donald Crisp",  # How Green Was My Valley
    15: "Van Heflin",  # Johnny Eager
    16: "Charles Coburn",  # The More the Merrier
    17: "Barry Fitzgerald",  # Going My Way
    18: "James Dunn",  # A Tree Grows in Brooklyn
    19: "Harold Russell",  # The Best Years of Our Lives
    20: "Edmund Gwenn",  # Miracle on 34th Street
    21: "Walter Huston",  # The Treasure of the Sierra Madre
    22: "Dean Jagger",  # Twelve O'Clock High
    23: "George Sanders",  # All About Eve
    24: "Karl Malden",  # A Streetcar Named Desire
    25: "Anthony Quinn",  # Viva Zapata!
    26: "Frank Sinatra",  # From Here to Eternity
    27: "Edmond O'Brien",  # The Barefoot Contessa
    28: "Jack Lemmon",  # Mister Roberts
    29: "Anthony Quinn",  # Lust for Life
    30: "Red Buttons",  # Sayonara
    31: "Burl Ives",  # The Big Country
    32: "Hugh Griffith",  # Ben-Hur
    33: "Peter Ustinov",  # Spartacus
    34: "George Chakiris",  # West Side Story
    35: "Ed Begley",  # Sweet Bird of Youth
    36: "Melvyn Douglas",  # Hud
    37: "Peter Ustinov",  # Topkapi
    38: "Martin Balsam",  # A Thousand Clowns
    39: "Walter Matthau",  # The Fortune Cookie
    40: "George Kennedy",  # Cool Hand Luke
    41: "Jack Albertson",  # The Subject Was Roses
    42: "Gig Young",  # They Shoot Horses, Don't They?
    43: "John Mills",  # Ryan's Daughter
    44: "Ben Johnson",  # The Last Picture Show
    45: "Joel Grey",  # Cabaret
    46: "John Houseman",  # The Paper Chase
    47: "Robert De Niro",  # The Godfather Part II
    48: "George Burns",  # The Sunshine Boys
    49: "Jason Robards",  # All the President's Men
    50: "Jason Robards",  # Julia
    51: "Christopher Walken",  # The Deer Hunter
    52: "Melvyn Douglas",  # Being There
    53: "Timothy Hutton",  # Ordinary People
    54: "John Gielgud",  # Arthur
    55: "Louis Gossett Jr.",  # An Officer and a Gentleman
    56: "Jack Nicholson",  # Terms of Endearment
    57: "Haing S. Ngor",  # The Killing Fields
    58: "Don Ameche",  # Cocoon
    59: "Michael Caine",  # Hannah and Her Sisters
    60: "Sean Connery",  # The Untouchables
    61: "Kevin Kline",  # A Fish Called Wanda
    62: "Denzel Washington",  # Glory
    63: "Joe Pesci",  # Goodfellas
    64: "Jack Palance",  # City Slickers
    65: "Gene Hackman",  # Unforgiven
    66: "Tommy Lee Jones",  # The Fugitive
    67: "Martin Landau",  # Ed Wood
    68: "Kevin Spacey",  # The Usual Suspects
    69: "Cuba Gooding Jr.",  # Jerry Maguire
    70: "Robin Williams",  # Good Will Hunting
    71: "James Coburn",  # Affliction
    72: "Michael Caine",  # The Cider House Rules
    73: "Benicio del Toro",  # Traffic
    74: "Jim Broadbent",  # Iris
    75: "Chris Cooper",  # Adaptation
    76: "Tim Robbins",  # Mystic River
    77: "Morgan Freeman",  # Million Dollar Baby
    78: "George Clooney",  # Syriana
    79: "Alan Arkin",  # Little Miss Sunshine
    80: "Javier Bardem",  # No Country for Old Men
    81: "Heath Ledger",  # The Dark Knight (posthumous)
    82: "Christoph Waltz",  # Inglourious Basterds
    83: "Christian Bale",  # The Fighter
    84: "Christopher Plummer",  # Beginners
    85: "Christoph Waltz",  # Django Unchained
    86: "Jared Leto",  # Dallas Buyers Club
    87: "J.K. Simmons",  # Whiplash
    88: "Mark Rylance",  # Bridge of Spies
    89: "Mahershala Ali",  # Moonlight
    90: "Sam Rockwell",  # Three Billboards Outside Ebbing, Missouri
    91: "Mahershala Ali",  # Green Book
    92: "Brad Pitt",  # Once Upon a Time in Hollywood
    93: "Daniel Kaluuya",  # Judas and the Black Messiah
    94: "Troy Kotsur",  # CODA
    95: "Ke Huy Quan",  # Everything Everywhere All at Once
    # 96: "Robert Downey Jr.",  # Oppenheimer
    # 97: "Kieran Culkin",  # A Real Pain
}

# Oscar Best Supporting Actress winners by year
OSCAR_BEST_SUPPORTING_ACTRESS = {
    1944: "Ethel Barrymore",  # None but the Lonely Heart
    1945: "Anne Revere",  # National Velvet
    1946: "Anne Baxter",  # The Razor's Edge
    1947: "Celeste Holm",  # Gentleman's Agreement
    1948: "Claire Trevor",  # Key Largo
    1949: "Mercedes McCambridge",  # All the King's Men
    1950: "Josephine Hull",  # Harvey
    1951: "Kim Hunter",  # A Streetcar Named Desire
    1952: "Gloria Grahame",  # The Bad and the Beautiful
    1953: "Donna Reed",  # From Here to Eternity
    1954: "Eva Marie Saint",  # On the Waterfront
    1955: "Jo Van Fleet",  # East of Eden
    1956: "Dorothy Malone",  # Written on the Wind
    1957: "Miyoshi Umeki",  # Sayonara
    1958: "Wendy Hiller",  # Separate Tables
    1959: "Shelley Winters",  # The Diary of Anne Frank
    1960: "Shirley Jones",  # Elmer Gantry
    1961: "Rita Moreno",  # West Side Story
    1962: "Patty Duke",  # The Miracle Worker
    1963: "Margaret Rutherford",  # The V.I.P.s
    1964: "Lila Kedrova",  # Zorba the Greek
    1965: "Shelley Winters",  # A Patch of Blue
    1966: "Sandy Dennis",  # Who's Afraid of Virginia Woolf?
    1967: "Estelle Parsons",  # Bonnie and Clyde
    1968: "Ruth Gordon",  # Rosemary's Baby
    1969: "Goldie Hawn",  # Cactus Flower
    1970: "Helen Hayes",  # Airport
    1971: "Cloris Leachman",  # The Last Picture Show
    1972: "Eileen Heckart",  # Butterflies Are Free
    1973: "Tatum O'Neal",  # Paper Moon
    1974: "Ingrid Bergman",  # Murder on the Orient Express
    1975: "Lee Grant",  # Shampoo
    1976: "Beatrice Straight",  # Network
    1977: "Vanessa Redgrave",  # Julia
    1978: "Maggie Smith",  # California Suite
    1979: "Meryl Streep",  # Kramer vs. Kramer
    1980: "Mary Steenburgen",  # Melvin and Howard
    1981: "Maureen Stapleton",  # Reds
    1982: "Jessica Lange",  # Tootsie
    1983: "Linda Hunt",  # The Year of Living Dangerously
    1984: "Peggy Ashcroft",  # A Passage to India
    1985: "Anjelica Huston",  # Prizzi's Honor
    1986: "Dianne Wiest",  # Hannah and Her Sisters
    1987: "Olympia Dukakis",  # Moonstruck
    1988: "Geena Davis",  # The Accidental Tourist
    1989: "Brenda Fricker",  # My Left Foot
    1990: "Whoopi Goldberg",  # Ghost
    1991: "Mercedes Ruehl",  # The Fisher King
    1992: "Marisa Tomei",  # My Cousin Vinny
    1993: "Anna Paquin",  # The Piano
    1994: "Dianne Wiest",  # Bullets over Broadway
    1995: "Mira Sorvino",  # Mighty Aphrodite
    1996: "Juliette Binoche",  # The English Patient
    1997: "Kim Basinger",  # L.A. Confidential
    1998: "Judi Dench",  # Shakespeare in Love
    1999: "Angelina Jolie",  # Girl, Interrupted
    2000: "Marcia Gay Harden",  # Pollock
    2001: "Jennifer Connelly",  # A Beautiful Mind
    2002: "Catherine Zeta-Jones",  # Chicago
    2003: "Renée Zellweger",  # Cold Mountain
    2004: "Cate Blanchett",  # The Aviator
    2005: "Rachel Weisz",  # The Constant Gardener
    2006: "Jennifer Hudson",  # Dreamgirls
    2007: "Tilda Swinton",  # Michael Clayton
    2008: "Penélope Cruz",  # Vicky Cristina Barcelona
    2009: "Mo'Nique",  # Precious
    2010: "Melissa Leo",  # The Fighter
    2011: "Octavia Spencer",  # The Help
    2012: "Anne Hathaway",  # Les Misérables
    2013: "Lupita Nyong'o",  # 12 Years a Slave
    2014: "Patricia Arquette",  # Boyhood
    2015: "Alicia Vikander",  # The Danish Girl
    2016: "Viola Davis",  # Fences
    2017: "Allison Janney",  # I, Tonya
    2018: "Regina King",  # If Beale Street Could Talk
    2019: "Laura Dern",  # Marriage Story
    2021: "Ariana DeBose",  # West Side Story
    # 2022: "Jamie Lee Curtis",  # Everything Everywhere All at Once
    # 2023: "Da'Vine Joy Randolph",  # The Holdovers
    # 2024: "Zoe Saldaña",  # Emilia Pérez
}

# Oscar Best Supporting Actress birth years
OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR = {
    "Jane Darwell": 1879,
    "Mary Astor": 1906,
    "Teresa Wright": 1918,
    "Katina Paxinou": 1900,
    "Ethel Barrymore": 1879,
    "Anne Revere": 1903,
    "Anne Baxter": 1923,
    "Celeste Holm": 1917,
    "Claire Trevor": 1910,
    "Mercedes McCambridge": 1916,
    "Josephine Hull": 1877,
    "Kim Hunter": 1922,
    "Gloria Grahame": 1923,
    "Donna Reed": 1921,
    "Eva Marie Saint": 1924,
    "Miyoshi Umeki": 1929,
    "Wendy Hiller": 1912,
    "Shelley Winters": 1920,
    "Shirley Jones": 1934,
    "Rita Moreno": 1931,
    "Patty Duke": 1946,
    "Margaret Rutherford": 1892,
    "Sandy Dennis": 1937,
    "Estelle Parsons": 1927,
    "Ruth Gordon": 1896,
    "Goldie Hawn": 1945,
    "Helen Hayes": 1900,
    "Cloris Leachman": 1926,
    "Eileen Heckart": 1919,
    "Tatum O'Neal": 1963,
    "Ingrid Bergman": 1915,
    "Beatrice Straight": 1914,
    "Vanessa Redgrave": 1937,
    "Maggie Smith": 1934,
    "Meryl Streep": 1949,
    "Mary Steenburgen": 1953,
    "Maureen Stapleton": 1925,
    "Jessica Lange": 1949,
    "Linda Hunt": 1945,
    "Peggy Ashcroft": 1907,
    "Anjelica Huston": 1951,
    "Dianne Wiest": 1948,
    "Olympia Dukakis": 1931,
    "Geena Davis": 1956,
    "Brenda Fricker": 1945,
    "Whoopi Goldberg": 1955,
    "Mercedes Ruehl": 1948,
    "Marisa Tomei": 1964,
    "Anna Paquin": 1982,
    "Mira Sorvino": 1967,
    "Juliette Binoche": 1964,
    "Kim Basinger": 1953,
    "Judi Dench": 1934,
    "Angelina Jolie": 1975,
    "Marcia Gay Harden": 1959,
    "Jennifer Connelly": 1970,
    "Catherine Zeta-Jones": 1969,
    "Renée Zellweger": 1969,
    "Cate Blanchett": 1969,
    "Rachel Weisz": 1970,
    "Jennifer Hudson": 1981,
    "Tilda Swinton": 1960,
    "Penélope Cruz": 1974,
    "Mo'Nique": 1967,
    "Melissa Leo": 1960,
    "Octavia Spencer": 1970,
    "Anne Hathaway": 1982,
    "Lupita Nyong'o": 1983,
    "Patricia Arquette": 1968,
    "Alicia Vikander": 1988,
    "Viola Davis": 1965,
    "Allison Janney": 1959,
    "Regina King": 1971,
    "Laura Dern": 1967,
    "Ariana DeBose": 1991,
    "Jamie Lee Curtis": 1958,
}

# Oscar Best Supporting Actress birth day of month
OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY = {
    "Jane Darwell": 15,
    "Mary Astor": 3,
    "Teresa Wright": 27,
    "Katina Paxinou": 17,
    "Ethel Barrymore": 15,
    "Anne Revere": 25,
    "Anne Baxter": 7,
    "Celeste Holm": 29,
    "Claire Trevor": 8,
    "Mercedes McCambridge": 16,
    "Josephine Hull": 3,
    "Kim Hunter": 12,
    "Gloria Grahame": 28,
    "Donna Reed": 27,
    "Eva Marie Saint": 4,
    "Jo Van Fleet": 30,
    "Dorothy Malone": 30,
    "Miyoshi Umeki": 8,
    "Wendy Hiller": 15,
    "Shelley Winters": 18,
    "Shirley Jones": 31,
    "Rita Moreno": 11,
    "Patty Duke": 14,
    "Margaret Rutherford": 11,
    "Lila Kedrova": 9,
    "Shelley Winters": 18,
    "Sandy Dennis": 27,
    "Estelle Parsons": 20,
    "Ruth Gordon": 30,
    "Goldie Hawn": 21,
    "Helen Hayes": 10,
    "Cloris Leachman": 30,
    "Eileen Heckart": 29,
    "Tatum O'Neal": 5,
    "Ingrid Bergman": 29,
    "Lee Grant": 31,
    "Beatrice Straight": 2,
    "Vanessa Redgrave": 30,
    "Maggie Smith": 28,
    "Meryl Streep": 22,
    "Mary Steenburgen": 8,
    "Maureen Stapleton": 21,
    "Jessica Lange": 20,
    "Linda Hunt": 2,
    "Peggy Ashcroft": 22,
    "Anjelica Huston": 8,
    "Dianne Wiest": 28,
    "Olympia Dukakis": 20,
    "Geena Davis": 21,
    "Brenda Fricker": 17,
    "Whoopi Goldberg": 13,
    "Mercedes Ruehl": 28,
    "Marisa Tomei": 4,
    "Anna Paquin": 24,
    "Mira Sorvino": 28,
    "Juliette Binoche": 9,
    "Kim Basinger": 8,
    "Judi Dench": 9,
    "Angelina Jolie": 4,
    "Marcia Gay Harden": 14,
    "Jennifer Connelly": 12,
    "Catherine Zeta-Jones": 25,
    "Renée Zellweger": 25,
    "Cate Blanchett": 14,
    "Rachel Weisz": 7,
    "Jennifer Hudson": 12,
    "Tilda Swinton": 5,
    "Penélope Cruz": 28,
    "Mo'Nique": 11,
    "Melissa Leo": 14,
    "Octavia Spencer": 25,
    "Anne Hathaway": 12,
    "Lupita Nyong'o": 1,
    "Patricia Arquette": 8,
    "Alicia Vikander": 3,
    "Viola Davis": 11,
    "Allison Janney": 19,
    "Regina King": 15,
    "Laura Dern": 10,
    "Ariana DeBose": 25,
    "Jamie Lee Curtis": 22,
}

# Oscar Best Supporting Actress by order (starting from ceremony 10)
OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER = {
    9: "Gale Sondergaard",  # Anthony Adverse
    10: "Alice Brady",  # In Old Chicago
    11: "Fay Bainter",  # Jezebel
    12: "Hattie McDaniel",  # Gone with the Wind
    13: "Jane Darwell",  # The Grapes of Wrath
    14: "Mary Astor",  # The Great Lie
    15: "Teresa Wright",  # Mrs. Miniver
    16: "Katina Paxinou",  # For Whom the Bell Tolls
    17: "Ethel Barrymore",  # None but the Lonely Heart
    18: "Anne Revere",  # National Velvet
    19: "Anne Baxter",  # The Razor's Edge
    20: "Celeste Holm",  # Gentleman's Agreement
    21: "Claire Trevor",  # Key Largo
    22: "Mercedes McCambridge",  # All the King's Men
    23: "Josephine Hull",  # Harvey
    24: "Kim Hunter",  # A Streetcar Named Desire
    25: "Gloria Grahame",  # The Bad and the Beautiful
    26: "Donna Reed",  # From Here to Eternity
    27: "Eva Marie Saint",  # On the Waterfront
    28: "Jo Van Fleet",  # East of Eden
    29: "Dorothy Malone",  # Written on the Wind
    30: "Miyoshi Umeki",  # Sayonara
    31: "Wendy Hiller",  # Separate Tables
    32: "Shelley Winters",  # The Diary of Anne Frank
    33: "Shirley Jones",  # Elmer Gantry
    34: "Rita Moreno",  # West Side Story
    35: "Patty Duke",  # The Miracle Worker
    36: "Margaret Rutherford",  # The V.I.P.s
    37: "Lila Kedrova",  # Zorba the Greek
    38: "Shelley Winters",  # A Patch of Blue
    39: "Sandy Dennis",  # Who's Afraid of Virginia Woolf?
    40: "Estelle Parsons",  # Bonnie and Clyde
    41: "Ruth Gordon",  # Rosemary's Baby
    42: "Goldie Hawn",  # Cactus Flower
    43: "Helen Hayes",  # Airport
    44: "Cloris Leachman",  # The Last Picture Show
    45: "Eileen Heckart",  # Butterflies Are Free
    46: "Tatum O'Neal",  # Paper Moon
    47: "Ingrid Bergman",  # Murder on the Orient Express
    48: "Lee Grant",  # Shampoo
    49: "Beatrice Straight",  # Network
    50: "Vanessa Redgrave",  # Julia
    51: "Maggie Smith",  # California Suite
    52: "Meryl Streep",  # Kramer vs. Kramer
    53: "Mary Steenburgen",  # Melvin and Howard
    54: "Maureen Stapleton",  # Reds
    55: "Jessica Lange",  # Tootsie
    56: "Linda Hunt",  # The Year of Living Dangerously
    57: "Peggy Ashcroft",  # A Passage to India
    58: "Anjelica Huston",  # Prizzi's Honor
    59: "Dianne Wiest",  # Hannah and Her Sisters
    60: "Olympia Dukakis",  # Moonstruck
    61: "Geena Davis",  # The Accidental Tourist
    62: "Brenda Fricker",  # My Left Foot
    63: "Whoopi Goldberg",  # Ghost
    64: "Mercedes Ruehl",  # The Fisher King
    65: "Marisa Tomei",  # My Cousin Vinny
    66: "Anna Paquin",  # The Piano
    67: "Dianne Wiest",  # Bullets over Broadway
    68: "Mira Sorvino",  # Mighty Aphrodite
    69: "Juliette Binoche",  # The English Patient
    70: "Kim Basinger",  # L.A. Confidential
    71: "Judi Dench",  # Shakespeare in Love
    72: "Angelina Jolie",  # Girl, Interrupted
    73: "Marcia Gay Harden",  # Pollock
    74: "Jennifer Connelly",  # A Beautiful Mind
    75: "Catherine Zeta-Jones",  # Chicago
    76: "Renée Zellweger",  # Cold Mountain
    77: "Cate Blanchett",  # The Aviator
    78: "Rachel Weisz",  # The Constant Gardener
    79: "Jennifer Hudson",  # Dreamgirls
    80: "Tilda Swinton",  # Michael Clayton
    81: "Penélope Cruz",  # Vicky Cristina Barcelona
    82: "Mo'Nique",  # Precious
    83: "Melissa Leo",  # The Fighter
    84: "Octavia Spencer",  # The Help
    85: "Anne Hathaway",  # Les Misérables
    86: "Lupita Nyong'o",  # 12 Years a Slave
    87: "Patricia Arquette",  # Boyhood
    88: "Alicia Vikander",  # The Danish Girl
    89: "Viola Davis",  # Fences
    90: "Allison Janney",  # I, Tonya
    91: "Regina King",  # If Beale Street Could Talk
    92: "Laura Dern",  # Marriage Story
    94: "Ariana DeBose",  # West Side Story
    95: "Jamie Lee Curtis",  # Everything Everywhere All at Once
    # 96: "Da'Vine Joy Randolph",  # The Holdovers
    # 97: "Zoe Saldaña",  # Emilia Pérez
}

# Nobel Prize in Peace (single winners only)
NOBEL_PEACE = {
    1903: "Randal Cremer",
    1905: "Bertha von Suttner",
    1906: "Theodore Roosevelt",
    # 1910: "International Peace Bureau",
    1912: "Elihu Root",
    1913: "Henri La Fontaine",
    # 1914: Not awarded
    # 1915: Not awarded
    # 1916: Not awarded
    1917: "International Committee of the Red Cross",
    # 1918: Not awarded
    1919: "Woodrow Wilson",
    1920: "Léon Bourgeois",
    1922: "Fridtjof Nansen",
    # 1923: Not awarded
    # 1924: Not awarded
    # 1928: Not awarded
    1929: "Frank B. Kellogg",
    1930: "Nathan Söderblom",
    # 1932: Not awarded
    1933: "Norman Angell",
    1934: "Arthur Henderson",
    1935: "Carl von Ossietzky",
    1936: "Carlos Saavedra Lamas",
    1937: "Robert Cecil",
    1938: "Nansen International Office for Refugees",
    # 1939: Not awarded
    # 1940: Not awarded
    # 1941: Not awarded
    # 1942: Not awarded
    # 1943: Not awarded
    1944: "International Committee of the Red Cross",
    1945: "Cordell Hull",
    # 1948: Not awarded
    1949: "John Boyd Orr",
    1950: "Ralph Bunche",
    1951: "Léon Jouhaux",
    1952: "Albert Schweitzer",
    1953: "George C. Marshall",
    1954: "Office of the United Nations High Commissioner for Refugees",
    # 1955: Not awarded
    # 1956: Not awarded
    1957: "Lester B. Pearson",
    1958: "Georges Pire",
    1959: "Philip Noel-Baker",
    1960: "Albert Lutuli",
    1961: "Dag Hammarskjöld",
    1962: "Linus Pauling",
    1964: "Martin Luther King Jr.",
    1965: "UNICEF",
    # 1966: Not awarded
    # 1967: Not awarded
    1968: "René Cassin",
    1969: "International Labour Organization",
    1970: "Norman Borlaug",
    1971: "Willy Brandt",
    # 1972: Not awarded
    1975: "Andrei Sakharov",
    1977: "Amnesty International",
    1979: "Mother Teresa",
    1980: "Adolfo Pérez Esquivel",
    1981: "Office of the United Nations High Commissioner for Refugees",
    1983: "Lech Wałęsa",
    1984: "Desmond Tutu",
    1985: "International Physicians for the Prevention of Nuclear War",
    1986: "Elie Wiesel",
    1987: "Óscar Arias",
    1988: "United Nations Peacekeeping Forces",
    1990: "Mikhail Gorbachev",
    1991: "Aung San Suu Kyi",
    1992: "Rigoberta Menchú",
    1999: "Médecins Sans Frontières",
    2000: "Kim Dae-jung",
    2002: "Jimmy Carter",
    2003: "Shirin Ebadi",
    2004: "Wangari Maathai",
    2008: "Martti Ahtisaari",
    2009: "Barack Obama",
    2010: "Liu Xiaobo",
    2012: "European Union",
    2013: "Organisation for the Prohibition of Chemical Weapons",
    # 2015: "National Dialogue Quartet",
    2016: "Juan Manuel Santos",
    2017: "International Campaign to Abolish Nuclear Weapons",
    2019: "Abiy Ahmed",
    2020: "World Food Programme",
    # 2023: "Narges Mohammadi",
    # 2024: "Nihon Hidankyo",
    # 2025: "María Corina Machado",
}

# Nobel Prize in Peace birth years (individual winners only)
NOBEL_PEACE_BIRTH_YEAR = {
    "Henry Dunant": 1828,
    "Élie Ducommun": 1833,
    "Randal Cremer": 1828,
    "Theodore Roosevelt": 1858,
    "Ernesto Moneta": 1833,
    "Klas Pontus Arnoldson": 1844,
    "Auguste Beernaert": 1829,
    "Tobias Asser": 1838,
    "Elihu Root": 1845,
    "Henri La Fontaine": 1854,
    "Woodrow Wilson": 1856,
    "Léon Bourgeois": 1851,
    "Hjalmar Branting": 1860,
    "Fridtjof Nansen": 1861,
    "Austen Chamberlain": 1863,
    "Aristide Briand": 1862,
    "Ferdinand Buisson": 1841,
    "Frank B. Kellogg": 1856,
    "Nathan Söderblom": 1866,
    "Jane Addams": 1860,
    "Norman Angell": 1872,
    "Arthur Henderson": 1863,
    "Carl von Ossietzky": 1889,
    "Carlos Saavedra Lamas": 1878,
    # "Robert Cecil": 1864,
    "Cordell Hull": 1871,
    "Emily Greene Balch": 1867,
    "John Boyd Orr": 1880,
    "Ralph Bunche": 1904,
    "Léon Jouhaux": 1879,
    "Albert Schweitzer": 1875,
    "George Marshall": 1880,
    "Lester B. Pearson": 1897,
    "Georges Pire": 1910,
    "Philip Noel-Baker": 1889,
    # "Albert Lutuli": 1898,
    "Dag Hammarskjöld": 1905,
    "Linus Pauling": 1901,
    "Martin Luther King Jr.": 1929,
    "René Cassin": 1887,
    "Norman Borlaug": 1914,
    "Willy Brandt": 1913,
    "Seán MacBride": 1904,
    "Andrei Sakharov": 1921,
    "Betty Williams": 1943,
    "Anwar Sadat": 1918,
    "Mother Teresa": 1910,
    "Adolfo Pérez Esquivel": 1931,
    "Alva Myrdal": 1902,
    "Lech Wałęsa": 1943,
    "Desmond Tutu": 1931,
    "Elie Wiesel": 1928,
    "Óscar Arias": 1940,
    "Tenzin Gyatso": 1935,
    "Aung San Suu Kyi": 1945,
    "Rigoberta Menchú": 1959,
    "Nelson Mandela": 1918,
    "Joseph Rotblat": 1908,
    "Carlos Filipe Ximenes Belo": 1948,
    "Jody Williams": 1950,
    "John Hume": 1937,
    "Jimmy Carter": 1924,
    "Shirin Ebadi": 1947,
    "Wangari Maathai": 1940,
    "Muhammad Yunus": 1940,
    "Al Gore": 1948,
    "Martti Ahtisaari": 1937,
    "Barack Obama": 1961,
    "Liu Xiaobo": 1955,
    "Ellen Johnson Sirleaf": 1938,
    "Kailash Satyarthi": 1954,
    "Juan Manuel Santos": 1951,
    "Denis Mukwege": 1955,
    "Abiy Ahmed": 1976,
    "Maria Ressa": 1963,
    "Ales Bialiatski": 1962,
    "Narges Mohammadi": 1972,
}

# Nobel Prize in Peace birth day of month (individual winners only)
NOBEL_PEACE_BIRTH_DAY = {
    "Henry Dunant": 8,
    "Élie Ducommun": 19,
    "Randal Cremer": 18,
    "Theodore Roosevelt": 27,
    "Ernesto Moneta": 20,
    "Klas Pontus Arnoldson": 27,
    "Auguste Beernaert": 26,
    "Tobias Asser": 28,
    "Elihu Root": 15,
    "Henri La Fontaine": 22,
    "Woodrow Wilson": 28,
    "Léon Bourgeois": 21,
    "Hjalmar Branting": 23,
    "Fridtjof Nansen": 10,
    "Austen Chamberlain": 16,
    "Aristide Briand": 28,
    "Ferdinand Buisson": 20,
    "Frank B. Kellogg": 22,
    "Nathan Söderblom": 15,
    "Jane Addams": 6,
    "Norman Angell": 26,
    "Arthur Henderson": 13,
    "Carl von Ossietzky": 3,
    "Carlos Saavedra Lamas": 1,
    # "Robert Cecil": 14,
    "Cordell Hull": 2,
    "Emily Greene Balch": 8,
    "John Boyd Orr": 23,
    "Ralph Bunche": 7,
    "Léon Jouhaux": 1,
    "Albert Schweitzer": 14,
    "George Marshall": 31,
    "Lester B. Pearson": 23,
    "Georges Pire": 10,
    "Philip Noel-Baker": 1,
    # "Albert Lutuli": 1,
    "Dag Hammarskjöld": 29,
    "Linus Pauling": 28,
    "Martin Luther King Jr.": 15,
    "René Cassin": 5,
    "Norman Borlaug": 25,
    "Willy Brandt": 18,
    "Seán MacBride": 26,
    "Andrei Sakharov": 21,
    "Betty Williams": 22,
    "Anwar Sadat": 25,
    "Mother Teresa": 26,
    "Adolfo Pérez Esquivel": 26,
    "Alva Myrdal": 31,
    "Lech Wałęsa": 29,
    "Desmond Tutu": 7,
    "Elie Wiesel": 30,
    "Óscar Arias": 13,
    "Tenzin Gyatso": 6,
    "Aung San Suu Kyi": 19,
    "Rigoberta Menchú": 9,
    "Nelson Mandela": 18,
    "Joseph Rotblat": 4,
    "Carlos Filipe Ximenes Belo": 3,
    "Jody Williams": 9,
    "John Hume": 18,
    "Jimmy Carter": 1,
    "Shirin Ebadi": 21,
    "Wangari Maathai": 1,
    "Muhammad Yunus": 28,
    "Al Gore": 31,
    "Martti Ahtisaari": 23,
    "Barack Obama": 4,
    "Liu Xiaobo": 28,
    "Ellen Johnson Sirleaf": 29,
    "Kailash Satyarthi": 11,
    "Juan Manuel Santos": 10,
    "Denis Mukwege": 1,
    "Abiy Ahmed": 15,
    "Maria Ressa": 2,
    "Ales Bialiatski": 25,
    "Narges Mohammadi": 21,
}

# Nobel Prize in Chemistry (single winners only)
NOBEL_CHEMISTRY = {
    1901: "Jacobus Henricus van 't Hoff",
    1902: "Emil Fischer",
    1903: "Svante Arrhenius",
    1904: "William Ramsay",
    1905: "Adolf von Baeyer",
    1906: "Henri Moissan",
    1907: "Eduard Buchner",
    1908: "Ernest Rutherford",
    1909: "Wilhelm Ostwald",
    1910: "Otto Wallach",
    1911: "Marie Curie",
    1913: "Alfred Werner",
    1914: "Theodore William Richards",
    1915: "Richard Willstätter",
    # 1916: Not awarded
    # 1917: Not awarded
    1918: "Fritz Haber",
    # 1919: Not awarded
    1920: "Walther Nernst",
    1921: "Frederick Soddy",
    1922: "Francis William Aston",
    1923: "Fritz Pregl",
    # 1924: Not awarded
    1925: "Richard Zsigmondy",
    1926: "Theodor Svedberg",
    1927: "Heinrich Otto Wieland",
    1928: "Adolf Otto Reinhold Windaus",
    1930: "Hans Fischer",
    1932: "Irving Langmuir",
    # 1933: Not awarded
    1934: "Harold Urey",
    1936: "Petrus Debye",
    1938: "Richard Kuhn",
    # 1940: Not awarded
    # 1941: Not awarded
    # 1942: Not awarded
    1943: "George de Hevesy",
    1944: "Otto Hahn",
    1945: "Artturi Virtanen",
    1947: "Robert Robinson",
    1948: "Arne Tiselius",
    1949: "William Francis Giauque",
    1953: "Hermann Staudinger",
    1954: "Linus Pauling",
    1955: "Vincent du Vigneaud",
    1957: "Alexander R. Todd",
    1958: "Frederick Sanger",
    1959: "Jaroslav Heyrovský",
    1960: "Willard Libby",
    1961: "Melvin Calvin",
    1964: "Dorothy Hodgkin",
    1965: "Robert Burns Woodward",
    1966: "Robert S. Mulliken",
    1968: "Lars Onsager",
    1970: "Luis Federico Leloir",
    1971: "Gerhard Herzberg",
    1974: "Paul Flory",
    1976: "William N. Lipscomb",
    1977: "Ilya Prigogine",
    1978: "Peter D. Mitchell",
    1982: "Aaron Klug",
    1983: "Henry Taube",
    1984: "Robert Bruce Merrifield",
    1990: "Elias James Corey",
    1991: "Richard R. Ernst",
    1992: "Rudolph A. Marcus",
    1994: "George A. Olah",
    1999: "Ahmed Zewail",
    2006: "Roger D. Kornberg",
    2007: "Gerhard Ertl",
    2011: "Dan Shechtman",
}

# Nobel Prize in Chemistry birth years (single winners only)
NOBEL_CHEMISTRY_BIRTH_YEAR = {
    "Jacobus Henricus van 't Hoff": 1852,
    "Emil Fischer": 1852,
    "Svante Arrhenius": 1859,
    "William Ramsay": 1852,
    "Adolf von Baeyer": 1835,
    "Eduard Buchner": 1860,
    "Ernest Rutherford": 1871,
    "Wilhelm Ostwald": 1853,
    "Otto Wallach": 1847,
    "Marie Curie": 1867,
    "Alfred Werner": 1866,
    "Theodore William Richards": 1868,
    "Richard Willstätter": 1872,
    "Fritz Haber": 1868,
    "Walther Nernst": 1864,
    "Frederick Soddy": 1877,
    "Francis William Aston": 1877,
    "Fritz Pregl": 1869,
    "Richard Zsigmondy": 1865,
    "Theodor Svedberg": 1884,
    "Heinrich Otto Wieland": 1877,
    "Adolf Windaus": 1876,
    "Arthur Harden": 1865,
    "Hans Fischer": 1881,
    "Carl Bosch": 1874,
    "Irving Langmuir": 1881,
    "Harold Urey": 1893,
    "Frédéric Joliot": 1900,
    "Peter Debye": 1884,
    "Norman Haworth": 1883,
    "Richard Kuhn": 1900,
    "Adolf Butenandt": 1903,
    "George de Hevesy": 1885,
    "Otto Hahn": 1879,
    "Artturi Virtanen": 1895,
    "James B. Sumner": 1887,
    "Robert Robinson": 1886,
    "Arne Tiselius": 1902,
    "William Giauque": 1895,
    "Otto Diels": 1876,
    "Edwin McMillan": 1907,
    "Archer Martin": 1910,
    "Hermann Staudinger": 1881,
    "Linus Pauling": 1901,
    "Vincent du Vigneaud": 1901,
    "Cyril Hinshelwood": 1897,
    "Alexander Todd": 1907,
    "Frederick Sanger": 1918,
    "Jaroslav Heyrovský": 1890,
    "Melvin Calvin": 1911,
    "Max Perutz": 1914,
    "Karl Ziegler": 1898,
    "Dorothy Hodgkin": 1910,
    "Robert Burns Woodward": 1917,
    "Robert S. Mulliken": 1896,
    "Manfred Eigen": 1927,
    "Lars Onsager": 1903,
    "Derek Barton": 1918,
    "Luis Leloir": 1906,
    "Gerhard Herzberg": 1904,
    "Christian Anfinsen": 1916,
    "Ernst Otto Fischer": 1918,
    "Paul Flory": 1910,
    "John Cornforth": 1917,
    "William Lipscomb": 1919,
    "Ilya Prigogine": 1917,
    "Peter Mitchell": 1920,
    "Herbert Charles Brown": 1912,
    "Paul Berg": 1926,
    "Kenichi Fukui": 1918,
    "Aaron Klug": 1926,
    "Henry Taube": 1915,
    "Robert Bruce Merrifield": 1921,
    "Herbert A. Hauptman": 1917,
    "Dudley R. Herschbach": 1932,
    "Donald J. Cram": 1919,
    "Johann Deisenhofer": 1943,
    "Sidney Altman": 1939,
    "Elias James Corey": 1928,
    "Richard R. Ernst": 1933,
    "Rudolph A. Marcus": 1923,
    "Kary Mullis": 1944,
    "George Olah": 1927,
    "Paul J. Crutzen": 1933,
    "Robert F. Curl Jr.": 1933,
    "Paul D. Boyer": 1918,
    "Walter Kohn": 1923,
    "Ahmed Zewail": 1946,
    "Alan Heeger": 1936,
    "William Standish Knowles": 1917,
    "John Fenn": 1917,
    "Peter Agre": 1949,
    "Aaron Ciechanover": 1947,
    "Yves Chauvin": 1930,
    "Roger D. Kornberg": 1947,
    "Gerhard Ertl": 1936,
    "Osamu Shimomura": 1928,
    # "Venkatraman Ramakrishnan": 1952,
    "Richard F. Heck": 1931,
    "Dan Shechtman": 1941,
    "Martin Karplus": 1930,
    "Eric Betzig": 1960,
    "Tomas Lindahl": 1938,
    "Jean-Pierre Sauvage": 1944,
    "Jacques Dubochet": 1942,
    "Frances Arnold": 1956,
    "John B. Goodenough": 1922,
    "Benjamin List": 1968,
    "Carolyn Bertozzi": 1966,
}

# Nobel Prize in Chemistry birth day of month (single winners only)
NOBEL_CHEMISTRY_BIRTH_DAY = {
    "Jacobus Henricus van 't Hoff": 30,
    "Emil Fischer": 9,
    "Svante Arrhenius": 19,
    "William Ramsay": 2,
    "Adolf von Baeyer": 31,
    "Eduard Buchner": 20,
    "Ernest Rutherford": 30,
    "Wilhelm Ostwald": 2,
    "Otto Wallach": 27,
    "Marie Curie": 7,
    "Alfred Werner": 12,
    "Theodore William Richards": 31,
    "Richard Willstätter": 13,
    "Fritz Haber": 9,
    "Walther Nernst": 25,
    "Frederick Soddy": 2,
    "Francis William Aston": 1,
    "Fritz Pregl": 3,
    "Richard Zsigmondy": 1,
    "Theodor Svedberg": 30,
    "Heinrich Otto Wieland": 4,
    "Adolf Windaus": 25,
    "Arthur Harden": 12,
    "Hans Fischer": 27,
    "Carl Bosch": 27,
    "Irving Langmuir": 31,
    "Harold Urey": 29,
    "Frédéric Joliot": 19,
    "Peter Debye": 24,
    "Norman Haworth": 19,
    "Richard Kuhn": 3,
    "Adolf Butenandt": 24,
    "George de Hevesy": 1,
    "Otto Hahn": 8,
    "Artturi Virtanen": 15,
    "James B. Sumner": 19,
    "Robert Robinson": 13,
    "Arne Tiselius": 10,
    "William Giauque": 12,
    "Otto Diels": 23,
    "Edwin McMillan": 18,
    "Archer Martin": 1,
    "Hermann Staudinger": 23,
    "Linus Pauling": 28,
    "Vincent du Vigneaud": 18,
    "Cyril Hinshelwood": 19,
    "Alexander Todd": 2,
    "Frederick Sanger": 13,
    "Jaroslav Heyrovský": 20,
    "Melvin Calvin": 8,
    "Max Perutz": 19,
    "Karl Ziegler": 26,
    "Dorothy Hodgkin": 12,
    "Robert Burns Woodward": 10,
    "Robert S. Mulliken": 7,
    "Manfred Eigen": 9,
    "Lars Onsager": 27,
    "Derek Barton": 8,
    "Luis Leloir": 6,
    "Gerhard Herzberg": 25,
    "Christian Anfinsen": 26,
    "Ernst Otto Fischer": 10,
    "Paul Flory": 19,
    "John Cornforth": 7,
    "William Lipscomb": 9,
    "Ilya Prigogine": 25,
    "Peter Mitchell": 29,
    "Herbert Charles Brown": 22,
    "Paul Berg": 30,
    "Kenichi Fukui": 4,
    "Aaron Klug": 11,
    "Henry Taube": 30,
    "Robert Bruce Merrifield": 15,
    "Herbert A. Hauptman": 14,
    "Dudley R. Herschbach": 18,
    "Donald J. Cram": 22,
    "Johann Deisenhofer": 30,
    "Sidney Altman": 7,
    "Elias James Corey": 12,
    "Richard R. Ernst": 14,
    "Rudolph A. Marcus": 21,
    "Kary Mullis": 28,
    "George Olah": 22,
    "Paul J. Crutzen": 3,
    "Robert F. Curl Jr.": 23,
    "Paul D. Boyer": 31,
    "Walter Kohn": 9,
    "Ahmed Zewail": 26,
    "Alan Heeger": 22,
    "William Standish Knowles": 1,
    "John Fenn": 15,
    "Peter Agre": 30,
    "Aaron Ciechanover": 1,
    "Yves Chauvin": 10,
    "Roger D. Kornberg": 24,
    "Gerhard Ertl": 10,
    "Osamu Shimomura": 27,
    # "Venkatraman Ramakrishnan": 1,
    "Richard F. Heck": 15,
    "Dan Shechtman": 24,
    "Martin Karplus": 15,
    "Eric Betzig": 13,
    "Tomas Lindahl": 28,
    "Jean-Pierre Sauvage": 21,
    "Jacques Dubochet": 8,
    "Frances Arnold": 25,
    "John B. Goodenough": 25,
    "Benjamin List": 11,
    "Carolyn Bertozzi": 10,
}

# Nobel Prize in Physics (single winners only)
NOBEL_PHYSICS = {
    1901: "Wilhelm Conrad Röntgen",
    1904: "Lord Rayleigh",
    1905: "Philipp Lenard",
    1906: "J. J. Thomson",
    1907: "Albert A. Michelson",
    1908: "Gabriel Lippmann",
    1910: "Johannes Diderik van der Waals",
    1911: "Wilhelm Wien",
    # 1912: "Nils Gustaf Dalén",
    1913: "Heike Kamerlingh Onnes",
    1914: "Max von Laue",
    # 1916: Not awarded
    1917: "Charles Glover Barkla",
    1918: "Max Planck",
    1919: "Johannes Stark",
    1920: "Charles Édouard Guillaume",
    1921: "Albert Einstein",
    1922: "Niels Bohr",
    1923: "Robert A. Millikan",
    # 1924: "Manne Siegbahn",
    1926: "Jean Baptiste Perrin",
    1928: "Owen Willans Richardson",
    1929: "Louis de Broglie",
    1930: "Chandrasekhara Venkata Raman",
    # 1931: Not awarded
    1932: "Werner Heisenberg",
    # 1934: Not awarded
    1935: "James Chadwick",
    1938: "Enrico Fermi",
    1939: "Ernest Lawrence",
    # 1940: Not awarded
    # 1941: Not awarded
    # 1942: Not awarded
    1943: "Otto Stern",
    1944: "Isidor Isaac Rabi",
    1945: "Wolfgang Pauli",
    1946: "Percy Williams Bridgman",
    1947: "Edward Victor Appleton",
    1948: "Patrick Blackett",
    1949: "Hideki Yukawa",
    1950: "Cecil Frank Powell",
    1953: "Frits Zernike",
    1960: "Donald A. Glaser",
    1962: "Lev Landau",
    1966: "Alfred Kastler",
    1967: "Hans Bethe",
    1968: "Luis Walter Alvarez",
    1969: "Murray Gell-Mann",
    1971: "Dennis Gabor",
    1982: "Kenneth G. Wilson",
    1985: "Klaus von Klitzing",
    1991: "Pierre-Gilles de Gennes",
    1992: "Georges Charpak",
}

# Nobel Prize in Physics birth years (single winners only)
NOBEL_PHYSICS_BIRTH_YEAR = {
    "Wilhelm Röntgen": 1845,
    "Hendrik Lorentz": 1853,
    "Henri Becquerel": 1852,
    "Lord Rayleigh": 1842,
    "Philipp Lenard": 1862,
    "J. J. Thomson": 1856,
    "Albert Michelson": 1852,
    "Gabriel Lippmann": 1845,
    "Guglielmo Marconi": 1874,
    "Johannes Diderik van der Waals": 1837,
    "Wilhelm Wien": 1864,
    "Nils Gustaf Dalén": 1869,
    "Heike Kamerlingh Onnes": 1853,
    "Max von Laue": 1879,
    "William Henry Bragg": 1862,
    "Charles Glover Barkla": 1877,
    "Max Planck": 1858,
    "Johannes Stark": 1874,
    "Charles Edouard Guillaume": 1861,
    "Albert Einstein": 1879,
    "Niels Bohr": 1885,
    "Robert Millikan": 1868,
    # "Manne Siegbahn": 1886,
    "James Franck": 1882,
    "Jean Baptiste Perrin": 1870,
    "Arthur Compton": 1892,
    "Owen Willans Richardson": 1879,
    "Louis de Broglie": 1892,
    "Chandrasekhara Venkata Raman": 1888,
    "Werner Heisenberg": 1901,
    "Erwin Schrödinger": 1887,
    "James Chadwick": 1891,
    "Victor Francis Hess": 1883,
    "Clinton Davisson": 1881,
    "Enrico Fermi": 1901,
    "Ernest Lawrence": 1901,
    "Otto Stern": 1888,
    "Isidor Isaac Rabi": 1898,
    "Wolfgang Pauli": 1900,
    "Percy Williams Bridgman": 1882,
    "Edward Victor Appleton": 1892,
    "Patrick Maynard Stuart Blackett": 1897,
    "Hideki Yukawa": 1907,
    "Cecil Powell": 1903,
    "John Cockcroft": 1897,
    "Felix Bloch": 1905,
    "Frits Zernike": 1888,
    "Max Born": 1882,
    "Willis Lamb": 1913,
    "William Shockley": 1910,
    "Chen Ning Yang": 1922,
    "Pavel Cherenkov": 1904,
    "Emilio Segrè": 1905,
    "Donald Glaser": 1926,
    "Robert Hofstadter": 1915,
    "Lev Landau": 1908,
    "Eugene Wigner": 1902,
    "Charles Townes": 1915,
    "Sin-Itiro Tomonaga": 1906,
    "Alfred Kastler": 1902,
    "Hans Bethe": 1906,
    "Luis Alvarez": 1911,
    "Murray Gell-Mann": 1929,
    "Hannes Alfvén": 1908,
    "Dennis Gabor": 1900,
    "John Bardeen": 1908,
    "Leo Esaki": 1925,
    "Martin Ryle": 1918,
    "Aage Bohr": 1922,
    "Burton Richter": 1931,
    "Philip Anderson": 1923,
    # "Pyotr Kapitsa": 1894,
    "Sheldon Glashow": 1932,
    "James Cronin": 1931,
    "Nicolaas Bloembergen": 1920,
    "Kenneth Wilson": 1936,
    "Subrahmanyan Chandrasekhar": 1910,
    "Carlo Rubbia": 1934,
    "Klaus von Klitzing": 1943,
    "Ernst Ruska": 1906,
    "Georg Bednorz": 1950,
    "Leon Lederman": 1922,
    "Norman Ramsey": 1915,
    "Jerome Friedman": 1930,
    "Pierre-Gilles de Gennes": 1932,
    "Georges Charpak": 1924,
    "Russell Hulse": 1950,
    "Bertram Brockhouse": 1918,
    "Martin Perl": 1927,
    # "David Lee": 1931,
    "Steven Chu": 1948,
    "Robert Laughlin": 1950,
    "Gerardus 't Hooft": 1946,
    "Zhores Alferov": 1930,
    "Eric Cornell": 1961,
    "Raymond Davis Jr.": 1914,
    "Alexei Abrikosov": 1928,
    "David Gross": 1941,
    "Roy Glauber": 1925,
    "John Mather": 1946,
    "Albert Fert": 1938,
    "Yoichiro Nambu": 1921,
    "Charles Kao": 1933,
    "Andre Geim": 1958,
    "Saul Perlmutter": 1959,
    "Serge Haroche": 1944,
    "François Englert": 1932,
    "Isamu Akasaki": 1929,
    "Takaaki Kajita": 1959,
    "Duncan Haldane": 1951,
    "Rainer Weiss": 1932,
    "Arthur Ashkin": 1922,
    "James Peebles": 1935,
    "Roger Penrose": 1931,
    "Syukuro Manabe": 1931,
    "Alain Aspect": 1947,
}

# Nobel Prize in Physics birth day of month (single winners only)
NOBEL_PHYSICS_BIRTH_DAY = {
    "Wilhelm Röntgen": 27,
    "Hendrik Lorentz": 18,
    "Henri Becquerel": 15,
    "Lord Rayleigh": 12,
    "Philipp Lenard": 7,
    "J. J. Thomson": 18,
    "Albert Michelson": 19,
    "Gabriel Lippmann": 16,
    "Guglielmo Marconi": 25,
    "Johannes Diderik van der Waals": 23,
    "Wilhelm Wien": 13,
    "Nils Gustaf Dalén": 30,
    "Heike Kamerlingh Onnes": 21,
    "Max von Laue": 9,
    "William Henry Bragg": 2,
    "Charles Glover Barkla": 7,
    "Max Planck": 23,
    "Johannes Stark": 15,
    "Charles Edouard Guillaume": 15,
    "Albert Einstein": 14,
    "Niels Bohr": 7,
    "Robert Millikan": 22,
    # "Manne Siegbahn": 3,
    "James Franck": 26,
    "Jean Baptiste Perrin": 30,
    "Arthur Compton": 10,
    "Owen Willans Richardson": 26,
    "Louis de Broglie": 15,
    "Chandrasekhara Venkata Raman": 7,
    "Werner Heisenberg": 5,
    "Erwin Schrödinger": 12,
    "James Chadwick": 20,
    "Victor Francis Hess": 24,
    "Clinton Davisson": 22,
    "Enrico Fermi": 29,
    "Ernest Lawrence": 8,
    "Otto Stern": 17,
    "Isidor Isaac Rabi": 29,
    "Wolfgang Pauli": 25,
    "Percy Williams Bridgman": 21,
    "Edward Victor Appleton": 6,
    "Patrick Maynard Stuart Blackett": 18,
    "Hideki Yukawa": 23,
    "Cecil Powell": 5,
    "John Cockcroft": 27,
    "Felix Bloch": 23,
    "Frits Zernike": 16,
    "Max Born": 11,
    "Willis Lamb": 12,
    "William Shockley": 13,
    # "Chen Ning Yang": 1,
    "Pavel Cherenkov": 28,
    "Emilio Segrè": 1,
    "Donald Glaser": 21,
    "Robert Hofstadter": 5,
    "Lev Landau": 22,
    "Eugene Wigner": 17,
    "Charles Townes": 28,
    "Sin-Itiro Tomonaga": 31,
    "Alfred Kastler": 3,
    "Hans Bethe": 2,
    "Luis Alvarez": 13,
    "Murray Gell-Mann": 15,
    "Hannes Alfvén": 30,
    "Dennis Gabor": 5,
    "John Bardeen": 23,
    "Leo Esaki": 12,
    "Martin Ryle": 27,
    "Aage Bohr": 19,
    "Burton Richter": 22,
    "Philip Anderson": 13,
    # "Pyotr Kapitsa": 8,
    "Sheldon Glashow": 5,
    "James Cronin": 29,
    "Nicolaas Bloembergen": 11,
    "Kenneth Wilson": 8,
    "Subrahmanyan Chandrasekhar": 19,
    "Carlo Rubbia": 31,
    "Klaus von Klitzing": 28,
    "Ernst Ruska": 25,
    "Georg Bednorz": 16,
    "Leon Lederman": 15,
    "Norman Ramsey": 27,
    "Jerome Friedman": 28,
    "Pierre-Gilles de Gennes": 24,
    "Georges Charpak": 1,
    "Russell Hulse": 28,
    "Bertram Brockhouse": 15,
    "Martin Perl": 24,
    # "David Lee": 20,
    "Steven Chu": 28,
    "Robert Laughlin": 1,
    "Gerardus 't Hooft": 5,
    "Zhores Alferov": 15,
    "Eric Cornell": 19,
    "Raymond Davis Jr.": 14,
    "Alexei Abrikosov": 25,
    "David Gross": 19,
    "Roy Glauber": 1,
    "John Mather": 7,
    "Albert Fert": 7,
    "Yoichiro Nambu": 18,
    "Charles Kao": 4,
    "Andre Geim": 21,
    "Saul Perlmutter": 22,
    "Serge Haroche": 11,
    "François Englert": 6,
    "Isamu Akasaki": 30,
    "Takaaki Kajita": 9,
    "Duncan Haldane": 14,
    "Rainer Weiss": 29,
    "Arthur Ashkin": 2,
    "James Peebles": 25,
    "Roger Penrose": 8,
    "Syukuro Manabe": 21,
    "Alain Aspect": 15,
}

# Nobel Prize in Literature (single winners only)
NOBEL_LITERATURE = {
    1901: "Sully Prudhomme",
    1902: "Theodor Mommsen",
    1903: "Bjørnstjerne Bjørnson",
    1905: "Henryk Sienkiewicz",
    1906: "Giosuè Carducci",
    1907: "Rudyard Kipling",
    1908: "Rudolf Christoph Eucken",
    1909: "Selma Lagerlöf",
    1910: "Paul Heyse",
    1911: "Maurice Maeterlinck",
    1912: "Gerhart Hauptmann",
    1913: "Rabindranath Tagore",
    # 1914: Not awarded
    1915: "Romain Rolland",
    1916: "Verner von Heidenstam",
    # 1918: Not awarded
    1919: "Carl Spitteler",
    1920: "Knut Hamsun",
    1921: "Anatole France",
    1922: "Jacinto Benavente",
    1923: "William Butler Yeats",
    1924: "Władysław Reymont",
    1925: "George Bernard Shaw",
    1926: "Grazia Deledda",
    1927: "Henri Bergson",
    1928: "Sigrid Undset",
    1929: "Thomas Mann",
    1930: "Sinclair Lewis",
    1931: "Erik Axel Karlfeldt",
    1932: "John Galsworthy",
    1933: "Ivan Bunin",
    1934: "Luigi Pirandello",
    # 1935: Not awarded
    1936: "Eugene O'Neill",
    1937: "Roger Martin du Gard",
    1938: "Pearl S. Buck",
    1939: "Frans Eemil Sillanpää",
    # 1940: Not awarded
    # 1941: Not awarded
    # 1942: Not awarded
    # 1943: Not awarded
    1944: "Johannes V. Jensen",
    1945: "Gabriela Mistral",
    1946: "Hermann Hesse",
    1947: "André Gide",
    1948: "T. S. Eliot",
    1949: "William Faulkner",
    1950: "Bertrand Russell",
    1951: "Pär Lagerkvist",
    1952: "François Mauriac",
    1953: "Winston Churchill",
    1954: "Ernest Hemingway",
    1955: "Halldór Laxness",
    1956: "Juan Ramón Jiménez",
    1957: "Albert Camus",
    1958: "Boris Pasternak",  # declined
    1959: "Salvatore Quasimodo",
    1960: "Saint-John Perse",
    1961: "Ivo Andrić",
    1962: "John Steinbeck",
    1963: "Giorgos Seferis",
    1964: "Jean-Paul Sartre",  # declined
    1965: "Mikhail Sholokhov",
    1967: "Miguel Ángel Asturias",
    1968: "Yasunari Kawabata",
    1969: "Samuel Beckett",
    1970: "Aleksandr Solzhenitsyn",
    1971: "Pablo Neruda",
    1972: "Heinrich Böll",
    1973: "Patrick White",
    1975: "Eugenio Montale",
    1976: "Saul Bellow",
    1977: "Vicente Aleixandre",
    1978: "Isaac Bashevis Singer",
    1979: "Odysseas Elytis",
    1980: "Czesław Miłosz",
    1981: "Elias Canetti",
    1982: "Gabriel García Márquez",
    1983: "William Golding",
    1984: "Jaroslav Seifert",
    1985: "Claude Simon",
    1986: "Wole Soyinka",
    1987: "Joseph Brodsky",
    1988: "Naguib Mahfouz",
    1989: "Camilo José Cela",
    1990: "Octavio Paz",
    1991: "Nadine Gordimer",
    1992: "Derek Walcott",
    1993: "Toni Morrison",
    1994: "Kenzaburō Ōe",
    1995: "Seamus Heaney",
    1996: "Wisława Szymborska",
    1997: "Dario Fo",
    1998: "José Saramago",
    1999: "Günter Grass",
    2000: "Gao Xingjian",
    2001: "V. S. Naipaul",
    2002: "Imre Kertész",
    2003: "J. M. Coetzee",
    2004: "Elfriede Jelinek",
    2005: "Harold Pinter",
    2006: "Orhan Pamuk",
    2007: "Doris Lessing",
    2008: "Jean-Marie Gustave Le Clézio",
    2009: "Herta Müller",
    2010: "Mario Vargas Llosa",
    2011: "Tomas Tranströmer",
    2012: "Mo Yan",
    2013: "Alice Munro",
    2014: "Patrick Modiano",
    2015: "Svetlana Alexievich",
    2016: "Bob Dylan",
    2017: "Kazuo Ishiguro",
    2018: "Olga Tokarczuk",
    2019: "Peter Handke",
    2020: "Louise Glück",
    # 2021: "Abdulrazak Gurnah",
    # 2022: "Annie Ernaux",
    # 2023: "Jon Fosse",
    # 2024: "Han Kang",
    # 2025: "László Krasznahorkai",
}

# Nobel Prize in Literature birth years (single winners only)
NOBEL_LITERATURE_BIRTH_YEAR = {
    "Sully Prudhomme": 1839,
    "Theodor Mommsen": 1817,
    "Bjørnstjerne Bjørnson": 1832,
    "Frédéric Mistral": 1830,
    "Henryk Sienkiewicz": 1846,
    "Giosuè Carducci": 1835,
    "Rudyard Kipling": 1865,
    "Rudolf Eucken": 1846,
    "Selma Lagerlöf": 1858,
    "Paul Heyse": 1830,
    "Maurice Maeterlinck": 1862,
    "Gerhart Hauptmann": 1862,
    "Rabindranath Tagore": 1861,
    "Romain Rolland": 1866,
    "Verner von Heidenstam": 1859,
    "Karl Gjellerup": 1857,
    "Erik Axel Karlfeldt": 1864,
    "Carl Spitteler": 1845,
    "Knut Hamsun": 1859,
    "Anatole France": 1844,
    "Jacinto Benavente": 1866,
    "William Butler Yeats": 1865,
    "Władysław Reymont": 1867,
    "George Bernard Shaw": 1856,
    "Grazia Deledda": 1871,
    "Henri Bergson": 1859,
    "Sigrid Undset": 1882,
    "Thomas Mann": 1875,
    "Sinclair Lewis": 1885,
    "John Galsworthy": 1867,
    "Ivan Bunin": 1870,
    "Luigi Pirandello": 1867,
    "Eugene O'Neill": 1888,
    "Roger Martin du Gard": 1881,
    "Pearl S. Buck": 1892,
    "Frans Eemil Sillanpää": 1888,
    "Johannes V. Jensen": 1873,
    "Gabriela Mistral": 1889,
    "Hermann Hesse": 1877,
    "André Gide": 1869,
    "T. S. Eliot": 1888,
    "William Faulkner": 1897,
    "Bertrand Russell": 1872,
    "Pär Lagerkvist": 1891,
    "François Mauriac": 1885,
    "Winston Churchill": 1874,
    "Ernest Hemingway": 1899,
    "Halldór Laxness": 1902,
    # "Juan Ramón Jiménez": 1881,
    "Albert Camus": 1913,
    "Boris Pasternak": 1890,
    "Salvatore Quasimodo": 1901,
    "Saint-John Perse": 1887,
    "Ivo Andrić": 1892,
    "John Steinbeck": 1902,
    "Giorgos Seferis": 1900,
    "Jean-Paul Sartre": 1905,
    "Mikhail Sholokhov": 1905,
    "Shmuel Yosef Agnon": 1888,
    "Miguel Ángel Asturias": 1899,
    "Yasunari Kawabata": 1899,
    "Samuel Beckett": 1906,
    "Aleksandr Solzhenitsyn": 1918,
    "Pablo Neruda": 1904,
    "Heinrich Böll": 1917,
    "Patrick White": 1912,
    "Eyvind Johnson": 1900,
    "Eugenio Montale": 1896,
    "Saul Bellow": 1915,
    "Vicente Aleixandre": 1898,
    # "Isaac Bashevis Singer": 1903,
    "Odysseas Elytis": 1911,
    "Czesław Miłosz": 1911,
    "Elias Canetti": 1905,
    "Gabriel García Márquez": 1927,
    "William Golding": 1911,
    "Jaroslav Seifert": 1901,
    "Claude Simon": 1913,
    "Wole Soyinka": 1934,
    "Joseph Brodsky": 1940,
    "Naguib Mahfouz": 1911,
    "Camilo José Cela": 1916,
    "Octavio Paz": 1914,
    "Nadine Gordimer": 1923,
    "Derek Walcott": 1930,
    "Toni Morrison": 1931,
    "Kenzaburō Ōe": 1935,
    "Seamus Heaney": 1939,
    "Wisława Szymborska": 1923,
    "Dario Fo": 1926,
    "José Saramago": 1922,
    "Günter Grass": 1927,
    "Gao Xingjian": 1940,
    "V. S. Naipaul": 1932,
    "Imre Kertész": 1929,
    "J. M. Coetzee": 1940,
    "Elfriede Jelinek": 1946,
    "Harold Pinter": 1930,
    "Orhan Pamuk": 1952,
    "Doris Lessing": 1919,
    "Jean-Marie Gustave Le Clézio": 1940,
    "Herta Müller": 1953,
    "Mario Vargas Llosa": 1936,
    "Tomas Tranströmer": 1931,
    "Mo Yan": 1955,
    "Alice Munro": 1931,
    "Patrick Modiano": 1945,
    "Svetlana Alexievich": 1948,
    "Bob Dylan": 1941,
    "Kazuo Ishiguro": 1954,
    "Olga Tokarczuk": 1962,
    "Peter Handke": 1942,
    "Louise Glück": 1943,
    "Abdulrazak Gurnah": 1948,
    "Annie Ernaux": 1940,
    "Jon Fosse": 1959,
}

# Nobel Prize in Literature birth day of month (single winners only)
NOBEL_LITERATURE_BIRTH_DAY = {
    "Sully Prudhomme": 16,
    "Theodor Mommsen": 30,
    "Bjørnstjerne Bjørnson": 8,
    "Frédéric Mistral": 8,
    "Henryk Sienkiewicz": 5,
    "Giosuè Carducci": 27,
    "Rudyard Kipling": 30,
    "Rudolf Eucken": 5,
    "Selma Lagerlöf": 20,
    "Paul Heyse": 15,
    "Maurice Maeterlinck": 29,
    "Gerhart Hauptmann": 15,
    "Rabindranath Tagore": 7,
    "Romain Rolland": 29,
    "Verner von Heidenstam": 6,
    "Karl Gjellerup": 2,
    "Erik Axel Karlfeldt": 20,
    "Carl Spitteler": 24,
    "Knut Hamsun": 4,
    "Anatole France": 16,
    "Jacinto Benavente": 12,
    "William Butler Yeats": 13,
    "Władysław Reymont": 7,
    "George Bernard Shaw": 26,
    "Grazia Deledda": 27,
    "Henri Bergson": 18,
    "Sigrid Undset": 20,
    "Thomas Mann": 6,
    "Sinclair Lewis": 7,
    "John Galsworthy": 14,
    "Ivan Bunin": 22,
    "Luigi Pirandello": 28,
    "Eugene O'Neill": 16,
    "Roger Martin du Gard": 23,
    "Pearl S. Buck": 26,
    "Frans Eemil Sillanpää": 16,
    "Johannes V. Jensen": 20,
    "Gabriela Mistral": 7,
    "Hermann Hesse": 2,
    "André Gide": 22,
    "T. S. Eliot": 26,
    "William Faulkner": 25,
    "Bertrand Russell": 18,
    "Pär Lagerkvist": 23,
    "François Mauriac": 11,
    "Winston Churchill": 30,
    "Ernest Hemingway": 21,
    "Halldór Laxness": 23,
    # "Juan Ramón Jiménez": 23,
    "Albert Camus": 7,
    "Boris Pasternak": 10,
    "Salvatore Quasimodo": 20,
    "Saint-John Perse": 31,
    "Ivo Andrić": 9,
    "John Steinbeck": 27,
    "Giorgos Seferis": 13,
    "Jean-Paul Sartre": 21,
    "Mikhail Sholokhov": 24,
    "Shmuel Yosef Agnon": 17,
    "Miguel Ángel Asturias": 19,
    "Yasunari Kawabata": 11,
    "Samuel Beckett": 13,
    "Aleksandr Solzhenitsyn": 11,
    "Pablo Neruda": 12,
    "Heinrich Böll": 21,
    "Patrick White": 28,
    "Eyvind Johnson": 29,
    "Eugenio Montale": 12,
    "Saul Bellow": 10,
    "Vicente Aleixandre": 26,
    # "Isaac Bashevis Singer": 11,
    "Odysseas Elytis": 2,
    "Czesław Miłosz": 30,
    "Elias Canetti": 25,
    "Gabriel García Márquez": 6,
    "William Golding": 19,
    "Jaroslav Seifert": 23,
    "Claude Simon": 10,
    "Wole Soyinka": 13,
    "Joseph Brodsky": 24,
    "Naguib Mahfouz": 11,
    "Camilo José Cela": 11,
    "Octavio Paz": 31,
    "Nadine Gordimer": 20,
    "Derek Walcott": 23,
    "Toni Morrison": 18,
    "Kenzaburō Ōe": 31,
    "Seamus Heaney": 13,
    "Wisława Szymborska": 2,
    "Dario Fo": 24,
    "José Saramago": 16,
    "Günter Grass": 16,
    "Gao Xingjian": 4,
    "V. S. Naipaul": 17,
    "Imre Kertész": 9,
    "J. M. Coetzee": 9,
    "Elfriede Jelinek": 20,
    "Harold Pinter": 10,
    "Orhan Pamuk": 7,
    "Doris Lessing": 22,
    "Jean-Marie Gustave Le Clézio": 13,
    "Herta Müller": 17,
    "Mario Vargas Llosa": 28,
    "Tomas Tranströmer": 15,
    "Mo Yan": 17,
    "Alice Munro": 10,
    "Patrick Modiano": 30,
    "Svetlana Alexievich": 31,
    "Bob Dylan": 24,
    "Kazuo Ishiguro": 8,
    "Olga Tokarczuk": 29,
    "Peter Handke": 6,
    "Louise Glück": 22,
    "Abdulrazak Gurnah": 20,
    "Annie Ernaux": 1,
    "Jon Fosse": 29,
}

# US State flowers
US_STATE_FLOWERS = {
    "Alabama": "Camellia",
    "Alaska": "Forget-me-not",
    "Arizona": "Saguaro Cactus Blossom",
    "Arkansas": "Apple Blossom",
    "California": "California Poppy",
    "Colorado": "Rocky Mountain Columbine",
    "Connecticut": "Mountain Laurel",
    "Delaware": "Peach Blossom",
    "Florida": "Orange Blossom",
    "Georgia": "Cherokee Rose",
    "Hawaii": "Hawaiian Hibiscus",
    "Idaho": "Syringa",
    "Illinois": "Violet",
    "Indiana": "Peony",
    "Iowa": "Wild Rose",
    "Kansas": "Sunflower",
    "Kentucky": "Goldenrod",
    "Louisiana": "Magnolia",
    "Maine": "White Pine Cone and Tassel",
    "Maryland": "Black-Eyed Susan",
    "Massachusetts": "Mayflower",
    "Michigan": "Apple Blossom",
    "Minnesota": "Pink and White Lady's Slipper",
    "Mississippi": "Magnolia",
    "Missouri": "White Hawthorn Blossom",
    "Montana": "Bitterroot",
    "Nebraska": "Goldenrod",
    "Nevada": "Sagebrush",
    "New Hampshire": "Purple Lilac",
    "New Jersey": "Common Meadow Violet",
    "New Mexico": "Yucca Flower",
    "New York": "Rose",
    "North Carolina": "Dogwood",
    "North Dakota": "Wild Prairie Rose",
    "Ohio": "Scarlet Carnation",
    "Oklahoma": "Oklahoma Rose",
    "Oregon": "Oregon Grape",
    "Pennsylvania": "Mountain Laurel",
    "Rhode Island": "Violet",
    "South Carolina": "Yellow Jessamine",
    "South Dakota": "Pasque Flower",
    "Tennessee": "Iris",
    "Texas": "Bluebonnet",
    "Utah": "Sego Lily",
    "Vermont": "Red Clover",
    "Virginia": "American Dogwood",
    "Washington": "Coast Rhododendron",
    "West Virginia": "Rhododendron",
    "Wisconsin": "Wood Violet",
    "Wyoming": "Indian Paintbrush",
    "District of Columbia": "American Beauty Rose",
}

# US House of Representatives seats by state (post-2020 census apportionment)
US_STATE_HOUSE_SEATS = {
    "Alabama": 7,
    "Alaska": 1,
    "Arizona": 9,
    "Arkansas": 4,
    "California": 52,
    "Colorado": 8,
    "Connecticut": 5,
    "Delaware": 1,
    "Florida": 28,
    "Georgia": 14,
    "Hawaii": 2,
    "Idaho": 2,
    "Illinois": 17,
    "Indiana": 9,
    "Iowa": 4,
    "Kansas": 4,
    "Kentucky": 6,
    "Louisiana": 6,
    "Maine": 2,
    "Maryland": 8,
    "Massachusetts": 9,
    "Michigan": 13,
    "Minnesota": 8,
    "Mississippi": 4,
    "Missouri": 8,
    "Montana": 2,
    "Nebraska": 3,
    "Nevada": 4,
    "New Hampshire": 2,
    "New Jersey": 12,
    "New Mexico": 3,
    "New York": 26,
    "North Carolina": 14,
    "North Dakota": 1,
    "Ohio": 15,
    "Oklahoma": 5,
    "Oregon": 6,
    "Pennsylvania": 17,
    "Rhode Island": 2,
    "South Carolina": 7,
    "South Dakota": 1,
    "Tennessee": 9,
    "Texas": 38,
    "Utah": 4,
    "Vermont": 1,
    "Virginia": 11,
    "Washington": 10,
    "West Virginia": 2,
    "Wisconsin": 8,
    "Wyoming": 1,
}

# State legislature lower chamber seats by state
US_STATE_LEGISLATURE_HOUSE_SEATS = {
    "Alabama": 105,
    "Alaska": 40,
    "Arizona": 60,
    "Arkansas": 100,
    "California": 80,
    "Colorado": 65,
    "Connecticut": 151,
    "Delaware": 41,
    "Florida": 120,
    "Georgia": 180,
    "Hawaii": 51,
    "Idaho": 70,
    "Illinois": 118,
    "Indiana": 100,
    "Iowa": 100,
    "Kansas": 125,
    "Kentucky": 100,
    "Louisiana": 105,
    "Maine": 151,
    "Maryland": 141,
    "Massachusetts": 160,
    "Michigan": 110,
    "Minnesota": 134,
    "Mississippi": 122,
    "Missouri": 163,
    "Montana": 100,
    "Nevada": 42,
    "New Hampshire": 400,
    "New Jersey": 80,
    "New Mexico": 70,
    "New York": 150,
    "North Carolina": 120,
    "North Dakota": 94,
    "Ohio": 99,
    "Oklahoma": 101,
    "Oregon": 60,
    "Pennsylvania": 203,
    "Rhode Island": 75,
    "South Carolina": 124,
    "South Dakota": 70,
    "Tennessee": 99,
    "Texas": 150,
    "Utah": 75,
    "Vermont": 150,
    "Virginia": 100,
    "Washington": 98,
    "West Virginia": 100,
    "Wisconsin": 99,
    "Wyoming": 60,
}

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
