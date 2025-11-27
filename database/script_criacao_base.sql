-- RODE ESSE COMANDO PARA CRIAR A BASE QUE ESTAMOS TESTANDO

CREATE DATABASE hbr_demo_db;
USE hbr_demo_db;

CREATE TABLE tomografo (
	idExame INTEGER PRIMARY KEY AUTO_INCREMENT,
    nomePaciente VARCHAR(150),
    idade SMALLINT,
    resultados VARCHAR(150)
);
