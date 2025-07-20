import graphviz
import os

def generate_fa_diagram(fa_name, transitions, final_states, filename):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR')

    # Normalize states to strip any * and keep unique ones
    all_states = set()
    for state in transitions:
        clean_state = state.rstrip('*')
        all_states.add(clean_state)

    # Draw states (only once per state)
    for state in all_states:
        is_final = state in final_states
        dot.node(state, shape='doublecircle' if is_final else 'circle')

    # Draw transitions (normalize both from and to states)
    for from_state, trans in transitions.items():
        from_clean = from_state.rstrip('*')
        for symbol, to_state in trans.items():
            targets = to_state.split(',') if isinstance(to_state, str) and ',' in to_state else [to_state]
            for tgt in targets:
                tgt_clean = tgt.rstrip('*') if isinstance(tgt, str) else tgt
                if tgt_clean and tgt_clean != '-':
                    dot.edge(from_clean, tgt_clean, label=symbol)

    # Output to static/diagrams folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, '..', 'static', 'diagrams')
    os.makedirs(STATIC_DIR, exist_ok=True)

    output_path = os.path.abspath(STATIC_DIR)
    dot.render(filename=filename, directory=output_path, cleanup=True)

    return filename + '.png'  # Return filename for use in templates

def generate_minimized_dfa_diagram(fa_name, transitions, final_states, filename):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR')

    # Ensure state names are consistent with transition keys (e.g., [A, B]*)
    all_states = set(transitions.keys())
    for trans in transitions.values():
        for target in trans.values():
            if target and target != '∅':
                all_states.add(target)

    # Add nodes (preserve brackets and asterisks)
    for state in all_states:
        is_final = state in final_states
        dot.node(state, shape='doublecircle' if is_final else 'circle')

    # Add edges
    for from_state, trans in transitions.items():
        for symbol, to_state in trans.items():
            if to_state and to_state != '∅':
                dot.edge(from_state, to_state, label=symbol)

    # Ensure output directory exists
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, '..', 'static', 'diagrams', 'minimize')
    os.makedirs(STATIC_DIR, exist_ok=True)

    output_path = os.path.abspath(STATIC_DIR)
    dot.render(filename=filename, directory=output_path, cleanup=True)

    return f'diagrams/minimize/{filename}.png'