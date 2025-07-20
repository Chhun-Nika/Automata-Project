import json
from db.dbConnection import get_connection
from prettytable import PrettyTable

def testInputStringById():
    print("\n===== Test Input String =====")

    conn = get_connection()
    if not conn:
        print("❌ Could not connect to the database.")
        return

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM finiteAutomata")
        fas = cursor.fetchall()

        if not fas:
            print("⚠️  No Finite Automata found.")
            return

        # Show all FA in a summary table
        print("\n📋 Available Finite Automata:\n")
        table = PrettyTable()
        table.field_names = ["ID", "FA Name", "States", "Symbols", "Type", "Created At"]

        for fa in fas:
            table.add_row([
                fa["id"],
                fa.get("faName", "Unnamed"),
                fa["numberOfState"],
                fa["numberOfSymbol"],
                fa["faType"],
                fa["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            ])
        print(table)

        # Prompt user for FA ID
        print("\n🔍 Select a Finite Automaton by ID to test input strings.\n")
        fa_id = int(input("Enter FA ID: ").strip())

        cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s", (fa_id,))
        fa = cursor.fetchone()

        if not fa:
            print(f"❌ No FA found with ID {fa_id}")
            return

        states_raw = json.loads(fa["state"])
        symbols = json.loads(fa["symbol"])
        transitions = json.loads(fa["transition"])
        fa_type = fa["faType"]

        final_states = [s.replace('*', '') for s in states_raw if '*' in s]
        base_states = [s.replace('*', '') for s in states_raw]
        start_state = base_states[0]

        print("\n📊 Transition Table:")
        table = PrettyTable()
        table.field_names = ["State"] + symbols
        for state in states_raw:
            row = [state]
            for sym in symbols:
                val = transitions[state].get(sym, '-')
                row.append(val)
            table.add_row(row)
        print(table)
        print("ℹ️  Note: States marked with '*' are final states.")

        # Test loop
        while True:
            input_str = input("\n🔡 Enter input string (or 'n' to exit): ").strip()
            if input_str.lower() == 'n':
                print("👋 Exiting input string test.")
                break

            current_states = [start_state]
            valid = True

            for ch in input_str:
                if ch not in symbols:
                    print(f"❌ Symbol '{ch}' is not part of the alphabet: {symbols}")
                    valid = False
                    break

                next_states = []
                for state in current_states:
                    trans = transitions.get(state, {}).get(ch, '-')
                    if trans == '-' or not trans:
                        continue
                    if isinstance(trans, list):
                        next_states.extend(trans)
                    else:
                        next_states.append(trans)

                if not next_states:
                    print(f"❌ No valid transitions on '{ch}' from state(s): {current_states}")
                    valid = False
                    break

                current_states = next_states

            if valid:
                if any(s in final_states for s in current_states):
                    print(f"\n✅ Accepted! Ended in final state(s): {current_states}")
                else:
                    print(f"\n❌ Rejected. Ended in non-final state(s): {current_states}")

    except Exception as e:
        print("🚨 Error during execution:", e)
    finally:
        cursor.close()
        conn.close()

def run_test_string(input_str, states, symbols, transitions, fa_type):
    final_states = [s.replace('*', '') for s in states if '*' in s]
    states = [s.replace('*', '') for s in states]
    current_state = states[0]

    for ch in input_str:
        if ch not in symbols:
            return f"❌ Invalid symbol: '{ch}'"
        next_state = transitions.get(current_state, {}).get(ch)
        if not next_state or next_state == '-':
            return f"❌ Rejected: No transition from {current_state} on '{ch}'"
        if isinstance(next_state, list):
            current_state = next_state[0]
        else:
            current_state = next_state

    return "✅ Accepted" if current_state in final_states else "❌ Rejected"

