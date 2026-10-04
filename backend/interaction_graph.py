import json
import os
import re
import networkx as nx


RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "compatibility_rules.json"
)


with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)


def clean_name(name):
    """
    Normalize ingredient names for interaction matching.
    """
    name = name.lower().strip()

    # Keep letters, numbers, &, and hyphens
    name = re.sub(r"[^a-z0-9&-]", "-", name)

    # Remove repeated hyphens
    name = re.sub(r"-+", "-", name)

    # Remove leading/trailing hyphens
    name = name.strip("-")

    return name


def get_group_for_ingredient(ingredient):
    """
    Find which interaction group an ingredient belongs to.
    """

    cleaned = clean_name(ingredient)

    for group_name, group_data in RULES.get("groups", {}).items():

        if not isinstance(group_data, list):
            continue

        cleaned_group_ingredients = [
            clean_name(item)
            for item in group_data
        ]

        if cleaned in cleaned_group_ingredients:
            return group_name

    return None


def find_relationship(group_a, group_b):
    """
    Find the relationship between two ingredient groups.
    """

    if not group_a or not group_b:
        return None

    # The dataset stores interaction rules under "rules"
    rules = RULES.get("rules", [])

    for rule in rules:

        first = rule.get("a")
        second = rule.get("b")

        if (
            (first == group_a and second == group_b)
            or
            (first == group_b and second == group_a)
        ):
            return rule

    return None


def build_interaction_graph(ingredients):
    """
    Build a graph where:
    - nodes = ingredients
    - edges = known interactions
    """

    graph = nx.Graph()

    cleaned_ingredients = [
        clean_name(ingredient)
        for ingredient in ingredients
    ]

    # Add ingredient nodes
    for ingredient in cleaned_ingredients:

        graph.add_node(
            ingredient,
            group=get_group_for_ingredient(ingredient)
        )

    # Compare every ingredient pair
    for i in range(len(cleaned_ingredients)):

        for j in range(i + 1, len(cleaned_ingredients)):

            ingredient_a = cleaned_ingredients[i]
            ingredient_b = cleaned_ingredients[j]

            group_a = get_group_for_ingredient(
                ingredient_a
            )

            group_b = get_group_for_ingredient(
                ingredient_b
            )

            relationship = find_relationship(
                group_a,
                group_b
            )

            if relationship:

                graph.add_edge(
                    ingredient_a,
                    ingredient_b,
                    severity=relationship.get("severity"),
                    reason=relationship.get("reason"),
                    recommendation=relationship.get(
                        "recommendation"
                    ),
                    group_a=group_a,
                    group_b=group_b
                )

    return graph


def analyze_interactions(ingredients):

    graph = build_interaction_graph(
        ingredients
    )

    conflicts = []
    cautions = []
    beneficial = []

    for (
        ingredient_a,
        ingredient_b,
        data
    ) in graph.edges(data=True):

        reason = data.get("reason")
        recommendation = data.get(
            "recommendation"
        )
        severity = data.get("severity")

        # Create a human-readable explanation
        if reason:

            explanation = (
                f"{ingredient_a} and {ingredient_b} "
                f"are flagged because "
                f"{reason.rstrip('.')}."
            )

        else:

            explanation = (
                f"{ingredient_a} and {ingredient_b} "
                f"are flagged by the interaction rules."
            )

        result = {
            "ingredient_a": ingredient_a,
            "ingredient_b": ingredient_b,
            "severity": severity,
            "reason": reason,
            "recommendation": recommendation,
            "explanation": explanation
        }

        if severity == "avoid":

            conflicts.append(result)

        elif severity == "caution":

            cautions.append(result)

        elif severity in [
            "great",
            "good",
            "essential"
        ]:

            beneficial.append(result)

    return {
        "ingredients": list(graph.nodes),
        "conflicts": conflicts,
        "cautions": cautions,
        "beneficial_combinations": beneficial
    }