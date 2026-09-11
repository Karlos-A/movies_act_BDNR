from cassandra.cluster import Cluster
import uuid
# ==============================
# CQL Statements
# ==============================
CREATE_KEYSPACE = """
    CREATE KEYSPACE IF NOT EXISTS movie_db WITH REPLICATION =
    {'class': 'SimpleStrategy', 'replication_factor': 1};
"""

CREATE_TABLE_MOVIE_BY_TITLE = """
    CREATE TABLE IF NOT EXISTS movies.movie_by_title (
        movie_id UUID,
        title TEXT,
        release_year INT,
        genre TEXT,
        rating FLOAT,
        director TEXT,
        PRIMARY KEY ((title), release_year)
    );
"""

CREATE_TABLE_MOVIE_BY_GENRE = """
    CREATE TABLE IF NOT EXISTS movies.movie_by_genre (
        movie_id UUID,
        title TEXT,
        release_year INT,
        genre TEXT,
        rating FLOAT,
        director TEXT,
        PRIMARY KEY ((genre), rating, movie_id)
        ) WITH CLUSTERING ORDER BY (rating DESC, movie_id ASC);
"""
INSERT_MOVIE_TITLE = """
    INSERT INTO movies.movie_by_title (movie_id, title, release_year, genre, rating, director)
        VALUES (%s, %s, %s, %s, %s, %s)
"""
INSERT_MOVIE_GENRE = """
    INSERT INTO movies.movie_by_genre (movie_id, title, release_year, genre, rating, director)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
DELETE_MOVIE_TITLE = """
    DELETE FROM movies.movie_by_title WHERE title = %s AND release_year = %s
"""
DELETE_MOVIE_GENRE = """
    DELETE FROM movies.movie_by_genre WHERE genre = %s AND rating = %s AND movie_id = %s
"""
SELECT_BY_TITLE = """
    SELECT * FROM movies.movie_by_title WHERE title = %s AND release_year = %s
"""
SELECT_BY_GENRE = """
    SELECT * FROM movies.movie_by_genre WHERE genre = %s
"""
UPDATE_DIRECTOR = """
    UPDATE movies.movie_by_title SET director = %s WHERE title = %s AND release_year = %s
"""
UPDATE_MOVIE_TITLE = """
    UPDATE movies.movie_by_title SET director = %s WHERE title = %s AND release_year = %s
"""
UPDATE_MOVIE_GENRE = """
    UPDATE movies.movie_by_genre SET director = %s WHERE genre = %s AND rating = %s AND movie_id = %s
"""
# ==============================
# Funciones base
# ==============================
def create_keyspace_and_tables(session):
    try:
        session.execute(CREATE_KEYSPACE)
        session.set_keyspace('movie_db')
        session.execute(CREATE_TABLE_MOVIE_BY_TITLE)
        session.execute(CREATE_TABLE_MOVIE_BY_GENRE)
        print("Keyspace y tablas creadas correctamente.")
    except Exception as e:
        print(f"Error al crear keyspace o tablas: {e}")

def insert_movie(session, title, year, director, genre, rating):
    try:
        movie_id = uuid.uuid4()
        session.execute(INSERT_MOVIE_TITLE, (movie_id, title, year, genre, rating, director))
        session.execute(INSERT_MOVIE_GENRE, (movie_id, title, year, genre, rating, director))
        print("Película insertada correctamente.")
    except Exception as e:
        print(f"Error al insertar película: {e}")

def query_by_title(session, title, year):
    try:
        rows = session.execute(SELECT_BY_TITLE, (title, year))
        found = False
        print(f"Resultados para título '{title}' y año '{year}':")
        for row in rows:
            found = True
            print(f"Título: {row.title}")
            print(f"Año: {row.release_year}")
            print(f"Director: {row.director}")
            print(f"Género: {row.genre}")
            print(f"Rating: {row.rating:.1f}")
        if not found:
            print("No se encontraron resultados.")
    except Exception as e:
        print(f"Error al consultar por título: {e}")

def query_by_genre(session, genre):
    try:
        rows = session.execute(SELECT_BY_GENRE, (genre,)) #La coma es para que sea una tupla de un solo elemento
        found = False
        print(f"Resultados para género '{genre}':")
        for row in rows:
            found = True
            print("")
            print(f"Título: {row.title}")
            print(f"Año: {row.release_year}")
            print(f"Director: {row.director}")
            print(f"Género: {row.genre}")
            print(f"Rating: {row.rating:.1f}")
        if not found:
            print("No se encontraron resultados.")
    except Exception as e:
        print(f"Error al consultar por género: {e}")

def update_movie_director(session, title, year, genre, new_director):
    try:
        rows = session.execute(SELECT_BY_TITLE, (title, year))
        movie = rows.one()
        if movie:
            session.execute(UPDATE_MOVIE_TITLE, (new_director, title, year))
            session.execute(UPDATE_MOVIE_GENRE, (new_director, genre, movie.rating, movie.movie_id))
            print("Director actualizado en las tablas.")
        else:
            print("Película no encontrada.")
    except Exception as e:
        print(f"Error al actualizar director: {e}")
        

def delete_movie(session, title, genre, rating, release_year):
    try:
        rows = session.execute(SELECT_BY_TITLE, (title, release_year))
        movie = rows.one()
        if movie:
            session.execute(DELETE_MOVIE_TITLE, (title, release_year))
            session.execute(DELETE_MOVIE_GENRE, (genre, rating, movie.movie_id))
            print("Película eliminada de las tablas.")
        else:
            print("Película no encontrada.")
    except Exception as e:
        print(f"Error al eliminar película: {e}")
# ==============================
# Menú
# ==============================
def main():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    create_keyspace_and_tables(session)

    while True:
        print("\n=== Movie Database Menu ===")
        print("1. Insertar película")
        print("2. Consultar por título")
        print("3. Consultar por género")
        print("4. Actualizar director")
        print("5. Eliminar película")
        print("0. Salir")
        choice = input("Seleccione opción: ")

        if choice == "1":
            title = input("Título: ")
            year = int(input("Año: "))
            director = input("Director: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            insert_movie(session, title, year, director, genre, rating)
        elif choice == "2":
            title = input("Título: ")
            year = int(input("Año: "))
            query_by_title(session, title, year)
        elif choice == "3":
            genre = input("Género: ")
            query_by_genre(session, genre)
        elif choice == "4":
            title = input("Título: ")
            year = int(input("Año: "))
            genre = input("Género: ")
            new_director = input("Nuevo Director: ")
            update_movie_director(session, title, year, genre, new_director)
        elif choice == "5":
            title = input("Título: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            release_year = int(input("Año: "))
            delete_movie(session, title, genre, rating, release_year)
        elif choice == '0':
            # Cerrar conexión y salir
            cluster.shutdown()
            break
        else:
            print("Opción inválida")
            break

if __name__ == "__main__":
    main()