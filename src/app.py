from flask import Flask, render_template, request, redirect, url_for
from db.dbConnection import get_connection
import json
from datetime import datetime
from functions.minimizeDFA import minimizeDFA
from functions.minimizeDFA import minimize_dfa_by_id
from functions.generate_diagram import generate_fa_diagram
from functions.generate_diagram import generate_minimized_dfa_diagram
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', current_year=datetime.now().year)

@app.route('/create', methods=['GET', 'POST'])
def create_fa():
    if request.method == 'POST':
        action = request.form.get('action')

        # Handle Design FA
        if action == 'design':
            return render_template('create_fa.html')

        # Handle Delete by ID
        elif action == 'delete':
            fa_id = request.form.get('fa_id')
            if not fa_id:
                return render_template('create_menu.html', message="⚠️ Please enter a valid ID to delete.")
            
            conn = get_connection()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM finiteAutomata WHERE id = %s", (fa_id,))
                        conn.commit()
                        return render_template('create_menu.html', message=f"FA with ID {fa_id} deleted successfully.")
                except Exception as e:
                    return render_template('create_menu.html', message=f"Error deleting FA: {e}")
                finally:
                    conn.close()
            else:
                return render_template('create_menu.html', message="Database connection failed.")

        # Back to home
        elif action == 'back':
            return redirect(url_for('home'))

        # Handle FA form submission
        elif action == 'submit_fa':
            fa_name = request.form.get('fa_name')
            num_states = int(request.form.get('num_states'))
            num_symbols = int(request.form.get('num_symbols'))
            symbols = [s.strip() for s in request.form.get('symbols').split(',') if s.strip()]
            final_states = [s.strip().upper() for s in request.form.get('final_states').split(',') if s.strip()]
            transitions = json.loads(request.form.get('transitions'))
            has_epsilon = request.form.get('has_epsilon')
            fa_type = 'DFA'

            if has_epsilon == 'y':
                symbols.append('ε')
                fa_type = 'NFA'

            for state_trans in transitions.values():
                for val in state_trans.values():
                    if ',' in val or val == '-':
                        fa_type = 'NFA'

            base_states = [chr(65 + i) for i in range(num_states)]
            display_states = [s + '*' if s in final_states else s for s in base_states]

            # Build updated transition dictionary with * for final states
            transition_with_star = {}
            for i, state in enumerate(base_states):
                label = state + '*' if state in final_states else state
                transition_with_star[label] = transitions[state]

            # Build displayable table
            display_table = []
            for state in base_states:
                label = state + '*' if state in final_states else state
                row = [label]
                for sym in symbols:
                    val = transitions[state].get(sym, '-')
                    row.append(val)
                display_table.append(row)

            # Save to DB
            conn = get_connection()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO finiteAutomata 
                            (faName, numberOfState, numberOfSymbol, symbol, state, finalStates, transition, faType, createdAt)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            fa_name, num_states, num_symbols,
                            json.dumps(symbols),
                            json.dumps(display_states),
                            json.dumps(final_states),
                            json.dumps(transition_with_star),
                            fa_type,
                            datetime.now()
                        ))
                        conn.commit()

                    # Generate FA diagram image
                    diagram_filename = generate_fa_diagram(
                        fa_name=fa_name,
                        transitions=transition_with_star,
                        final_states=final_states,
                        filename=fa_name.replace(" ", "_")
                    )
                    

                    return render_template(
                        'result.html',
                        fa_name=fa_name,
                        symbols=symbols,
                        table=display_table,
                        diagram_image=diagram_filename  # path to show the image in the template
                    )

                except Exception as e:
                    return render_template('create_fa.html', message=f"DB Save Error: {e}")
                finally:
                    conn.close()
            else:
                return render_template('create_fa.html', message="Cannot connect to database.")

    # Initial GET
    return render_template('create_menu.html')

test_history = []  # global list to hold session test history (cleared on refresh)

test_history = []

