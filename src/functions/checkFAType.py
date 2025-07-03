import json
import textwrap
from prettytable import PrettyTable
from db.dbConnection import get_connection 

def load_all_fas_from_mysql():
    conn = get_connection()
    if conn is None:
        print("❌ Failed to connect to the database.")
        return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM finiteAutomata")
    results = cursor.fetchall()
    conn.close()

    fas = []
    for fa in results:
        try:
            states = fa['state'].split(',')
            alphabet = fa['symbol'].split(',')
            transitions = json.loads(fa['transition'])
            start_state = states[0]
            final_states = [s for s in states if s.endswith("*")]

            fas.append({
                "id": fa['id'],
                "num_states": len(states),
                "num_symbols": len(alphabet),
                "symbols": fa['symbol'],
                "states": fa['state'],
                "transitions_raw": fa['transition'],
                "transitions": transitions,
                "createdAt": fa['createdAt'],
                "start_state": start_state,
                "final_states": final_states
            })
        except Exception as e:
            print(f"Error parsing FA id={fa['id']}: {e}")
            continue

    return fas

def is_deterministic(fa):
    for state in fa['states'].split(','):
        clean_state = state.replace("*", "")
        if clean_state not in fa['transitions']:
            continue
        for symbol in fa['symbols'].split(','):
            if symbol not in fa['transitions'][clean_state]:
                continue
            target = fa['transitions'][clean_state][symbol]
            if isinstance(target, list) and len(target) > 1:
                return False
            if isinstance(target, str) and ',' in target:
                return False
            if target == '-' or target == []:
                continue
    return True

def shorten_transition(transition_str, width=70):
    return textwrap.fill(transition_str, width=width)

def display_fa_list(fa_list):
    table = PrettyTable()
    table.field_names = [
        "id", "numberOfState", "numberOfSymbol", "symbol",
        "state", "transition", "createdAt"
    ]
    table.align["transition"] = "l"
    table.align["state"] = "l"
    table.max_width["transition"] = 70
    table.max_width["state"] = 15

    for fa in fa_list:
        transition_wrapped = shorten_transition(fa['transitions_raw'], 70)
        table.add_row([
            fa['id'],
            fa['num_states'],
            fa['num_symbols'],
            fa['symbols'],
            fa['states'],
            transition_wrapped,
            fa['createdAt'] if fa['createdAt'] else "None"
        ])
    print("\n=== List of Finite Automata ===")
    print(table)

def display_table_and_type(fa):
    table = PrettyTable()
    table.field_names = ["States"] + fa['symbols'].split(',')

    for state in fa['states'].split(','):
        clean_state = state.replace("*", "")
        row = [state]
        for symbol in fa['symbols'].split(','):
            target = fa['transitions'].get(clean_state, {}).get(symbol, '-')
            if isinstance(target, list):
                row.append(",".join(target))
            else:
                row.append(target)
        table.add_row(row)

    print("\nTransition Table:")
    print(table)

    fa_type = "DFA" if is_deterministic(fa) else "NFA"
    print("\nType of Finite Automata:", fa_type)

def check_determinism():
    print("\nCheck Determinism of Finite Automata")

    fa_list = load_all_fas_from_mysql()
    if not fa_list:
        print("\nNo finite automata found in the database.")
        return

    display_fa_list(fa_list)

    while True:
        choice = input("\nEnter the number of FA to check: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(fa_list):
            print("Invalid choice. Please try again.")
        else:
            break

    selected_fa = fa_list[int(choice) - 1]
    display_table_and_type(selected_fa)

if __name__ == "__main__":
    check_determinism()
