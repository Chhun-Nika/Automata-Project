
CREATE DATABASE automata_db;
USE automata_db;

CREATE TABLE IF NOT EXISTS finiteAutomata (
	id INT PRIMARY KEY AUTO_INCREMENT,
	numberOfState INT,
	numberOfSymbol INT,
	symbol VARCHAR(100),
	state VARCHAR(100),
	transition VARCHAR(255),
	faType ENUM('DFA', 'NFA'),
	createdAt TIMESTAMP
);