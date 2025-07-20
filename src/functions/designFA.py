from datetime import datetime
import json
from db.dbConnection import get_connection
from prettytable import PrettyTable

def designFA():
    print("\n===== Design Finite Automata =====")
    typeOfFA = 'DFA'

    # Input number of states
    while True:
        try:
            num_states = int(input("\nEnter the number of states: "))
            if num_states > 0:
                break
            print("Number of states must be greater than 0.")
        except ValueError:
            print("Please enter a valid integer.")

    # Input number of symbols
    while True:
        try:
            num_symbols = int(input("Enter the number of input symbols: "))
            if num_symbols > 0:
                break
            print("Number of symbols must be greater than 0.")
        except ValueError:
            print("Please enter a valid integer.")

    symbols = [input(f"\t- Enter symbol {i+1}: ") for i in range(num_symbols)]

    # Initialize states A, B, C, ...
    base_states = [chr(65 + i) for i in range(num_states)]
    final_states = []

    print("\nCurrent States and Symbols:")
    print("\t- Symbols:", symbols)
    print("\t- States:", base_states)

    # Input final states
    while True:
        try:
            num_final = int(input("Enter the number of final states: "))
            if 0 < num_final <= num_states:
                break
            print("Must be between 1 and number of states.")
        except ValueError:
            print("Please enter a valid number.")

    for i in range(num_final):
        while True:
            state = input(f"\t- Enter final state {i+1}: ").upper()
            if state in base_states:
                final_states.append(state)
                break
            else:
                print(f"{state} is not a valid state.")

    has_epsilon = input("Does your FA have an epsilon transition? (y/n): ").strip().lower()
    if has_epsilon == 'y':
        symbols.append('ε')
        typeOfFA = 'NFA'

    # Build transition table
    print("\nEnter the transition:")
    print("Use '-' for no transition; use commas for NFA (e.g., B,C)")

    transition_table = []
    for state in base_states:
        row = []
        for sym in symbols:
            while True:
                value = input(f"\t- {state} with '{sym}': ").strip()
                if value == '-':
                    row.append('-')
                    typeOfFA = 'NFA'
                    break
                elif ',' in value:
                    targets = [v.strip() for v in value.split(',')]
                    if not all(t in base_states for t in targets):
                        print("Invalid state in input.")
                        continue
                    row.append(targets)
                    typeOfFA = 'NFA'
                    break
                elif value in base_states:
                    row.append(value)
                    break
                else:
                    print("Invalid input. Try again.")
        transition_table.append(row)

    # Create display states with * for finals
    display_states = [s + '*' if s in final_states else s for s in base_states]

    # Show transition table
    print("\nTransition Table:")
    table = PrettyTable()
    table.field_names = ["States"] + symbols
    for i, state in enumerate(display_states):
        table.add_row([state] + transition_table[i])
    print(table)
    print("\nFA Type:", typeOfFA)

    # Input FA name
    fa_name = input("Enter a name for your Finite Automaton: ").strip()

    if input(f"Save FA '{fa_name}' to database? (y/n): ").lower() != 'y':
        print("FA not saved.")
        return

    # JSON conversion (UTF-safe for ε)
    transition_dict = {}
    for i, state in enumerate(base_states):
        label = state + '*' if state in final_states else state
        state_transitions = {}
        for j, sym in enumerate(symbols):
            val = transition_table[i][j]
            state_transitions[sym] = val
        transition_dict[label] = state_transitions

    json_states = json.dumps(display_states, ensure_ascii=False)
    json_symbols = json.dumps(symbols, ensure_ascii=False)
    json_transition = json.dumps(transition_dict, ensure_ascii=False)

    # Save to DB
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO finiteAutomata (faName, numberOfState, numberOfSymbol, symbol, state, transition, faType, createdAt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    fa_name, num_states, num_symbols, json_symbols,
                    json_states, json_transition, typeOfFA, datetime.now()
                ))
            conn.commit()
            print("✅ FA saved successfully.")
        except Exception as e:
            print("❌ Error saving FA:", e)
        finally:
            conn.close()
    else:
        print("❌ Failed to connect to the database.")

    # Ask to continue
    again = input("Design another FA? (y/n): ").lower()
    if again == 'y':
        designFA()
    else:
        print("Done. Goodbye!")
