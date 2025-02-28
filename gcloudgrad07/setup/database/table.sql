DROP TABLE IF EXISTS robots CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Cria a tabela users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash TEXT NOT NULL
);

-- Cria a tabela robots
CREATE TABLE IF NOT EXISTS robots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    ip_address VARCHAR(256) NOT NULL,
    port INTEGER NOT NULL,
    robot_id VARCHAR(255) UNIQUE NOT NULL,
    robot_password TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    
    CONSTRAINT user_robot_fk 
        FOREIGN KEY (user_id) 
        REFERENCES users (id)
);