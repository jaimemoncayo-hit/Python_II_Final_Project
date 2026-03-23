import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pokemon Dashboard", layout="wide")

st.title("⚔️ Pokemon Combat Dashboard")
st.markdown("### First draft of the simulator")
st.divider()

st.write("This dashboard allows users to select two Pokémon, compare their stats, and simulate a battle.")

# Lista ampliada de Pokémon
pokemon_options = [
    "pikachu", "charizard", "bulbasaur", "squirtle",
    "gengar", "dragonite", "snorlax", "lucario"
]

col1, col2 = st.columns(2)

with col1:
    pokemon1 = st.selectbox("Choose Pokémon 1", pokemon_options)

with col2:
    pokemon2 = st.selectbox("Choose Pokémon 2", pokemon_options, index=1)

if pokemon1 == pokemon2:
    st.warning("⚠️ Choose two different Pokémon for battle")

url1 = f"https://pokeapi.co/api/v2/pokemon/{pokemon1}"
url2 = f"https://pokeapi.co/api/v2/pokemon/{pokemon2}"

response1 = requests.get(url1)
response2 = requests.get(url2)

if response1.status_code != 200:
    st.error("Error loading Pokémon 1 data")
    st.stop()

if response2.status_code != 200:
    st.error("Error loading Pokémon 2 data")
    st.stop()

data1 = response1.json()
data2 = response2.json()

st.subheader("⚔️ Battle Simulation")

if pokemon1 != pokemon2 and st.button("🔥 Fight!"):
    stats1_total = sum([stat["base_stat"] for stat in data1["stats"]])
    stats2_total = sum([stat["base_stat"] for stat in data2["stats"]])

    if stats1_total > stats2_total:
        winner = pokemon1
    elif stats2_total > stats1_total:
        winner = pokemon2
    else:
        winner = "Draw"

    st.success(f"🏆 Winner: {winner.upper()}")
    st.write(f"{pokemon1.capitalize()}: {stats1_total} total points")
    st.write(f"{pokemon2.capitalize()}: {stats2_total} total points")

col3, col4 = st.columns(2)

with col3:
    st.subheader(pokemon1.capitalize())
    st.image(data1["sprites"]["front_default"], width=150)
    st.write(f"Height: {data1['height']}")
    st.write(f"Weight: {data1['weight']}")

with col4:
    st.subheader(pokemon2.capitalize())
    st.image(data2["sprites"]["front_default"], width=150)
    st.write(f"Height: {data2['height']}")
    st.write(f"Weight: {data2['weight']}")

stats1 = {stat["stat"]["name"]: stat["base_stat"] for stat in data1["stats"]}
stats2 = {stat["stat"]["name"]: stat["base_stat"] for stat in data2["stats"]}

comparison_df = pd.DataFrame({
    "Stat": list(stats1.keys()),
    pokemon1.capitalize(): list(stats1.values()),
    pokemon2.capitalize(): list(stats2.values())
})

st.divider()

st.subheader("📊 Stats Comparison Table")
st.dataframe(comparison_df)

plot_df = comparison_df.melt(id_vars="Stat", var_name="Pokemon", value_name="Value")

st.subheader("📈 Stats Comparison Chart")
fig = px.bar(plot_df, x="Stat", y="Value", color="Pokemon", barmode="group")
st.plotly_chart(fig, use_container_width=True)