@app.route('/test', methods=['GET', 'POST'])
def test_input():
    global test_history
    result = None
    transition_data = None
    selected_fa_id = None
    fa_list = []

    conn = get_connection()
    if conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, faName FROM finiteAutomata")
            fa_list = cursor.fetchall()

    if request.method == 'POST':
        # Handle clear history
        if 'clear_history' in request.form:
            test_history = []
            result = "History cleared."
        else:
            fa_id = request.form.get('fa_id')
            selected_fa_id = fa_id
            input_string = request.form.get('input_string')

            if not fa_id:
                result = "Please select a Finite Automaton."
            else:
                conn = get_connection()
                if conn:
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT state, transition, symbol, faType FROM finiteAutomata WHERE id = %s", (fa_id,))
                            row = cursor.fetchone()
                            if not row:
                                result = f"FA with ID {fa_id} not found."
                            else:
                                states = json.loads(row[0])
                                transitions = json.loads(row[1])
                                symbols = json.loads(row[2])
                                fa_type = row[3]

                                table = []
                                for state in states:
                                    row_cells = [state]
                                    for sym in symbols:
                                        val = transitions.get(state, {}).get(sym, '∅')
                                        row_cells.append(val)
                                    table.append(row_cells)
                                transition_data = {
                                    "symbols": symbols,
                                    "rows": table
                                }

                                if input_string:
                                    from functions.testInputString import run_test_string
                                    result = run_test_string(input_string, states, symbols, transitions, fa_type)
                                    test_history.append({"input": input_string, "result": result})
                    except Exception as e:
                        result = f"Error: {e}"
                    finally:
                        conn.close()
                else:
                    result = "Cannot connect to the database."

    return render_template('test_input.html',
                           fa_list=fa_list,
                           result=result,
                           transition_data=transition_data,
                           selected_fa_id=selected_fa_id,
                           history=test_history)

@app.route('/check', methods=['GET', 'POST'])
def check_fa_type():
    result = None

    if request.method == 'POST':
        fa_id = request.form.get('fa_id')

        if not fa_id:
            result = "Please provide a valid FA ID."
        else:
            conn = get_connection()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT transition FROM finiteAutomata WHERE id = %s", (fa_id,))
                        row = cursor.fetchone()

                        if not row:
                            result = f"No FA found with ID {fa_id}."
                        else:
                            transition_data = json.loads(row[0])
                            is_nfa = False

                            for state, transitions in transition_data.items():
                                for symbol, next_state in transitions.items():
                                    if symbol.strip() == 'ε' or symbol.strip() == '-':
                                        is_nfa = True
                                        break

                                    # Check if it's a list or a comma-separated string
                                    if isinstance(next_state, list):
                                        if len(next_state) > 1:
                                            is_nfa = True
                                            break
                                    elif isinstance(next_state, str):
                                        if ',' in next_state or next_state.strip() == '-':
                                            is_nfa = True
                                            break

                                if is_nfa:
                                    break

                            result = "This is an **NFA**." if is_nfa else "🧠 This is a **DFA**."

                except Exception as e:
                    result = f"Error checking FA type: {str(e)}"
                finally:
                    conn.close()
            else:
                result = "Could not connect to the database."

    return render_template("check_type.html", result=result)

@app.route('/convert', methods=['GET', 'POST'])
def convert_fa():
    nfa_table = None
    dfa_table = None
    result = None

    if request.method == 'POST':
        fa_id = request.form.get('fa_id')
        if not fa_id:
            result = "Please provide a valid FA ID."
        else:
            from functions.convertNFAtoDFA import convert_nfa_to_dfa_web 
            nfa_table, dfa_table, result = convert_nfa_to_dfa_web(int(fa_id))

    return render_template("convert_fa.html", nfa_table=nfa_table, dfa_table=dfa_table, result=result)

@app.route('/minimize', methods=['GET', 'POST'])
def minimize_dfa():
    result = None
    minimized_table = None
    original_table = None
    image_path = None

    if request.method == 'POST':
        fa_id = request.form.get('fa_id')

        if not fa_id or not fa_id.isdigit():
            result = "Please provide a valid DFA ID."
        else:
            try:
                fa_id = int(fa_id)

                # Step 1: Get minimized DFA info
                result, table_data, transition_dict, final_states = minimize_dfa_by_id(fa_id)
                minimized_table = table_data


                # Step 2: Fetch original DFA for reference
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM finiteAutomata WHERE id = %s AND faType = %s", (fa_id, "DFA"))
                fa = cursor.fetchone()

                if fa:
                    symbols = json.loads(fa["symbol"])
                    states = json.loads(fa["state"])
                    transitions = json.loads(fa["transition"])

                    original_table = [["State"] + symbols]
                    for state in states:
                        row = [state]
                        for sym in symbols:
                            row.append(transitions.get(state, {}).get(sym, "∅"))
                        original_table.append(row)

                cursor.close()
                conn.close()

                # Step 3: Generate diagram
                if transition_dict:
                    filename = f"minimized_{fa_id}"
                    image_path = generate_minimized_dfa_diagram(
                        fa_name=filename,
                        transitions=transition_dict,
                        final_states=final_states,
                        filename=filename
                    )

            except Exception as e:
                result = f"Error minimizing DFA: {e}"

    return render_template(
        "minimize_dfa.html",
        result=result,
        table=minimized_table, 
        original_table=original_table,
        image_path=image_path
    )

if __name__ == '__main__':
    app.run(debug=True)