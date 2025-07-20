import json 
from db.dbConnection import get_connection
from prettytable import PrettyTable

def checkFAType():
    print("\n===== Checking Finite Automata Type =====\n")

    print("\n*** Here are the Finite Automata in your current database ***")

    # test the connect to the database 
    conn = get_connection()
    if not conn:
        print("Could not connect to the Database!")
        return 
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM finiteAutomata")
        fas = cursor.fetchall()

        if not fas:
            print("Not Finits Automata Found.")
        
        # create pretty table 
        table = PrettyTable()
        table.field_names = [
            "ID", "FAName", "NumbeOfState", "NumberOfSymbol", "Symbol", "State", "Transition", "CreatedAt"
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
                fa["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            ])

        print(table);
    
        print("\n*** Select one Finite Automata that u want to know its type (DFA or NFA) by input ID ***")
       
        # enter fa's id
        selectID = int(input("\nEnter the ID of Finite Automata: "))
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
        print("Noted! State With * is Final State\n");

        transitionData = json.loads(fa["transition"]);
        
        def define_TypeFA(transitionData):
            for state, transitions in transitionData.items():
                for symbol, next_state in transitions.items():  
                    if symbol == 'ε' or symbol == '-':
                        return 'NFA'
                    if isinstance(next_state, list) and len(next_state) > 1:
                        return 'NFA'
            return 'DFA'
        faType = define_TypeFA(transitionData)
        print("Your FA's Type is ", faType)
    
    except Exception as e:
        print("Error While Loading FA from Database.", e)
    finally:
        cursor.close()
        conn.close()
