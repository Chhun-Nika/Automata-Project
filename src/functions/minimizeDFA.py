from prettytable import PrettyTable
import json
from db.dbConnection import get_connection
from datetime import datetime
from itertools import combinations

def minimizeDFA():
    print("\nMinimizing Deterministic Finite Automata (DFA)\n")
    print("*** Here are the deterministic Finite Automata (DFA) in your Database ***\n")

    conn = get_connection()
    if not conn:
        print("Could not connect to the Database!")
        return

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM finiteAutomata WHERE faType = %s", ("DFA",))
        fas = cursor.fetchall()

        if not fas:
            print("No Finite Automata Found.")
            return

        table = PrettyTable()
        table.field_names = [
            "ID", "FAName", "NumberOfState", "NumberOfSymbol", "Symbol",
            "State", "Transition", "FAType", "CreatedAt"
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
        print(table)

        print("\n*** Enter the ID of DFA that you want to minimize ***\n");

        dfa_ids = [fa["id"] for fa in fas] 

        while True:
            try:
                selectID = int(input("Enter the ID of Nondeterministic Finite Automata: "))
                if selectID in dfa_ids:
                    break
                print("\nInvalid ID. Please select one from the list above.\n")
            except ValueError:
                print("\nPlease enter a valid integer.\n")

        cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s", (selectID,));
        fa = cursor.fetchone();

        if not fa:
            print("No FA found with ID");

        table1 = PrettyTable()
        table1.field_names = ["Symbol", "State", "Transition"]
        table1.add_row([
            json.loads(fa["symbol"]),
            json.loads(fa["state"]),
            json.loads(fa["transition"])
        ])

        print("\n*** Here is the transition table of your NFA, you have selected. ***\n");
        print(table1);
        print("Noted! State With * is Final State");
        
        states_raw = json.loads(fa["state"])
        symbols = json.loads(fa["symbol"])
        transitions_raw = json.loads(fa["transition"])

        clean_states = [s.rstrip("*") for s in states_raw]
        final_states = {s.rstrip("*") for s in states_raw if s.endswith("*")}

        print("\n*** Here are the step of processing Minimize ***\n")
        
        # Step 1: Non-accessible states
        print("Step1: Find non accessible state")
        start_state = clean_states[0]
        reachable = set()
        queue = [start_state]
        while queue:
            curr = queue.pop(0)
            reachable.add(curr)
            for sym in symbols:
                tgt = transitions_raw.get(curr, {}).get(sym)
                if tgt and tgt not in reachable:
                    queue.append(tgt)
        non_accessible = set(clean_states) - reachable
        if not non_accessible:
            print("We have no non accessible state.\n")
        else:
            print("Non-accessible states:", ", ".join(non_accessible), "\n")

        # Step 2: Mark distinguishable pairs
        print("Step2: Find no marked state")
        pairs = list(combinations(sorted(clean_states), 2))
        marked = {}
        dependents = {}

        for (s1, s2) in pairs:
            key = tuple(sorted((s1, s2)))
            if (s1 in final_states) != (s2 in final_states):
                marked[key] = True
            else:
                marked[key] = False
                dependents[key] = []

        # Register dependencies
        for (s1, s2) in pairs:
            if marked[(s1, s2)]:
                continue
            for sym in symbols:
                t1 = transitions_raw.get(s1, {}).get(sym)
                t2 = transitions_raw.get(s2, {}).get(sym)
                if not t1 or not t2:
                    continue
                t1_clean = t1.rstrip("*")
                t2_clean = t2.rstrip("*")
                trans_key = tuple(sorted((t1_clean, t2_clean)))
                if trans_key not in marked:
                    continue
                dependents.setdefault(trans_key, []).append((s1, s2))

        # Propagate markings
        queue = [k for k, v in marked.items() if v]
        while queue:
            key = queue.pop()
            for dep in dependents.get(key, []):
                if not marked[dep]:
                    marked[dep] = True
                    queue.append(dep)

        # Union-Find helper functions 
        def find(parent, x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]  # path compression
                x = parent[x]
            return x

        def union(parent, rank, x, y):
            rootX = find(parent, x)
            rootY = find(parent, y)
            if rootX != rootY:
                if rank[rootX] < rank[rootY]:
                    parent[rootX] = rootY
                elif rank[rootX] > rank[rootY]:
                    parent[rootY] = rootX
                else:
                    parent[rootY] = rootX
                    rank[rootX] += 1

        # Initialize union-find structure 
        parent = {s: s for s in clean_states}
        rank = {s: 0 for s in clean_states}

        # Union all unmarked pairs (equivalent states)
        for (s1, s2), marked_flag in marked.items():
            if not marked_flag:
                union(parent, rank, s1, s2)

        # Group states by their root parent
        groups_dict = {}
        for s in clean_states:
            root = find(parent, s)
            groups_dict.setdefault(root, set()).add(s)

        groups = [sorted(list(group)) for group in groups_dict.values()]

        for g in groups:
            print("Group:", "[" + ", ".join(g) + "]")
        print(f"\nFinally, there are {len(groups)} states of DFA.\n")

        print("\nStep3: The minimal DFA (Final)")

        # Create the table with dynamic column headers
        table = PrettyTable()
        table.field_names = ["State"] + symbols

        # Build a map from each state to its group tuple (sorted) for easy lookup
        group_map = {}
        for g in groups:
            g_tuple = tuple(sorted(g))
            for s in g:
                group_map[s] = g_tuple

        # Fill the table rows
        for g in groups:
            rep = g[0]  # Representative state
            label = "[" + ", ".join(g) + "]"
            if any(s in final_states for s in g):
                label += "*"  # Mark final states

            row = [label]

            for sym in symbols:
                target = transitions_raw.get(rep, {}).get(sym)
                if target:
                    target_clean = target.rstrip("*")
                    tgt_group = group_map.get(target_clean)
                    if tgt_group:
                        tgt_label = "[" + ", ".join(tgt_group) + "]"
                    else:
                        tgt_label = "None"
                else:
                    tgt_label = "None"

                row.append(tgt_label)

            table.add_row(row)

        # Print the table
        print(table)

    except Exception as e:
        print("Error While Loading from Database:", e)
    finally:
        cursor.close()
        conn.close()

def minimize_dfa_by_id(fa_id):
    from db.dbConnection import get_connection
    import json
    from itertools import combinations

    result = ""
    table_data = []

    conn = get_connection()
    if not conn:
        return "❌ Cannot connect to the database.", None, None, None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s AND faType = %s", (fa_id, "DFA"))
        fa = cursor.fetchone()

        if not fa:
            return f"❌ No DFA found with ID {fa_id}.", None, None, None

        states_raw = json.loads(fa["state"])
        symbols = json.loads(fa["symbol"])
        transitions_raw = json.loads(fa["transition"])

        # Normalize state names
        clean_states = [s.rstrip("*") for s in states_raw]
        final_states = {s.rstrip("*") for s in states_raw if s.endswith("*")}
        start_state = clean_states[0]

        # Normalize transitions by stripping '*' from keys
        normalized_transitions = {}
        for state, trans in transitions_raw.items():
            state_clean = state.rstrip("*")
            normalized_transitions[state_clean] = {}
            for sym, tgt in trans.items():
                normalized_transitions[state_clean][sym] = tgt
        transitions_raw = normalized_transitions

        # Step 1: Remove unreachable states
        reachable = set()
        queue = [start_state]
        while queue:
            curr = queue.pop(0)
            reachable.add(curr)
            for sym in symbols:
                tgt = transitions_raw.get(curr, {}).get(sym)
                if tgt:
                    tgt_clean = tgt.rstrip("*")
                    if tgt_clean not in reachable:
                        queue.append(tgt_clean)
        clean_states = list(reachable)

        # Step 2: Mark distinguishable state pairs
        pairs = list(combinations(sorted(clean_states), 2))
        marked = {}
        dependents = {}

        for (s1, s2) in pairs:
            key = tuple(sorted((s1, s2)))
            if (s1 in final_states) != (s2 in final_states):
                marked[key] = True
            else:
                marked[key] = False
                dependents[key] = []

        for (s1, s2) in pairs:
            if marked[(s1, s2)]:
                continue
            for sym in symbols:
                t1 = transitions_raw.get(s1, {}).get(sym)
                t2 = transitions_raw.get(s2, {}).get(sym)
                if not t1 or not t2:
                    continue
                t1_clean = t1.rstrip("*")
                t2_clean = t2.rstrip("*")
                trans_key = tuple(sorted((t1_clean, t2_clean)))
                if trans_key not in marked:
                    continue
                dependents.setdefault(trans_key, []).append((s1, s2))

        queue = [k for k, v in marked.items() if v]
        while queue:
            key = queue.pop()
            for dep in dependents.get(key, []):
                if not marked[dep]:
                    marked[dep] = True
                    queue.append(dep)

        # Step 3: Union-find to group equivalent states
        def find(parent, x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(parent, rank, x, y):
            rootX = find(parent, x)
            rootY = find(parent, y)
            if rootX != rootY:
                if rank[rootX] < rank[rootY]:
                    parent[rootX] = rootY
                elif rank[rootX] > rank[rootY]:
                    parent[rootY] = rootX
                else:
                    parent[rootY] = rootX
                    rank[rootX] += 1

        parent = {s: s for s in clean_states}
        rank = {s: 0 for s in clean_states}
        for (s1, s2), mark_flag in marked.items():
            if not mark_flag:
                union(parent, rank, s1, s2)

        groups_dict = {}
        for s in clean_states:
            root = find(parent, s)
            groups_dict.setdefault(root, set()).add(s)
        groups = [sorted(list(g)) for g in groups_dict.values()]

        # Step 4: Build transition table for minimized DFA
        table_data.append(["State"] + symbols)
        transition_dict = {}
        minimized_final_states = []
        label_map = {}

        for group in groups:
            label = "[" + ", ".join(group) + "]"
            if any(s in final_states for s in group):
                label += "*"
                minimized_final_states.append(label)
            for s in group:
                label_map[s] = label
            transition_dict[label] = {}

        for group in groups:
            rep = group[0]
            label = label_map[rep]
            row = [label]
            for sym in symbols:
                tgt = transitions_raw.get(rep, {}).get(sym)
                if tgt:
                    tgt_clean = tgt.rstrip("*")
                    row.append(label_map.get(tgt_clean, "∅"))
                    transition_dict[label][sym] = label_map.get(tgt_clean, "∅")
                else:
                    row.append("∅")
                    transition_dict[label][sym] = "∅"
            table_data.append(row)

        result = f"✅ DFA with ID {fa_id} minimized successfully into {len(groups)} states."
        return result, table_data, transition_dict, minimized_final_states

    except Exception as e:
        return f"❌ Error: {e}", None, None, None
    finally:
        cursor.close()
        conn.close()
