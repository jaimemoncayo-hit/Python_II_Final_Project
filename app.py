import random
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Pokemon Combat Simulator", layout="wide")

API_BASE = "https://pokeapi.co/api/v2"
STAT_ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]

pokemon_options = [
    "pikachu", "charizard", "bulbasaur", "squirtle",
    "gengar", "dragonite", "snorlax", "lucario",
    "blastoise", "venusaur", "alakazam", "machamp"
]


@st.cache_data(show_spinner=False)
def fetch_json(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


@st.cache_data(show_spinner=False)
def get_pokemon(name):
    return fetch_json(f"{API_BASE}/pokemon/{name.lower().strip()}")


@st.cache_data(show_spinner=False)
def get_move(name):
    return fetch_json(f"{API_BASE}/move/{name.lower().strip()}")


@st.cache_data(show_spinner=False)
def get_type(name):
    return fetch_json(f"{API_BASE}/type/{name.lower().strip()}")


def extract_stats(data):
    raw_stats = {item["stat"]["name"]: item["base_stat"] for item in data["stats"]}
    return {stat: raw_stats.get(stat, 0) for stat in STAT_ORDER}


def extract_types(data):
    return [item["type"]["name"] for item in data["types"]]


def format_name(text):
    return text.replace("-", " ").title()


def get_damaging_moves(data, limit=8):
    moves = []

    for move_entry in data["moves"][:30]:
        move_name = move_entry["move"]["name"]

        try:
            move_data = get_move(move_name)
        except requests.RequestException:
            continue

        power = move_data.get("power")
        accuracy = move_data.get("accuracy")
        damage_class = move_data.get("damage_class", {}).get("name")
        move_type = move_data.get("type", {}).get("name")

        if power is None:
            continue

        if damage_class not in ["physical", "special"]:
            continue

        moves.append({
            "name": move_name,
            "display_name": format_name(move_name),
            "power": power,
            "accuracy": accuracy if accuracy is not None else 100,
            "type": move_type,
            "class": damage_class,
            "label": f"{format_name(move_name)} | {format_name(move_type)} | Power {power} | Accuracy {accuracy if accuracy is not None else 100}"
        })

    moves = sorted(moves, key=lambda x: (x["power"], x["accuracy"]), reverse=True)

    if not moves:
        return [{
            "name": "struggle",
            "display_name": "Struggle",
            "power": 50,
            "accuracy": 100,
            "type": "normal",
            "class": "physical",
            "label": "Struggle | Normal | Power 50 | Accuracy 100"
        }]

    return moves[:limit]


def type_multiplier(move_type, defender_types):
    try:
        type_data = get_type(move_type)
    except requests.RequestException:
        return 1.0

    relations = type_data.get("damage_relations", {})
    double_damage = {item["name"] for item in relations.get("double_damage_to", [])}
    half_damage = {item["name"] for item in relations.get("half_damage_to", [])}
    no_damage = {item["name"] for item in relations.get("no_damage_to", [])}

    multiplier = 1.0

    for defender_type in defender_types:
        if defender_type in no_damage:
            multiplier *= 0
        elif defender_type in double_damage:
            multiplier *= 2
        elif defender_type in half_damage:
            multiplier *= 0.5

    return multiplier


def effect_text(multiplier):
    if multiplier == 0:
        return "No effect"
    if multiplier > 1:
        return "Super effective"
    if multiplier < 1:
        return "Not very effective"
    return "Normal"


def calculate_damage(attacker_stats, defender_stats, attacker_types, defender_types, move):
    if move["class"] == "physical":
        attack_value = attacker_stats["attack"]
        defense_value = defender_stats["defense"]
    else:
        attack_value = attacker_stats["special-attack"]
        defense_value = defender_stats["special-defense"]

    base_damage = (((2 * 50 / 5) + 2) * move["power"] * (attack_value / max(defense_value, 1))) / 50 + 2
    stab = 1.5 if move["type"] in attacker_types else 1.0
    multiplier = type_multiplier(move["type"], defender_types)
    random_factor = random.uniform(0.90, 1.00)

    damage = int(base_damage * stab * multiplier * random_factor)
    return max(damage, 1) if multiplier != 0 else 0, multiplier


def build_stats_dataframe(name1, name2, stats1, stats2):
    return pd.DataFrame({
        "Stat": [format_name(stat) for stat in STAT_ORDER],
        format_name(name1): [stats1[stat] for stat in STAT_ORDER],
        format_name(name2): [stats2[stat] for stat in STAT_ORDER]
    })


def display_pokemon_card(name, data, types_list):
    st.subheader(format_name(name))
    st.image(data["sprites"]["front_default"], width=140)
    st.write(f"**Types:** {', '.join(format_name(t) for t in types_list)}")
    st.write(f"**Height:** {data['height'] / 10} m")
    st.write(f"**Weight:** {data['weight'] / 10} kg")


def choose_move_from_selectbox(label, moves, key):
    labels = [move["label"] for move in moves]
    selected_label = st.selectbox(label, labels, key=key)
    return next(move for move in moves if move["label"] == selected_label)


def simulate_battle(p1, p2, stats1, stats2, types1, types2, move1, move2):
    hp1 = stats1["hp"]
    hp2 = stats2["hp"]

    battle_log = []
    hp_log = [
        [0, format_name(p1), hp1],
        [0, format_name(p2), hp2]
    ]

    turn = 1
    max_turns = 12

    while hp1 > 0 and hp2 > 0 and turn <= max_turns:
        if stats1["speed"] >= stats2["speed"]:
            order = [
                (p1, stats1, types1, move1, p2, stats2, types2),
                (p2, stats2, types2, move2, p1, stats1, types1)
            ]
        else:
            order = [
                (p2, stats2, types2, move2, p1, stats1, types1),
                (p1, stats1, types1, move1, p2, stats2, types2)
            ]

        for attacker_name, attacker_stats, attacker_types, move, defender_name, defender_stats, defender_types in order:
            if hp1 <= 0 or hp2 <= 0:
                break

            if random.randint(1, 100) > move["accuracy"]:
                battle_log.append([
                    turn,
                    format_name(attacker_name),
                    move["display_name"],
                    0,
                    "Miss",
                    hp1,
                    hp2
                ])
                hp_log.append([turn, format_name(p1), hp1])
                hp_log.append([turn, format_name(p2), hp2])
                continue

            damage, multiplier = calculate_damage(
                attacker_stats, defender_stats, attacker_types, defender_types, move
            )

            if attacker_name == p1:
                hp2 = max(hp2 - damage, 0)
            else:
                hp1 = max(hp1 - damage, 0)

            battle_log.append([
                turn,
                format_name(attacker_name),
                move["display_name"],
                damage,
                effect_text(multiplier),
                hp1,
                hp2
            ])

            hp_log.append([turn, format_name(p1), hp1])
            hp_log.append([turn, format_name(p2), hp2])

        turn += 1

    if hp1 > hp2:
        winner = format_name(p1)
    elif hp2 > hp1:
        winner = format_name(p2)
    else:
        winner = "Draw"

    battle_df = pd.DataFrame(
        battle_log,
        columns=["Turn", "Attacker", "Move", "Damage", "Effect", f"{format_name(p1)} HP", f"{format_name(p2)} HP"]
    )

    hp_df = pd.DataFrame(hp_log, columns=["Turn", "Pokemon", "HP"])

    return winner, battle_df, hp_df


st.title("Pokemon Combat Simulator")
st.markdown("Compare Pokémon stats, choose one move for each fighter, and simulate a battle.")

left_col, right_col = st.columns(2)

with left_col:
    pokemon1_name = st.selectbox("Pokemon 1", pokemon_options, index=0)

with right_col:
    pokemon2_name = st.selectbox("Pokemon 2", pokemon_options, index=1)

if pokemon1_name == pokemon2_name:
    st.warning("Choose two different Pokémon.")
    st.stop()

try:
    pokemon1_data = get_pokemon(pokemon1_name)
    pokemon2_data = get_pokemon(pokemon2_name)
except requests.RequestException:
    st.error("Could not load data from the PokeAPI. Please try again.")
    st.stop()

stats1 = extract_stats(pokemon1_data)
stats2 = extract_stats(pokemon2_data)

types1 = extract_types(pokemon1_data)
types2 = extract_types(pokemon2_data)

moves1 = get_damaging_moves(pokemon1_data)
moves2 = get_damaging_moves(pokemon2_data)

card1, card2 = st.columns(2)

with card1:
    display_pokemon_card(pokemon1_name, pokemon1_data, types1)
    move1 = choose_move_from_selectbox("Move for Pokémon 1", moves1, "move_1")

with card2:
    display_pokemon_card(pokemon2_name, pokemon2_data, types2)
    move2 = choose_move_from_selectbox("Move for Pokémon 2", moves2, "move_2")

comparison_df = build_stats_dataframe(pokemon1_name, pokemon2_name, stats1, stats2)

st.subheader("Stats Comparison")
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

plot_df = comparison_df.melt(id_vars="Stat", var_name="Pokemon", value_name="Value")
fig_stats = px.bar(plot_df, x="Stat", y="Value", color="Pokemon", barmode="group", text="Value")
fig_stats.update_layout(xaxis_title="", yaxis_title="Base Stat")
st.plotly_chart(fig_stats, use_container_width=True)

st.subheader("Battle")

summary_left, summary_right = st.columns(2)
with summary_left:
    st.write(f"**{format_name(pokemon1_name)}** will use **{move1['display_name']}**.")
with summary_right:
    st.write(f"**{format_name(pokemon2_name)}** will use **{move2['display_name']}**.")

if st.button("Simulate battle", use_container_width=True):
    winner, battle_df, hp_df = simulate_battle(
        pokemon1_name, pokemon2_name,
        stats1, stats2,
        types1, types2,
        move1, move2
    )

    if winner == "Draw":
        st.info("The battle ended in a draw.")
    else:
        st.success(f"{winner} wins the battle!")

    st.dataframe(battle_df, use_container_width=True, hide_index=True)

    fig_hp = px.line(hp_df, x="Turn", y="HP", color="Pokemon", markers=True)
    fig_hp.update_layout(yaxis_title="Remaining HP")
    st.plotly_chart(fig_hp, use_container_width=True)