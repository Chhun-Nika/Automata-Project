# Automata-Project

## Introduction

This project implements a Finite Automata simulator with a graphical user interface (GUI). It allows users to design both Deterministic (DFA) and Nondeterministic Finite Automata (NFA), simulate input strings, convert NFAs to DFAs, minimize DFAs, and save automata data using a database. The project demonstrates practical applications of automata theory in programming.

## How to Run the Project

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Chhun-Nika/Automata-Project
cd Automata-Project
```

### 2. Set up Environment Variables

```bash
cp .env.example .env
```
Example of .env format 

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=hms_db
```

### 3. Install Dependencies

Install Graphviz (required for visualization):
```bash
brew install graphviz
```

Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

```bash
pip install mysql-connector-python Flask PyMySQL prettytable graphviz python-dotenv
```

### 4. Run the Project
Run with the app.py
```bash
python app.py
```
The server will start, and you can access the application through your web browser.

