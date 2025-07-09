# from db.dbConnection import get_connection
# import json
# from prettytable import PrettyTable

# def testInputStringById():
#     print("\n===== Test Input String from MySQL by ID =====")

#     try:
#         fa_id = int(input("Enter FA ID to test: "))
#     except ValueError:
#         print("Invalid ID.")
#         return

#     # Connect to DB
#     conn = get_connection()
#     if conn is None:
#         print("❌ Database connection failed.")
#         return
#     cursor = conn.cursor(dictionary=True)

#     try:
#         cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s", (fa_id,))
#         fa = cursor.fetchone()

#         if not fa:
#             print(f"No FA found with ID {fa_id}")
#             return

#         # Parse fields
#         symbols = fa['symbol'].split(',')
#         raw_states = fa['state'].split(',')
#         transition_data = json.loads(fa['transition'])
#         fa_type = fa['faType']

#         # Final & cleaned states
#         final_states = [s.replace('*', '') for s in raw_states if '*' in s]
#         states = [s.replace('*', '') for s in raw_states]

#         # Display Transition Table
#         table = PrettyTable()
#         table.field_names = ["State"] + symbols
#         for state in states:
#             row = []
#             for sym in symbols:
#                 trans = transition_data.get(state, {}).get(sym, '-')
#                 if isinstance(trans, list):
#                     row.append(",".join(trans))
#                 else:
#                     row.append(trans)
#             row_label = state + "*" if state in final_states else state
#             table.add_row([row_label] + row)

#         print("\n🧾 Transition Table:")
#         print(table)
#         print(f"\nFA Type: {fa_type}")
#         print(f"Start State: {states[0]}")
#         print(f"Final States: {final_states}")

#         # Start loop for input strings
#         while True:
#             input_str = input("\nEnter input string to test (or 'k' to stop): ").strip()
#             if input_str.lower() == 'k':
#                 print("🛑 Stopped input testing.")
#                 break

#             current_state = states[0]
#             valid = True

#             for ch in input_str:
#                 if ch not in symbols:
#                     print(f"❌ Invalid symbol '{ch}' — not in FA alphabet.")
#                     valid = False
#                     break

#                 next_state = transition_data.get(current_state, {}).get(ch)

#                 if not next_state or next_state == '-':
#                     print(f"❌ No transition from {current_state} on symbol '{ch}'")
#                     valid = False
#                     break

#                 # NFA — pick first path only
#                 if isinstance(next_state, list):
#                     current_state = next_state[0]
#                 else:
#                     current_state = next_state

#             if valid:
#                 if current_state in final_states:
#                     print("✅ Input Accepted!")
#                 else:
#                     print("❌ Input Rejected — not in final state.")

#     except Exception as e:
#         print(f"❌ Error during test: {e}")
#     finally:
#         cursor.close()
#         conn.close()


import json
from db.dbConnection import get_connection
from prettytable import PrettyTable

def testInputStringById():
    print("\n===== Test Input String =====");

    print("\n*** Here are the Finite Automata in your current database ***\n");
    
    # test the connect to the database
    conn = get_connection();
    if not conn:
        print("Could not connect to the Database!");
        return
    cursor = conn.cursor(dictionary=True)
    try: 
        cursor.execute("SELECT * FROM finiteAutomata");
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
    
        print("\n*** In order to Test input String, you have to select one Finite Automata by ID ***\n");
    
        # enter fa's id
        selectID = int(input("Enter the ID of Finite Automata: "));
    
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
            print("\nTransition Table\n");
            print(table1);
            print("Noted! State With * is Final State");
        
        # parse the data into string
        states =  json.loads(fa["state"])
        symbols =  json.loads(fa["symbol"])
        transitionData =  json.loads(fa["transition"])

        # Clean states & identify final states
        final_states = [s.replace('*', '') for s in states if '*' in s]
        states = [s.replace('*', '') for s in states]
        
        # Start loop for input strings
        while True:
            input_str = input("\nEnter input string to test (or 'n' to stop): ").strip()
            if input_str.lower() == 'n':
                print("\n*** Stopped input string for testing. ***")
                break

            current_state = states[0]
            valid = True

            for ch in input_str:
                if ch not in symbols:
                    print(f"\n*** Invalid symbol '{ch}', this symbol is not in FA alphabet. ***\n")
                    valid = False
                    break

                next_state = transitionData.get(current_state, {}).get(ch)

                if not next_state or next_state == '-':
                    print(f" No transition from {current_state} on symbol '{ch}'")
                    valid = False
                    break

                # NFA — pick first path only
                if isinstance(next_state, list):
                    current_state = next_state[0]
                else:
                    current_state = next_state

            if valid:
                if current_state in final_states:
                    print("\n*** Aww... Input Accepted ***")
                else:
                    print("\n*** Sorry ! Input not Accepted ***")


    except Exception as e:
        print("Error! Loading Finite Automata Data", e);
    finally:
        cursor.close()
        conn.close()
        