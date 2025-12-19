#!/usr/bin/env python3
"""
Generate multi-hop reasoning dataset with unrelated fact chains.

The key property is that facts in each chain are from unrelated domains,
so the model must actually dereference each step sequentially.
"""

from collections import defaultdict
import json
import random
import argparse
from typing import Counter, Dict, List, Any
from pathlib import Path
from abc import ABC, abstractmethod

from generate_dataset_constants import (
    AGE_FACTS,
    NUM_TO_ELEMENT,
    OSCAR_BEST_ACTOR_BIRTH_DAY,
    OSCAR_BEST_ACTOR_BY_ORDER,
    OSCAR_BEST_ACTRESS,
    OSCAR_BEST_ACTRESS_BIRTH_YEAR,
    OSCAR_BEST_ACTRESS_BIRTH_DAY,
    OSCAR_BEST_ACTRESS_BY_ORDER,
    OSCAR_BEST_SUPPORTING_ACTOR,
    OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR,
    OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY,
    OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER,
    OSCAR_BEST_SUPPORTING_ACTRESS,
    OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR,
    OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY,
    OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER,
    NOBEL_PEACE,
    NOBEL_PEACE_BIRTH_YEAR,
    NOBEL_PEACE_BIRTH_DAY,
    NOBEL_CHEMISTRY,
    NOBEL_CHEMISTRY_BIRTH_YEAR,
    NOBEL_CHEMISTRY_BIRTH_DAY,
    NOBEL_PHYSICS,
    NOBEL_PHYSICS_BIRTH_YEAR,
    NOBEL_PHYSICS_BIRTH_DAY,
    NOBEL_LITERATURE,
    NOBEL_LITERATURE_BIRTH_YEAR,
    NOBEL_LITERATURE_BIRTH_DAY,
    STATIC_FACTS,
    US_STATE_BY_ORDER,
    US_STATE_FLOWERS,
    US_STATE_MOTTOS,
    US_HOUSE_SEATS_FACTS,
    STATE_LEGISLATURE_HOUSE_SEATS_FACTS,
    MISS_AMERICA,
    OSCAR_BEST_ACTOR,
    OSCAR_BEST_ACTOR_BIRTH_YEAR,
    ELEMENTS_FILTERED,
    US_STATE_TO_COUNTIES,
)


# =============================================================================
# OSCAR AWARD TYPE MAPPINGS
# =============================================================================

# Mappings for parametric Oscar consumer classes
OSCAR_AWARD_CONFIGS = {
    "best_actor": {
        "year_dict": OSCAR_BEST_ACTOR,
        "birth_year_dict": OSCAR_BEST_ACTOR_BIRTH_YEAR,
        "birth_day_dict": OSCAR_BEST_ACTOR_BIRTH_DAY,
        "by_order_dict": OSCAR_BEST_ACTOR_BY_ORDER,
        "display_name": "Best Actor",
        "short_name": "best actor",
    },
    "best_actress": {
        "year_dict": OSCAR_BEST_ACTRESS,
        "birth_year_dict": OSCAR_BEST_ACTRESS_BIRTH_YEAR,
        "birth_day_dict": OSCAR_BEST_ACTRESS_BIRTH_DAY,
        "by_order_dict": OSCAR_BEST_ACTRESS_BY_ORDER,
        "display_name": "Best Actress",
        "short_name": "best actress",
    },
    "best_supporting_actor": {
        "year_dict": OSCAR_BEST_SUPPORTING_ACTOR,
        "birth_year_dict": OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_YEAR,
        "birth_day_dict": OSCAR_BEST_SUPPORTING_ACTOR_BIRTH_DAY,
        "by_order_dict": OSCAR_BEST_SUPPORTING_ACTOR_BY_ORDER,
        "display_name": "Best Supporting Actor",
        "short_name": "best supporting actor",
    },
    "best_supporting_actress": {
        "year_dict": OSCAR_BEST_SUPPORTING_ACTRESS,
        "birth_year_dict": OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_YEAR,
        "birth_day_dict": OSCAR_BEST_SUPPORTING_ACTRESS_BIRTH_DAY,
        "by_order_dict": OSCAR_BEST_SUPPORTING_ACTRESS_BY_ORDER,
        "display_name": "Best Supporting Actress",
        "short_name": "best supporting actress",
    },
}

# =============================================================================
# NOBEL PRIZE TYPE MAPPINGS
# =============================================================================

