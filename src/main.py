import os;
from functions import designFA, testInputString, checkFAType, convertNFAtoDFA, minimizeDFA;


# Function to clear the console screen
# this function works on Windows and other OS
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear');


while True:
    clear_screen();
    print("========== MENU ==========\n");
    print("1. Desing Finite Automata");
    print("2. Test input String");
    print("3. Check FA Type");
    print("4. Convert NFA to DFA");
    print("5. Minimize DFA");
    print("0. Exit\n");
    print("==========================\n");
    choice = input("Enter your choice: ");
    if choice == '0':
        print("Exiting the program.");
        break;
    elif choice == '1':
        clear_screen();
        designFA.designFA();
        input("Press Enter to exit...")

