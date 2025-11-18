import argparse
import mysql.connector
import json
import streamlit as st
import pandas as pd
from mysql.connector import errorcode
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Demo HBr - CIIA")

def init_db(user='root', password='pass123', host='127.0.0.3', database='hbr_demo_db'):
    # Tenta a conexão
    try:
        connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('ACESSO NEGADO: user ou senha incorreto(a).')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('A base de dados não existe.')
        else:
            print(err)
    else:
        # Caso dê certo, criamos o cursor e realizamos a query
        
        cursor = connection.cursor()

        query = cursor.execute("""
                               CREATE TABLE IF NOT EXISTS tomografo (
                                idExame INT PRIMARY KEY AUTO_INCREMENT,
                                nomePaciente VARCHAR(100),
                                idade INT,
                                resultados VARCHAR(100)
                                )
                               """
                                )
        connection.commit()

        return connection, cursor

@mcp.tool()
def add_data(query: str) -> bool:
    """Adiciona novos dados à tabela do tomógrafo usando uma consulta SQL INSERT.

    Argumentos:
        query (str): query SQL INSERT seguindo o seguinte formato:
            INSERT INTO tomografo (nomePaciente, idade, resultados)
            VALUES ('João Silva', 45, 'Glaucoma')
        
    Esquema:
        - nomePaciente: campo de texto (exigido)
        - idade: campo de inteiro (exigido)
        - resultados: campo de texto (exigido)
        Observação: O campo 'idExame' é gerado automaticamente.
    
    Retorno:
        bool: True se os dados foram inseridos corretamente, False caso contrário
    
    Exemplo:
        >>> query = '''
        ... INSERT INTO tomografo (nomePaciente, idade, resultados)
        ... VALUES ('Alice Guerra', 25, 'Retinopatia diabética')
        ... '''
        >>> add_data(query)
        True
    """

    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erro ao inserir dados: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM tomografo") -> list:
    """Lê dados da tabela tomografo usando uma query SQL SELECT.

    Argumentos:
        query (str, optional): SQL SELECT query. O comportamento default é: "SELECT * FROM tomografo;".
            Exemplos:
            - "SELECT * FROM tomografo"
            - "SELECT nomePaciente, idade FROM tomografo WHERE idade > 25"
            - "SELECT * FROM tomografo ORDER BY idade DESC"
    
    Retorna:
        list: Uma lista de tuplas contento os resultados da query.
              Para uma query default, o formato da tupla é (idExame, nomePaciente, idade, resultados)
              
    
    Exemplo:
        >>> # Leia todos os registros
        >>> read_data()
        [(1, 'João Silva', 45, 'Glaucoma'), (2, 'Alice Guerra', 25, 'Retinopatia diabética')]
        
        >>> # Leia com uma query específica
        >>> read_data("SELECT nomePaciente, resultados FROM tomografo WHERE idade < 30")
        [('João Silva', 'Glaucoma')]
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return json.dumps(results, ensure_ascii=False, indent=2)
    except mysql.connector.Error as e:
        print(f"Erro ao ler dados: {e}")
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

@mcp.tool()
def erase_data(query: str) -> bool:
    """Remove registros da tabela tomografo usando uma query SQL SELECT.

    Argumentos:
        query (str, opcional): SQL DELETE query. 
            Exemplos:
            - "DELETE FROM tomografo WHERE nomePaciente=\"Alice Guerra\""
            - "DELETE FROM tomografo WHERE idade > 25"
    
    Retorna:
        bool: True se os dados foram inseridos corretamente, False caso contrário
              
    
    Exemplo:
        >>> # Apague o registro do paciente João Silva, de 45 anos.
        >>> query = '''
        ... DELETE FROM tomografo
        ... WHERE nomePaciente="João Silva" AND idade=45;
        ... '''
        >>> erase_data(query)
        True
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erro ao remover dados: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM tomografo") -> list:
    """Lê dados da tabela tomografo usando uma query SQL SELECT.

    Argumentos:
        query (str, optional): SQL SELECT query. O comportamento default é: "SELECT * FROM tomografo;".
            Exemplos:
            - "SELECT * FROM tomografo"
            - "SELECT nomePaciente, idade FROM tomografo WHERE idade > 25"
            - "SELECT * FROM tomografo ORDER BY idade DESC"
    
    Retorna:
        list: Uma lista de tuplas contento os resultados da query.
              Para uma query default, o formato da tupla é (idExame, nomePaciente, idade, resultados)
              
    
    Exemplo:
        >>> # Leia todos os registros
        >>> read_data()
        [(1, 'João Silva', 45, 'Glaucoma'), (2, 'Alice Guerra', 25, 'Retinopatia diabética')]
        
        >>> # Leia com uma query específica
        >>> read_data("SELECT nomePaciente, resultados FROM tomografo WHERE idade < 30")
        [('João Silva', 'Glaucoma')]
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return json.dumps(results, ensure_ascii=False, indent=2)
    except mysql.connector.Error as e:
        print(f"Erro ao ler dados: {e}")
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

@mcp.tool()
def update_data(query: str) -> dict:
    """Atualiza dados na tabela tomografo usando uma query SQL UPDATE.

    Argumentos:
        query (str): SQL UPDATE query.
            Exemplos:
            - "UPDATE tomografo SET idade = 32 WHERE nomePaciente = 'Ana Beatriz'"
            - "UPDATE tomografo SET resultados = 'Sem anomalias' WHERE idExame = 5"
            - "UPDATE tomografo SET idade = 28, resultados = 'Normal' WHERE nomePaciente = 'Carlos Mendes'"

    Retorna:
        dict: Um dicionário com o status da operação e o número de linhas afetadas.
    
    Exemplo:
        >>> update_data("UPDATE tomografo SET idade = 32 WHERE nomePaciente = 'Ana Beatriz'")
        {"status": "sucesso", "linhas_afetadas": 1}
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return {"status": "sucesso", "linhas_afetadas": cursor.rowcount}
    except mysql.connector.Error as e:
        print(f"Erro ao atualizar dados: {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

@mcp.tool()
def create_bar_chart(x: list, y:list, x_label: str, y_label:str) -> str:
    """Cria tudo o que é necessário para criar um gráfico de barras simples usando o método bar_chart da biblioteca Streamlit.

    Argumentos:
        x (list): uma lista de valores categóricos ou numéricos a serem colocados no eixo x, como ["Fulano", "Ciclano", "Beltrano"] ou [10, 20, 30].
        y (list): uma lista de valores numéricos a serem colocados no eixo y, como [10, 20, 30].
        x_label (str): uma string que será o rótulo do eixo x, como "Pacientes".
        y_label (str): uma string que será o rótulo do eixo y, como "Valor em mg".

    
    Retorna:
        str: JSON contendo os dados necessários para gerar o gráfico no Streamlit.
    """
    try:
        df = pd.DataFrame(data={x_label: x, y_label: y})
        chart_data = {
            "type": "bar_chart",
            "x": x,
            "y": y,
            "x_label": x_label,
            "y_label": y_label,
        }
        return json.dumps(chart_data, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        return json.dumps({"error": str(e)})



print("Iniciando servidor...")

# Modo Debug
# uv run mcp dev server.py

# Modo Produção
# uv run server.py --server_type=sse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--server_type", type=str, default="sse", choices=["sse", "stdio"]
)

args = parser.parse_args()
mcp.run(args.server_type)