Pokemon Combat Simulator
___________________________________________________________________________________
Project Overview

This project is an interactive Pokémon battle simulator built with Streamlit, using real-time data from the PokeAPI.

Users can select two Pokémon, compare their base stats, choose one move for each, and simulate a battle based on stats, move power, and type effectiveness.

The goal of the project is to combine API usage, data processing, and visualization into a simple and functional application.
___________________________________________________________________________________

Features
Pokémon selection from a predefined list
Display of basic Pokémon information (types, height, weight)
Comparison of base stats using tables and charts
Selection of damaging moves only
Turn-based battle simulation
Damage calculation including move power, accuracy, STAB (Same Type Attack Bonus), and type effectiveness
Battle log showing each turn
HP evolution chart during the battle
Technologies Used
Python
Streamlit
Pandas
Plotly
Requests
PokeAPI
API Usage
___________________________________________________________________________________

The application uses the following endpoints from the PokeAPI:

/pokemon/ to retrieve Pokémon data (stats, types, moves)
/move/ to obtain move details (power, accuracy, damage class)
/type/ to calculate type effectiveness

To improve performance and avoid unnecessary requests, API calls are cached using @st.cache_data.
___________________________________________________________________________________

How to Run the App
Clone the repository:

git clone https://github.com/jaimemoncayo-hit/Python_II_Final_Project.git

Install the required libraries:

pip install -r requirements.txt

Run the application:

streamlit run app.py
___________________________________________________________________________________

Live App

https://pokemon-combat-simulator-g1.streamlit.app/
___________________________________________________________________________________

Project Structure

app.py
requirements.txt
README.md
config.toml
___________________________________________________________________________________

Team Contributions

This project was developed collaboratively by:

Dalton Kern
Worked on API integration and data extraction from the PokeAPI.

Isaam El Hoss
Focused on data processing and structuring using pandas.

Max Tieffenbacher
Developed the battle logic and damage calculation system.

Maria de la Cruz
Worked on the user interface and data visualizations in Streamlit.

Jaime Moncayo
Integrated all components, handled debugging, and finalized the application.

All team members contributed to testing, improvements, and final adjustments.
___________________________________________________________________________________

Example Use Case

A user selects two Pokémon, compares their stats, chooses a move for each, and simulates a battle. The system calculates damage dynamically and displays the results through a battle log and a visual representation of HP changes over time.
___________________________________________________________________________________

Conclusion

This project demonstrates how to combine real-time data from APIs, data analysis with pandas, and interactive visualization into a complete application.