from datetime import datetime
import json
from db.dbConnection import get_connection



def designFA ():
    print("\n===== Design Finite Automata =====");
    typeOfFA = 'DFA';

    # check if number of states is greater than 0
    while True:
        try:
            num_states = int(input("\nEnter the number of states: "));
            if num_states > 0:
                break;
            print("Number of states must be greater than 0. Please try again.");
        except ValueError:
            print("Invalid input. Please enter a valid integer for the number of states."); 
    
    # check if number of symbols is greater than 0
    while True:
        try:
            num_symbols = int(input("Enter the number of input symbols: "));
            if num_states > 0:
                break;
            print("Number of symbols must be greater than 0. Please try again.");
        except ValueError:
            print("Invalid input. Please enter a valid integer for the number of symbols.");
    

    # Initialize the list to hold all symbols
    symbols = [];
    for i in range(num_symbols):
        symbol = input(f"\t- Enter symbol {i+1}: ");
        symbols.append(symbol);

    # Initialize the list to hold all states
    all_states = [];
    initial_value = 65;
    for i in range(num_states):
        all_states.append(chr(initial_value));
        initial_value += 1;
    # Copy the original states to a new list for later use
    copy_all_states = all_states.copy();
    
    print("\nCurrent States and Symbols:");
    print ("\t- Symbols: ", symbols);
    print ("\t- State: ", all_states);


    
    while True:
        try:
            num_final_states = int(input("Enter the number of final states: "));  
            if num_final_states > 0 and num_final_states <= num_states:
                break;
            print("Number of final states must be greater than 0 and less than or equal to the number of states. Please try again.");
        except ValueError:
            print("Invalid input. Please enter a valid integer for the number of final states.");

    for i in range(num_final_states):    
            # Check if the final state is valid
            while True:
                final_state = input(f"\t- Enter final state {i+1}: ");
                if final_state not in all_states:
                    print(f"State {final_state} is not a valid state. Please try again.");
                else:
                    break;
            for j in range(len(all_states)):
                if all_states[j] == final_state:
                    all_states[j] = final_state + "*"; 
  
    elsilon = input("Does your FA have an elsilon transition? (y/n): ");
    print(all_states)

    if elsilon.lower() == 'y':
        symbols.append('ε');  # Add epsilon transition symbol if exists
        typeOfFA = 'NFA';  # Change type to NFA if epsilon transition exists
    
    # Input the transition table
    transition_table = [];
    print("\nEnter the transition:");
    print("\t *** if there are two transitions for a state and symbol, separate them with a comma (e.g., A,B) ***");
    print("\t *** if there is no transition for a state and symbol, enter '-' ***");

    for state in copy_all_states:
        row = [];
        for symbol in symbols:
            while True:
                transition_input = input(f"\t- Transition for state {state} with symbol '{symbol}': ");
                if transition_input == '-':
                    typeOfFA = 'NFA';
                    transitions = ['-']
                    row.append('-');
                    break;
                elif ',' in transition_input:
                    transitions = transition_input.split(',');
                    if len(transitions) > 1:
                        typeOfFA = 'NFA';
                    for t in transitions:
                        if t not in copy_all_states:
                            print(f"State {t} is not a valid state. Please try again.");
                            break;
                        else:
                            row.append(transitions);
                            break;
                elif transition_input in copy_all_states:
                    row.append(transition_input);
                break;
                
        transition_table.append(row);
    print (transition_table);

    # display as table
    from prettytable import PrettyTable;
    table = PrettyTable();
    table.field_names = ["States"] + symbols;
    for i in range(len(all_states)):
        table.add_row([all_states[i]] + transition_table[i]);
    print("\nTransition Table:");
    print(table);
    print("\nType of Finite Automata: ", typeOfFA);

    # input name of FA
    NameOfFA = input("Enter a name for your Finite Automaton: ");

    save_confirm = input(f"Do you want to save the FA '{NameOfFA}' to the database? (y/n): ").lower()
    if save_confirm != 'y':
        print("FA not saved.")
        return 
    
    
    
    # Build transitions dict
    transition_dict = {}

    for i, state in enumerate(copy_all_states):
        state_transitions = {}
        for j, symbol in enumerate(symbols):
            transition = transition_table[i][j]
            if isinstance(transition, list):
                # Multiple transitions (NFA)
                state_transitions[symbol] = transition
            else:
                state_transitions[symbol] = transition
        transition_dict[state] = state_transitions

    # convert to json string 
    json_symbols = json.dumps(symbols);
    json_states = json.dumps(all_states);
    json_transition = json.dumps(transition_dict);

    # save to database 
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try: 
            cursor.execute ("""
                INSERT INTO finiteAutomata (faName, numberOfState , numberOfSymbol , symbol, state, transition, faType, createdAt)
                            VALUES (%s, %s , %s, %s, %s, %s, %s, %s)""", (
                                NameOfFA,
                                num_states,
                                num_symbols,
                                json_symbols,
                                json_states,
                                json_transition,
                                typeOfFA,
                                datetime.now()
                            ))
            conn.commit()
            print("FA save to the Database");
        
            while True:
                print("*** if you want to design more FA enter y, otherwise enter n ***")
                choice = input("\nDo you want to design another Finite Automaton? (y/n): ").strip().lower()
                if choice == 'y':
                    designFA()  # call again
                    break
                elif choice == 'n':
                    print("Done. Thank you for designing Finite Automata!")
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
        except Exception as e:
            print("Error! cannot save FA to the Database", e);
        finally:
            cursor.close()
            conn.close()
        
    else: 
        print("Couldn't connect to the database.")
