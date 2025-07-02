
def designFA ():
    print("\nDesign Finite Automata");
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
    
    

        


    