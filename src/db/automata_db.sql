CREATE DATABASE automata_db;
USE automata_db;

CREATE TABLE IF NOT EXISTS finiteAutomata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    faName VARCHAR(100) NOT NULL,         -- FA name
    numberOfState INT,
    numberOfSymbol INT,
    symbol VARCHAR(255),
    state VARCHAR(255),
    finalStates VARCHAR(255),             -- Final states
    transition TEXT,
    faType ENUM('DFA', 'NFA'),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from finiteAutomata;