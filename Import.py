import sqlite3
import sys
import xml.etree.ElementTree as ET


# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>

# Read pokemon XML file name from command-line
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")
    sys.exit(1)

# Connect to database
conn = sqlite3.connect('pokemon.sqlite')
cursor = conn.cursor()

# Parse XML files and insert Pokemon into database
for i, arg in enumerate(sys.argv):
    # Skip if this is the Python filename (argv[0])
    if i == 0:
        continue
    
    # Parse XML file
    try:
        tree = ET.parse(arg)
    except:
        print(f"Error: cannot parse XML file {arg}")
        continue
    
    root = tree.getroot()
    
    # Check if Pokemon already exists in database
    name = root.find('name').text
    cursor.execute("SELECT COUNT(*) FROM pokemon WHERE name=?", (name,))
    if cursor.fetchone()[0] > 0:
        print(f"Pokemon {name} already exists in database, skipping")
        continue
    
    # Insert Pokemon into database
    pokemon = {
        'name': name,
        'pokedex': root.attrib.get('pokedexNumber', ''),
        'classification': root.attrib.get('classification', ''),
        'generation': root.attrib.get('generation', ''),
        'hp': root.find('hp').text,
        'attack': root.find('attack').text,
        'defense': root.find('defense').text,
        'speed': root.find('speed').text,
        'sp_attack': root.find('sp_attack').text,
        'sp_defense': root.find('sp_defense').text,
        'height': root.find('height/m').text,
        'weight': root.find('weight/kg').text
    }
    
    # Insert Pokemon into database
    cursor.execute("""INSERT INTO pokemon (name, pokedex, classification, generation, hp, attack, defense, speed, sp_attack, sp_defense, height, weight) 
                      VALUES (:name, :pokedex, :classification, :generation, :hp, :attack, :defense, :speed, :sp_attack, :sp_defense, :height, :weight)""", pokemon)
    conn.commit()
    
    # Insert Pokemon types into database
    types = [t.text for t in root.findall('type')]
    for t in types:
        cursor.execute("INSERT INTO pokemon_type (name, type) VALUES (?, ?)", (name, t))
        conn.commit()
    
    # Insert Pokemon abilities into database
    abilities = [a.text for a in root.findall('abilities/ability')]
    for a in abilities:
        cursor.execute("INSERT INTO pokemon_ability (name, ability) VALUES (?, ?)", (name, a))
        conn.commit()
    
    print(f"Inserted Pokemon {name} into database")
    
# Close database connection
conn.close()
