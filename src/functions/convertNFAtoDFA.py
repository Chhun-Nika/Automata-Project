from prettytable import PrettyTable;
import json;
from db.dbConnection import get_connection;
from datetime import datetime

def convertNFAtoDFA():
    print("\n===== Converting Nondeterministic Finite Automata (NFA) to Deterministic Finite Automata (DFA) =====\n");
    print("*** Here are the Nondeterministic Finite Automata (NFA) in your Database ***\n");

    # test the connect to the database
    conn = get_connection();
    if not conn:
        print("Could not connect to the Database!");
        return
    cursor = conn.cursor(dictionary=True)
    try: 
        cursor.execute("SELECT * FROM finiteAutomata WHERE faType = %s", ("NFA",))
        fas = cursor.fetchall()

        if not fas:
            print("Not Finite Automata Found.");

        # create pretty table 
        table = PrettyTable()
        table.field_names = [
            "ID", "FAName", "NumbeOfState", "NumberOfSymbol", "Symbol", "State", "Transition", "FAType", "CreatedAt"
        ]

        for fa in fas:
            table.add_row([
                fa["id"],
                fa.get("faName", "Unnamed"),
                fa["numberOfState"],
                fa["numberOfSymbol"],
                json.loads(fa["symbol"]),
                json.loads(fa["state"]),
                json.loads(fa["transition"]),
                fa["faType"],
                fa["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            ])

        print(table);
    
        print("\n*** Enter the ID of NFA that you want to convert it to DFA ***\n");

        nfa_ids = [fa["id"] for fa in fas] 

        while True:
            try:
                selectID = int(input("Enter the ID of Nondeterministic Finite Automata: "))
                if selectID in nfa_ids:
                    break
                print("\nInvalid ID. Please select one from the list above.\n")
            except ValueError:
                print("\nPlease enter a valid integer.\n")

        cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s", (selectID,));
        fas = cursor.fetchall();

        if not fas:
            print("No FA found with ID");

        # create pretty table for selected FA
        table1 = PrettyTable()
        table1.field_names = [
            "Symbol", "State", "Transition"
        ]

        for fa in fas:
            table1.add_row([
                json.loads(fa["symbol"]),
                json.loads(fa["state"]),
                json.loads(fa["transition"])
            ])
        print("\n*** Here is the transition table of your NFA, you have selected. ***\n");
        print(table1);
        print("Noted! State With * is Final State");
    
        # convert list (that was store as json in database) into python script 
        symbols = json.loads(fa["symbol"])    
        raw_states = json.loads(fa["state"])      
        nfa_transitions = json.loads(fa["transition"]) 
        start_state = raw_states[0].replace("*","") # assume that first state of list is the start-state and for the final state remove * 
        nfa_finals = {s.replace("*","") for s in raw_states if "*" in s} # extracts all final states from the raw_states list and removes * and stores them in a set.

        # Handle the state that what other state can reach by the epsilon transition
        def epsilon_closure(state_set):
            closure = set(state_set)
            stack = list(state_set) # we use concept LIFO
            while stack:
                q = stack.pop()
                for nxt in nfa_transitions.get(q, {}).get("ε", []):
                    if nxt not in closure:
                        closure.add(nxt)
                        stack.append(nxt)
            return closure
        
        step_number = 1
        
        symbols_no_eps = [s for s in symbols if s != "ε"]
        dfa_states = []
        dfa_unmarked = []
        dfa_delta = {}

        first = epsilon_closure({start_state})
        dfa_states.append(first)
        dfa_unmarked.append(first)

        state_name = lambda s: "".join(sorted(s)) if s else "∅"

        while dfa_unmarked:
            curr = dfa_unmarked.pop(0)
            curr_key = tuple(sorted(curr))
            dfa_delta[curr_key] = {}

            row = [state_name(curr)]  # for printing current step

            for sym in symbols_no_eps:
                dest = set()
                for q in curr:
                    dest.update(nfa_transitions.get(q, {}).get(sym, []))
                dest_cl = epsilon_closure(dest)
                dfa_delta[curr_key][sym] = dest_cl

                if dest_cl and dest_cl not in dfa_states:
                    dfa_states.append(dest_cl)
                    dfa_unmarked.append(dest_cl)

                row.append(state_name(dest_cl))

            # Print only 1 row for this current step
            table = PrettyTable()
            table.field_names = ["s.s"] + symbols_no_eps
            
            # loop every step to keep it link together 
            for state in dfa_delta:
                row = [state_name(state)]
                for sym in symbols_no_eps:
                    target = dfa_delta[state].get(sym, set())
                    row.append(state_name(target) if target else "∅")
                table.add_row(row)

            print(f"\nConvert NFA to DFA:\n#{step_number} step:")
            print(table)
            step_number += 1

        # display the final result of converting 
        dfa_table = PrettyTable()
        dfa_table.field_names = ["Symbol", "State", "Transition"]

        # Convert symbols to JSON
        symbol_json = json.dumps(symbols_no_eps)

        # Generate state names, mark final states with '*'
        dfa_state_names = []
        dfa_transition_map = {}

        def mark_state(state_set):
            name = "".join(sorted(state_set))
            if any(s in nfa_finals for s in state_set):
                name += "*"
            return name

        # Map DFA states to names
        state_name_map = {}
        for state in dfa_states:
            name = mark_state(state)
            state_name_map[tuple(sorted(state))] = name
            dfa_state_names.append(name)

        # Create DFA transitions using readable names
        for state in dfa_states:
            state_key = state_name_map[tuple(sorted(state))]
            dfa_transition_map[state_key] = {}
            for sym in symbols_no_eps:
                target = dfa_delta.get(tuple(state), {}).get(sym, set())
                if target:
                    target_key = state_name_map[tuple(sorted(target))]
                    dfa_transition_map[state_key][sym] = target_key

        # Convert states and transitions to JSON
        state_json = json.dumps(dfa_state_names)
        transition_json = json.dumps(dfa_transition_map)

        # Add to table
        dfa_table.add_row([symbol_json, state_json, transition_json])
        print("\n===== Here is the DFA converted from your NFA =====\n")
        print(dfa_table)

        # ask user whether they want to minimize DFA or not 
        NameOfFA = input("Enter the Name of DFA minimization: ")

        save_confirm = input(f"Do you want to save this minimize DFA '{NameOfFA}' to the database? (y/n): ").lower()
        if save_confirm != 'y':
            print("DFA not saved.")
            return 
        
        # count the number of state and symbol by using len 
        num_states = len(json.loads(state_json))
        num_symbols = len(json.loads(symbol_json))
        
        # save to database
        conn = get_connection()
        if conn: 
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO finiteAutomata (faName, numberOfState , numberOfSymbol , symbol, state, transition, faType, createdAt)
                            VALUES (%s, %s , %s, %s, %s, %s, %s, %s)""", (
                                NameOfFA,
                                num_states,
                                num_symbols,
                                symbol_json,
                                state_json,
                                transition_json,
                                'DFA',
                                datetime.now()
                            ))
                conn.commit()
                print("DFA save to database")

            except Exception as e:
                print("Error While Loading to Database", e)
            finally:
                cursor.close()
                conn.close()
                
    except Exception as e:
        print("Error While Loading NAF Data", e);
    finally:
        cursor.close()
        conn.close()

def convert_nfa_to_dfa_web(fa_id):
    from db.dbConnection import get_connection
    from datetime import datetime
    import json

    conn = get_connection()
    nfa_table = []
    dfa_table = []
    result = None

    if not conn:
        return None, None, "❌ Could not connect to database"

    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s AND faType = 'NFA'", (fa_id,))
            fa = cursor.fetchone()

            if not fa:
                return None, None, f"❌ No NFA found with ID {fa_id}"

            symbols = json.loads(fa["symbol"])
            raw_states = json.loads(fa["state"])
            nfa_transitions = json.loads(fa["transition"])
            start_state = raw_states[0].replace("*", "")
            nfa_finals = {s.replace("*", "") for s in raw_states if "*" in s}

            # Build NFA transition table
            nfa_table.append(["State"] + symbols)
            for state in raw_states:
                row = [state]
                for sym in symbols:
                    targets = nfa_transitions.get(state.replace("*", ""), {}).get(sym, "∅")
                    if isinstance(targets, list):
                        targets = ",".join(targets)
                    elif not targets:
                        targets = "∅"
                    row.append(targets)
                nfa_table.append(row)

            # ε-closure helper
            def epsilon_closure(state_set):
                closure = set(state_set)
                stack = list(state_set)
                while stack:
                    q = stack.pop()
                    for nxt in nfa_transitions.get(q, {}).get("ε", []):
                        if nxt not in closure:
                            closure.add(nxt)
                            stack.append(nxt)
                return closure

            # Start DFA construction
            symbols_no_eps = [s for s in symbols if s != "ε"]
            dfa_states = []
            dfa_unmarked = []
            dfa_delta = {}

            first = epsilon_closure({start_state})
            dfa_states.append(first)
            dfa_unmarked.append(first)

            while dfa_unmarked:
                curr = dfa_unmarked.pop(0)
                curr_key = tuple(sorted(curr))
                dfa_delta[curr_key] = {}

                for sym in symbols_no_eps:
                    dest = set()
                    for q in curr:
                        dest.update(nfa_transitions.get(q, {}).get(sym, []))
                    dest_cl = epsilon_closure(dest)
                    dfa_delta[curr_key][sym] = dest_cl
                    if dest_cl and dest_cl not in dfa_states:
                        dfa_states.append(dest_cl)
                        dfa_unmarked.append(dest_cl)

            # Mapping for state name → formatted string
            def format_state(state_set):
                if not state_set:
                    return "∅"
                label = "[" + ", ".join(sorted(state_set)) + "]"
                if any(s in nfa_finals for s in state_set):
                    label += "*"
                return label

            dfa_table.append(["State"] + symbols_no_eps)
            final_state_labels = []
            transition_dict = {}

            for state in dfa_states:
                formatted = format_state(state)
                row = [formatted]
                transition_dict[formatted] = {}
                for sym in symbols_no_eps:
                    target = dfa_delta.get(tuple(state), {}).get(sym, set())
                    target_label = format_state(target)
                    row.append(target_label)
                    transition_dict[formatted][sym] = target_label
                if formatted.endswith("*"):
                    final_state_labels.append(formatted)
                dfa_table.append(row)

            result = f"✅ NFA ID {fa_id} converted successfully."

            # Save to DB (including finalStates)
            cursor.execute("""
                INSERT INTO finiteAutomata (faName, numberOfState, numberOfSymbol, symbol, state, finalStates, transition, faType, createdAt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"{fa['faName']}_to_DFA",
                len(dfa_states),
                len(symbols_no_eps),
                json.dumps(symbols_no_eps),
                json.dumps([row[0] for row in dfa_table[1:]]),
                json.dumps(final_state_labels),
                json.dumps(transition_dict),
                "DFA",
                datetime.now()
            ))
            conn.commit()

    except Exception as e:
        result = f"❌ Conversion error: {e}"

    finally:
        conn.close()

    return nfa_table, dfa_table, result
