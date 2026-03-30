CREATE DATABASE [tic_tac_toe_users_db];

USE [tic_tac_toe_users_db];


CREATE TABLE users (
    [Id] INT IDENTITY PRIMARY KEY,
    [Login] NVARCHAR(50) NOT NULL UNIQUE,
    [Password_hash] NVARCHAR(64) NOT NULL,
    [Name] NVARCHAR(100),
    [Image] NVARCHAR(255)
);


INSERT INTO users (Login, Password_hash, Name, Image) VALUES
('ukr', 'f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae', 'UA', 'ukr_UA.png'),
('rus', '9b871512327c09ce91dd649b3f96a63b7408ef267c8cc5710114e629730cb61f', 'RU', 'rus_RU.png'),
('aaa', 'f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae', 'AAA', 'aaa_AAA.png'),
('bbb', '9b871512327c09ce91dd649b3f96a63b7408ef267c8cc5710114e629730cb61f', 'BBB', 'bbb_BBB.png');

SELECT * FROM users;