# Mappings for parametric Nobel Prize consumer classes
NOBEL_AWARD_CONFIGS = {
    "peace": {
        "year_dict": NOBEL_PEACE,
        "birth_year_dict": NOBEL_PEACE_BIRTH_YEAR,
        "birth_day_dict": NOBEL_PEACE_BIRTH_DAY,
        "display_name": "Nobel Peace Prize",
        "short_name": "Nobel Peace Prize",
    },
    "chemistry": {
        "year_dict": NOBEL_CHEMISTRY,
        "birth_year_dict": NOBEL_CHEMISTRY_BIRTH_YEAR,
        "birth_day_dict": NOBEL_CHEMISTRY_BIRTH_DAY,
        "display_name": "Nobel Prize in Chemistry",
        "short_name": "Nobel Prize in Chemistry",
    },
    "physics": {
        "year_dict": NOBEL_PHYSICS,
        "birth_year_dict": NOBEL_PHYSICS_BIRTH_YEAR,
        "birth_day_dict": NOBEL_PHYSICS_BIRTH_DAY,
        "display_name": "Nobel Prize in Physics",
        "short_name": "Nobel Prize in Physics",
    },
    "literature": {
        "year_dict": NOBEL_LITERATURE,
        "birth_year_dict": NOBEL_LITERATURE_BIRTH_YEAR,
        "birth_day_dict": NOBEL_LITERATURE_BIRTH_DAY,
        "display_name": "Nobel Prize in Literature",
        "short_name": "Nobel Prize in Literature",
    },
}

# =============================================================================
# 2-HOP PROBLEM GENERATOR TEMPLATES
# =============================================================================


# =============================================================================
# NUMBER CONSUMER CLASSES
# =============================================================================


class NumberConsumer(ABC):
    """Base class for number consumers that transform a number into an answer."""

    def __init__(self):
        self.id: str = ""

    @abstractmethod
    def is_valid(self, num: int, num_gen_id: str) -> bool:
        """Check if this number is valid for this consumer."""
        pass

    @abstractmethod
    def get_properties(self, num: int, num_expr: str) -> Dict:
        """
        Get properties for building the problem.

        Args:
            num: The number value
            num_expr: The formatted expression for the number (e.g., "atomic number of Gold")

        Returns:
            {
                "answer": final answer value,
                "question": formatted question string,
                "rest_of_chain": [{"fact": ..., "value": ...}, ...]  # chain items after the first
            }
        """
        pass


CUT_OFF_EARLY_FIXED_NUM_STATES = 5


class StateOrderConsumer(NumberConsumer):
    def __init__(self):
        self.id = "state_order"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num_gen_id == "fixed_num" and num <= CUT_OFF_EARLY_FIXED_NUM_STATES:
            return False
        if "state_order" in num_gen_id:
            return False
        return num in US_STATE_BY_ORDER

    def get_properties(self, num: int, num_expr: str) -> Dict:
        answer = US_STATE_BY_ORDER[num]
        question = f"What US state was number {num_expr} to join the union?"
        rest_of_chain = [{"fact": f"State that joined the union {num}th", "value": answer, "mapping_id": "state_order_to_state"}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class ElementConsumer(NumberConsumer):
    def __init__(self):
        self.id = "element"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        # Don't use element generator with element consumer (circular)
        if num_gen_id == "element":
            return False
        if num_gen_id == "fixed_num" and num <= 10:
            return False
        return num in NUM_TO_ELEMENT

    def get_properties(self, num: int, num_expr: str) -> Dict:
        answer = NUM_TO_ELEMENT[num]
        question = f"What element has atomic number {num_expr}?"
        rest_of_chain = [{"fact": f"Element with atomic number {num}", "value": answer, "mapping_id": "atomic_number_to_element"}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class StateOrderFlowerConsumer(NumberConsumer):
    def __init__(self):
        self.id = "state_order_state_flower"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num_gen_id == "fixed_num" and num <= CUT_OFF_EARLY_FIXED_NUM_STATES:
            return False
        if "state_order" in num_gen_id:
            return False
        return num in US_STATE_BY_ORDER

    def get_properties(self, num: int, num_expr: str) -> Dict:
        state = US_STATE_BY_ORDER[num]
        answer = US_STATE_FLOWERS[state]
        question = f"What is the state flower of the US State that was number {num_expr} to join the union?"
        rest_of_chain = [
            {"fact": f"State that joined the union {num}th", "value": state, "mapping_id": "state_order_to_state"},
            {"fact": f"State flower of {state}", "value": answer, "mapping_id": "state_to_flower"},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


# class StateOrderJoinDayConsumer(NumberConsumer):
#     def __init__(self):
#         self.id = "state_order_join_day"

#     def is_valid(self, num: int, num_gen_id: str) -> bool:
#         if num_gen_id == "fixed_num" and num <= CUT_OFF_EARLY_FIXED_NUM_STATES:
#             return False
#         if "state_order" in num_gen_id:
#             return False
#         return num in US_STATE_BY_ORDER

#     def get_properties(self, num: int, num_expr: str) -> Dict:
#         state = US_STATE_BY_ORDER[num]
#         answer = US_STATE_JOINED_DAY[state]
#         question = f"On what day of the month did the US State that was number {num_expr} to join the union join?"
#         rest_of_chain = [
#             {"fact": f"State that joined the union {num}th", "value": state},
#             {"fact": f"Day {state} joined the union", "value": answer},
#         ]
#         return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class StateOrderNumCountiesConsumer(NumberConsumer):
    def __init__(self):
        self.id = "state_order_num_counties"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num_gen_id == "fixed_num" and num <= CUT_OFF_EARLY_FIXED_NUM_STATES:
            return False
        if "state_order" in num_gen_id:
            return False
        return num in US_STATE_BY_ORDER and US_STATE_BY_ORDER[num] in US_STATE_TO_COUNTIES

    def get_properties(self, num: int, num_expr: str) -> Dict:
        state = US_STATE_BY_ORDER[num]
        answer = US_STATE_TO_COUNTIES[state]
        question = f"How many county-equivalents are in the US State that was number {num_expr} to join the union?"
        rest_of_chain = [
            {"fact": f"State that joined the union {num}th", "value": state, "mapping_id": "state_order_to_state"},
            {"fact": f"County-equivalents in {state}", "value": answer, "mapping_id": "state_to_counties"},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class MissAmericaConsumer(NumberConsumer):
    def __init__(self, start_year: int):
        self.id = f"miss_america_{start_year}"
        self.start_year = start_year

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        return num < 100 and self.start_year + num in MISS_AMERICA

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        answer = MISS_AMERICA[year]
        question = f"Who was Miss America for the ({self.start_year} + {num_expr}) competition?"
        rest_of_chain = [{"fact": f"Miss America for {year}", "value": answer, "mapping_id": "year_to_miss_america"}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class OscarConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_{start_year}"
        self.start_year = start_year
        self.mapping_id = f"year_to_oscar_{award_type}"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if "oscar" in num_gen_id:
            return False
        return num < 100 and self.start_year + num in self.config["year_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        answer = self.config["year_dict"][year]
        display_name = self.config["display_name"]
        question = (
            f"Who won the Academy Award for {display_name} for a film released in ({self.start_year} + {num_expr})?"
        )
        rest_of_chain = [{"fact": f"Oscar {display_name} in {year}", "value": answer, "mapping_id": self.mapping_id}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class StateOrderMottoConsumer(NumberConsumer):
    def __init__(self):
        self.id = "state_order_state_motto"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num_gen_id == "fixed_num" and num <= CUT_OFF_EARLY_FIXED_NUM_STATES:
            return False
        if "state_order" in num_gen_id:
            return False
        return num in US_STATE_BY_ORDER

    def get_properties(self, num: int, num_expr: str) -> Dict:
        state = US_STATE_BY_ORDER[num]
        answer = US_STATE_MOTTOS[state]
        question = f"What is the state motto of the US State that was number {num_expr} to join the union?"
        rest_of_chain = [
            {"fact": f"State that joined the union {num}th", "value": state, "mapping_id": "state_order_to_state"},
            {"fact": f"State motto of {state}", "value": answer, "mapping_id": "state_to_motto"},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


def get_num_expr_start_year(start_year: int, num_expr: str) -> str:
    try:
        int_num_expr = int(num_expr)
        full_num_expr = str(start_year + int_num_expr)
    except ValueError:
        full_num_expr = f"({start_year} + {num_expr})"
    return full_num_expr


class OscarBirthYearConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_{start_year}_birth_year"
        self.start_year = start_year
        self.year_mapping_id = f"year_to_oscar_{award_type}"
        self.birth_year_mapping_id = f"oscar_{award_type}_to_birth_year"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num >= 100:
            return False
        if "oscar" in num_gen_id:
            return False
        year = self.start_year + num
        return year in self.config["year_dict"] and self.config["year_dict"][year] in self.config["birth_year_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        winner = self.config["year_dict"][year]
        answer = self.config["birth_year_dict"][winner]
        display_name = self.config["display_name"]
        question = f"In what year was the Oscar {display_name} winner for a film released in {get_num_expr_start_year(self.start_year, num_expr)} born?"
        rest_of_chain = [
            {"fact": f"Oscar {display_name} in {year}", "value": winner, "mapping_id": self.year_mapping_id},
            {"fact": f"Birth year of {winner}", "value": answer, "mapping_id": self.birth_year_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class OscarBirthDayConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_{start_year}_birth_day"
        self.start_year = start_year
        self.year_mapping_id = f"year_to_oscar_{award_type}"
        self.birth_day_mapping_id = f"oscar_{award_type}_to_birth_day"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num >= 100:
            return False
        if "oscar" in num_gen_id:
            return False
        year = self.start_year + num
        return year in self.config["year_dict"] and self.config["year_dict"][year] in self.config["birth_day_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        winner = self.config["year_dict"][year]
        answer = self.config["birth_day_dict"][winner]
        display_name = self.config["display_name"]
        question = f"On what day of the month was the Oscar {display_name} winner for a film released in {get_num_expr_start_year(self.start_year, num_expr)} born?"
        rest_of_chain = [
            {"fact": f"Oscar {display_name} in {year}", "value": winner, "mapping_id": self.year_mapping_id},
            {"fact": f"Birth day of {winner}", "value": answer, "mapping_id": self.birth_day_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class OscarOrderConsumer(NumberConsumer):
    def __init__(self, award_type: str):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_order"
        self.order_mapping_id = f"order_to_oscar_{award_type}"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if "oscar" in num_gen_id:
            return False
        return num in self.config["by_order_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        answer = self.config["by_order_dict"][num]
        ordinal = f"{num}{['st', 'nd', 'rd'][num-1] if num <= 3 else 'th'}"
        short_name = self.config["short_name"]
        display_name = self.config["display_name"]
        question = f"Who won {short_name} at the {num_expr}th Academy Awards?"
        rest_of_chain = [{"fact": f"{ordinal} Oscar {display_name} winner", "value": answer, "mapping_id": self.order_mapping_id}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class OscarOrderBirthYearConsumer(NumberConsumer):
    def __init__(self, award_type: str):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_order_birth_year"
        self.order_mapping_id = f"order_to_oscar_{award_type}"
        self.birth_year_mapping_id = f"oscar_{award_type}_to_birth_year"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if "oscar" in num_gen_id:
            return False
        return (
            num in self.config["by_order_dict"] and self.config["by_order_dict"][num] in self.config["birth_year_dict"]
        )

    def get_properties(self, num: int, num_expr: str) -> Dict:
        winner = self.config["by_order_dict"][num]
        answer = self.config["birth_year_dict"][winner]
        ordinal = f"{num}{['st', 'nd', 'rd'][num-1] if num <= 3 else 'th'}"
        short_name = self.config["short_name"]
        display_name = self.config["display_name"]
        question = f"In what year was the {short_name} winner at the {num_expr}th Academy Awards born?"
        rest_of_chain = [
            {"fact": f"{ordinal} Oscar {display_name} winner", "value": winner, "mapping_id": self.order_mapping_id},
            {"fact": f"Birth year of {winner}", "value": answer, "mapping_id": self.birth_year_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class OscarOrderBirthDayConsumer(NumberConsumer):
    def __init__(self, award_type: str):
        self.award_type = award_type
        self.config = OSCAR_AWARD_CONFIGS[award_type]
        self.id = f"oscar_{award_type}_order_birth_day"
        self.order_mapping_id = f"order_to_oscar_{award_type}"
        self.birth_day_mapping_id = f"oscar_{award_type}_to_birth_day"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if "oscar" in num_gen_id:
            return False
        return (
            num in self.config["by_order_dict"] and self.config["by_order_dict"][num] in self.config["birth_day_dict"]
        )

    def get_properties(self, num: int, num_expr: str) -> Dict:
        winner = self.config["by_order_dict"][num]
        answer = self.config["birth_day_dict"][winner]
        ordinal = f"{num}{['st', 'nd', 'rd'][num-1] if num <= 3 else 'th'}"
        short_name = self.config["short_name"]
        display_name = self.config["display_name"]
        question = f"On what day of the month was the {short_name} winner at the {num_expr}th Academy Awards born?"
        rest_of_chain = [
            {"fact": f"{ordinal} Oscar {display_name} winner", "value": winner, "mapping_id": self.order_mapping_id},
            {"fact": f"Birth day of {winner}", "value": answer, "mapping_id": self.birth_day_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class NobelConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = NOBEL_AWARD_CONFIGS[award_type]
        self.id = f"nobel_{award_type}_{start_year}"
        self.start_year = start_year
        self.year_mapping_id = f"year_to_nobel_{award_type}"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if "nobel" in num_gen_id:
            return False
        return num < 100 and self.start_year + num in self.config["year_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        answer = self.config["year_dict"][year]
        display_name = self.config["display_name"]
        question = f"Who won the {display_name} in ({self.start_year} + {num_expr})?"
        rest_of_chain = [{"fact": f"{display_name} in {year}", "value": answer, "mapping_id": self.year_mapping_id}]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class NobelBirthYearConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = NOBEL_AWARD_CONFIGS[award_type]
        self.id = f"nobel_{award_type}_{start_year}_birth_year"
        self.start_year = start_year
        self.year_mapping_id = f"year_to_nobel_{award_type}"
        self.birth_year_mapping_id = f"nobel_{award_type}_to_birth_year"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num >= 100:
            return False
        if "nobel" in num_gen_id:
            return False
        year = self.start_year + num
        return year in self.config["year_dict"] and self.config["year_dict"][year] in self.config["birth_year_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        winner = self.config["year_dict"][year]
        answer = self.config["birth_year_dict"][winner]
        display_name = self.config["display_name"]
        question = (
            f"In what year was the {display_name} winner in {get_num_expr_start_year(self.start_year, num_expr)} born?"
        )
        rest_of_chain = [
            {"fact": f"{display_name} in {year}", "value": winner, "mapping_id": self.year_mapping_id},
            {"fact": f"Birth year of {winner}", "value": answer, "mapping_id": self.birth_year_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


class NobelBirthDayConsumer(NumberConsumer):
    def __init__(self, award_type: str, start_year: int):
        self.award_type = award_type
        self.config = NOBEL_AWARD_CONFIGS[award_type]
        self.id = f"nobel_{award_type}_{start_year}_birth_day"
        self.start_year = start_year
        self.year_mapping_id = f"year_to_nobel_{award_type}"
        self.birth_day_mapping_id = f"nobel_{award_type}_to_birth_day"

    def is_valid(self, num: int, num_gen_id: str) -> bool:
        if num >= 100:
            return False
        if "nobel" in num_gen_id:
            return False
        year = self.start_year + num
        return year in self.config["year_dict"] and self.config["year_dict"][year] in self.config["birth_day_dict"]

    def get_properties(self, num: int, num_expr: str) -> Dict:
        year = self.start_year + num
        winner = self.config["year_dict"][year]
        answer = self.config["birth_day_dict"][winner]
        display_name = self.config["display_name"]
        question = f"On what day of the month was the {display_name} winner in {get_num_expr_start_year(self.start_year, num_expr)} born?"
        rest_of_chain = [
            {"fact": f"{display_name} in {year}", "value": winner, "mapping_id": self.year_mapping_id},
            {"fact": f"Birth day of {winner}", "value": answer, "mapping_id": self.birth_day_mapping_id},
        ]
        return {"answer": answer, "question": question, "rest_of_chain": rest_of_chain}


# Number generators: these produce a number from some source
# Each item is: (produced_number, question, start_of_chain)
# Chain items now include: {"fact": ..., "value": ..., "mapping_id": ...}
NUMBER_GENERATORS = [
    {
        "id": "element",
        "items": [
            (num, f"(atomic number of {name})", [{"fact": f"Atomic number of {name}", "value": num, "mapping_id": "element_to_atomic_number"}])
            for name, num in ELEMENTS_FILTERED.items()
        ],
    },
    {
        "id": "agefact",
        "items": [
            (
                fact["answer"],
                f"({fact['question'].replace('?', '')})",
                [{"fact": fact["question"], "value": fact["answer"], "mapping_id": "age_facts"}],
            )
            for fact in AGE_FACTS
        ],
    },
    {
        "id": "staticfact",
        "items": [
            (
                fact["answer"],
                f"({fact['question'].replace('?', '')})",
                [{"fact": fact["question"], "value": fact["answer"], "mapping_id": "static_facts"}],
            )
            for fact in STATIC_FACTS
        ],
    },
    {
        "id": "us_house_seats",
        "items": [
            (
                fact["answer"],
                f"({fact['question'].replace('?', '')})",
                [{"fact": fact["question"], "value": fact["answer"], "mapping_id": "us_house_seats"}],
            )
            for fact in US_HOUSE_SEATS_FACTS
        ],
    },
    {
        "id": "state_leg_house_seats",
        "items": [
            (
                fact["answer"],
                f"({fact['question'].replace('?', '')})",
                [{"fact": fact["question"], "value": fact["answer"], "mapping_id": "state_legislature_house_seats"}],
            )
            for fact in STATE_LEGISLATURE_HOUSE_SEATS_FACTS
        ],
    },
    {
        "id": "fixed_num",
        "items": [(num, str(num), []) for num in range(1, 1000)],
    },
]

# All number consumers (will be filtered by is_valid to determine which generators they work with)
ALL_CONSUMERS = [
    StateOrderConsumer(),
    ElementConsumer(),
    MissAmericaConsumer(1900),
    StateOrderMottoConsumer(),
    StateOrderFlowerConsumer(),
    # StateOrderJoinDayConsumer(), # too easy I think
    StateOrderNumCountiesConsumer(),
    # Oscar consumers for all award types
    OscarConsumer("best_actor", 1900),
    OscarConsumer("best_actress", 1900),
    OscarConsumer("best_supporting_actor", 1900),
    OscarConsumer("best_supporting_actress", 1900),
    OscarOrderConsumer("best_actor"),
    OscarOrderConsumer("best_actress"),
    OscarOrderConsumer("best_supporting_actor"),
    OscarOrderConsumer("best_supporting_actress"),
    OscarBirthYearConsumer("best_actor", 1900),
    OscarBirthYearConsumer("best_actress", 1900),
    OscarBirthYearConsumer("best_supporting_actor", 1900),
    OscarBirthYearConsumer("best_supporting_actress", 1900),
    OscarBirthDayConsumer("best_actor", 1900),
    OscarBirthDayConsumer("best_actress", 1900),
    OscarBirthDayConsumer("best_supporting_actor", 1900),
    OscarBirthDayConsumer("best_supporting_actress", 1900),
    OscarOrderBirthYearConsumer("best_actor"),
    OscarOrderBirthYearConsumer("best_actress"),
    OscarOrderBirthYearConsumer("best_supporting_actor"),
    OscarOrderBirthYearConsumer("best_supporting_actress"),
    OscarOrderBirthDayConsumer("best_actor"),
    OscarOrderBirthDayConsumer("best_actress"),
    OscarOrderBirthDayConsumer("best_supporting_actor"),
    OscarOrderBirthDayConsumer("best_supporting_actress"),
    # Nobel Prize consumers for all award types (no order-based consumers)
    NobelConsumer("peace", 1900),
    NobelConsumer("chemistry", 1900),
    NobelConsumer("physics", 1900),
    NobelConsumer("literature", 1900),
    NobelBirthYearConsumer("peace", 1900),
    NobelBirthYearConsumer("chemistry", 1900),
    NobelBirthYearConsumer("physics", 1900),
    NobelBirthYearConsumer("literature", 1900),
    NobelBirthDayConsumer("peace", 1900),
    NobelBirthDayConsumer("chemistry", 1900),
    NobelBirthDayConsumer("physics", 1900),
    NobelBirthDayConsumer("literature", 1900),
]


def gen_hop_generic(generator, consumer: NumberConsumer, seed: int, num: int | None = None) -> List[Dict]:
    """Generic problem generator combining a number generator and consumer."""
    random.seed(seed)
    problems = []

    # Get all items from generator and filter by consumer's valid range
    all_items = generator["items"]
    valid = [
        (number, num_expr, start_of_chain)
        for number, num_expr, start_of_chain in all_items
        if consumer.is_valid(number, generator["id"])
    ]
    random.shuffle(valid)

    # only use non-repeated nums (do this after shuffle to randomize)
    num_used = set()
    new_valid = []
    for number, num_expr, start_of_chain in valid:
        if number not in num_used:
            num_used.add(number)
            new_valid.append((number, num_expr, start_of_chain))

    valid = new_valid

    if num is not None:
        valid = valid[:num]

    for number, num_expr, start_of_chain in valid:
        # Get properties from consumer
        props = consumer.get_properties(number, num_expr)

        # Build full chain: start_of_chain from generator + rest from consumer
        chain = start_of_chain + props["rest_of_chain"]

        hops = len(chain)

        problems.append(
            {
                "type": f"{hops}hop_{generator['id']}_{consumer.id}",
                "question": props["question"],
                "answer": props["answer"],
                "hops": hops,
                "chain": chain,
            }
        )

    return problems


# =============================================================================
# MAIN
# =============================================================================


def generate_all_problems(only_salient_facts: bool = False):
    """Generate all problems."""
    all_problems = []

    number_generators_use = NUMBER_GENERATORS
    consumers_use = ALL_CONSUMERS

    if only_salient_facts:
        # remove state_leg_house_seats
        number_generators_use = [
            gen for gen in NUMBER_GENERATORS if gen["id"] != "state_leg_house_seats"
        ]
        consumers_use = [
            StateOrderConsumer(),
            ElementConsumer(),
        ]



    seed = 128
    for gen in number_generators_use:
        for cons in consumers_use:
            problems = gen_hop_generic(gen, cons, seed=seed, num=None)
            all_problems.extend(problems)
            seed += 1

    new_numeric_generators = defaultdict(list)
    for p in all_problems:

        assert int(p["type"][0]) in [1, 2, 3, 4]
        clean_type_id = p["type"][1:]
        assert clean_type_id.startswith("hop_")
        clean_type_id = clean_type_id.removeprefix("hop_")
        if p["type"].endswith("birth_day") or p["type"].endswith("join_day") or p["type"].endswith("num_counties"):
            assert isinstance(p["answer"], int)
            # assert 0 < p["answer"] < 100
            new_numeric_generators[clean_type_id].append(
                (
                    p["answer"],
                    f"({p['question'].replace('?', '')})",
                    p["chain"],
                )
            )

    new_numeric_generators_fin = [{"id": k, "items": v} for k, v in new_numeric_generators.items()]

    for gen in new_numeric_generators_fin:
        for cons in consumers_use:
            problems = gen_hop_generic(gen, cons, seed=seed, num=None)
            all_problems.extend(problems)
            seed += 1

    # Separate by hop count (filtering out elements with 1 hop)
    all_1hop = [p for p in all_problems if p["hops"] == 1]
    all_2hop = [p for p in all_problems if p["hops"] == 2]
    all_3hop = [p for p in all_problems if p["hops"] == 3]
    all_4hop = [p for p in all_problems if p["hops"] == 4]

    return all_1hop, all_2hop, all_3hop, all_4hop


def generate_single_hop_questions_auto():
    all1hop, _, _, _ = generate_all_problems()
    out = defaultdict(list)
    for p in all1hop:
        out[p["type"]].append((p["question"], p["answer"]))
    return out


def save_dataset(problems: List[Dict], filepath: str):
    """Save problems to JSONL file."""
    import os

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for problem in problems:
            f.write(json.dumps(problem, ensure_ascii=False) + "\n")
    print(f"Saved {len(problems)} problems to {filepath}")


def main():
    """Generate all datasets."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate multi-hop reasoning dataset")
    parser.add_argument(
        "--num-2hop",
        type=int,
        default=300,
        help="Number of 2-hop problems to include (default: 300)",
    )
    parser.add_argument(
        "--num-3hop",
        type=int,
        default=600,
        help="Number of 3-hop problems to include (default: 600)",
    )
    parser.add_argument(
        "--num-4hop",
        type=int,
        default=600,
        help="Number of 4-hop problems to include (default: 600)",
    )
    parser.add_argument(
        "--only-salient-facts",
        action="store_true",
        help="Only use salient facts for generation (fewer problems)",

    )
    args = parser.parse_args()

    # Generate all problems
    _, all_2hop, all_3hop, all_4hop = generate_all_problems(only_salient_facts=args.only_salient_facts)

    print(f"Generated {len(all_2hop)} 2-hop problems")
    print(f"Generated {len(all_3hop)} 3-hop problems")
    print(f"Generated {len(all_4hop)} 4-hop problems")

    # Shuffle within each hop level
    random.seed(100)
    random.shuffle(all_2hop)
    random.shuffle(all_3hop)
    random.shuffle(all_4hop)

    # Downsample problems
    random.seed(101)  # Different seed for downsampling

    def downsample(problems, oscar_keep_rate: float, nobel_keep_rate: float):
        """Keep only a fraction of problems."""
        result = []
        for p in problems:
            if "oscar" in p["type"]:
                if random.random() > oscar_keep_rate:
                    continue
            if "nobel" in p["type"]:
                if random.random() > nobel_keep_rate:
                    continue
            result.append(p)
        return result

    all_2hop = downsample(all_2hop, oscar_keep_rate=0.2, nobel_keep_rate=0.3)
    all_3hop = downsample(all_3hop, oscar_keep_rate=0.13, nobel_keep_rate=0.25)
    all_4hop = downsample(all_4hop, oscar_keep_rate=0.1, nobel_keep_rate=0.13)

    print(f"After downsampling problems:")
    print(f"  {len(all_2hop)} 2-hop problems")
    print(f"  {len(all_3hop)} 3-hop problems")
    print(f"  {len(all_4hop)} 4-hop problems")

    # Cut to specified counts after shuffle and downsampling
    if args.num_2hop is not None:
        all_2hop = all_2hop[: args.num_2hop]
        print(f"Cut 2-hop to {len(all_2hop)} problems")
    if args.num_3hop is not None:
        all_3hop = all_3hop[: args.num_3hop]
        print(f"Cut 3-hop to {len(all_3hop)} problems")
    if args.num_4hop is not None:
        all_4hop = all_4hop[: args.num_4hop]
        print(f"Cut 4-hop to {len(all_4hop)} problems")

    # Print Oscar problem fractions
    def print_oscar_fraction(problems, label):
        """Print fraction of problems that are Oscar problems."""
        total = len(problems)
        oscar_count = sum(1 for p in problems if "oscar" in p["type"])
        nobel_count = sum(1 for p in problems if "nobel" in p["type"])
        fraction_oscar = oscar_count / total if total > 0 else 0
        fraction_nobel = nobel_count / total if total > 0 else 0
        print(
            f"{label}: {oscar_count}/{total} = {fraction_oscar:.1%} are Oscar problems and {nobel_count}/{total} = {fraction_nobel:.1%} are Nobel problems"
        )

    print_oscar_fraction(all_2hop, "2-HOP")
    print_oscar_fraction(all_3hop, "3-HOP")
    print_oscar_fraction(all_4hop, "4-HOP")
    all_problems_for_fraction = all_2hop + all_3hop + all_4hop
    print_oscar_fraction(all_problems_for_fraction, "ALL")

    # Print counts by type
    def print_type_counts(problems, label):
        """Print counts of each problem type."""
        type_counts = Counter([p["type"] for p in problems])
        print(f"\n=== {label} TYPE COUNTS ===")
        for ptype, count in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {ptype}: {count}")

    # print_type_counts(all_2hop, "2-HOP")
    # print_type_counts(all_3hop, "3-HOP")
    # print_type_counts(all_4hop, "4-HOP")

    # # Combined type counts
    # all_problems_for_counts = all_2hop + all_3hop + all_4hop
    # print_type_counts(all_problems_for_counts, "ALL")

    # Save individual datasets
    prefix = "data/salient_" if args.only_salient_facts else "data/"
    save_dataset(all_2hop, f"{prefix}problems_2hop.jsonl")
    save_dataset(all_3hop, f"{prefix}problems_3hop.jsonl")
    save_dataset(all_4hop, f"{prefix}problems_4hop.jsonl")

    # Save combined dataset
    all_problems = all_2hop + all_3hop + all_4hop
    save_dataset(all_problems, f"{prefix}problems_all.jsonl")

    # Print examples
    print("\n=== EXAMPLE 2-HOP PROBLEMS ===")
    for p in all_2hop[:10]:
        print(f"Q: {p['question']}")
        print(f"A: {p['answer']}")
        print(f"Chain: {' -> '.join(str(c['value']) for c in p['chain'])}")
        print()

    print("\n=== EXAMPLE 3-HOP PROBLEMS ===")
    for p in all_3hop[:5]:
        print(f"Q: {p['question']}")
        print(f"A: {p['answer']}")
        print(f"Chain: {' -> '.join(str(c['value']) for c in p['chain'])}")
        print()

    print("\n=== EXAMPLE 4-HOP PROBLEMS ===")
    for p in all_4hop[:5]:
        print(f"Q: {p['question']}")
        print(f"A: {p['answer']}")
        print(f"Chain: {' -> '.join(str(c['value']) for c in p['chain'])}")
        print()


if __name__ == "__main__":
    main()
