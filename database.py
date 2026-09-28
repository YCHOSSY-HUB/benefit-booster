import mysql.connector

from config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(

        host=DB_HOST,

        port=DB_PORT,

        user=DB_USER,

        password=DB_PASSWORD,

        database=DB_NAME

    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_database():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        # =================================================
        # CREATE TABLE JIKA BELUM ADA
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booster_roles (

                id INT AUTO_INCREMENT PRIMARY KEY,

                guild_id BIGINT NOT NULL,

                user_id BIGINT NOT NULL,

                role_id BIGINT NOT NULL,

                role_name VARCHAR(255) NOT NULL,

                color_1 VARCHAR(255),

                color_2 VARCHAR(255),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE KEY unique_user_role (
                    guild_id,
                    user_id
                ),

                UNIQUE KEY unique_role (
                    guild_id,
                    role_id
                )

            )
        """)


        connection.commit()


        # =================================================
        # CEK KOLOM LAMA
        # =================================================

        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'booster_roles'
        """, (DB_NAME,))


        existing_columns = {

            row[0]

            for row in cursor.fetchall()

        }


        # =================================================
        # TAMBAHKAN ROLE_NAME JIKA BELUM ADA
        # =================================================

        if "role_name" not in existing_columns:

            print(
                "🔧 Menambahkan kolom role_name..."
            )

            cursor.execute("""
                ALTER TABLE booster_roles
                ADD COLUMN role_name VARCHAR(255) NOT NULL DEFAULT ''
            """)


        # =================================================
        # TAMBAHKAN COLOR_1
        # =================================================

        if "color_1" not in existing_columns:

            print(
                "🔧 Menambahkan kolom color_1..."
            )

            cursor.execute("""
                ALTER TABLE booster_roles
                ADD COLUMN color_1 VARCHAR(255) NULL
            """)


        # =================================================
        # TAMBAHKAN COLOR_2
        # =================================================

        if "color_2" not in existing_columns:

            print(
                "🔧 Menambahkan kolom color_2..."
            )

            cursor.execute("""
                ALTER TABLE booster_roles
                ADD COLUMN color_2 VARCHAR(255) NULL
            """)


        connection.commit()


        print(
            "✅ Database booster_roles siap."
        )


    except mysql.connector.Error as error:

        print(
            f"❌ Database Error: {error}"
        )

        raise


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# =========================================================
# GET BOOSTER ROLE
# =========================================================

def get_booster_role(

    guild_id: int,

    user_id: int

):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT
                id,
                guild_id,
                user_id,
                role_id,
                role_name,
                color_1,
                color_2,
                created_at

            FROM booster_roles

            WHERE guild_id = %s

            AND user_id = %s

            LIMIT 1
        """, (

            guild_id,

            user_id

        ))


        return cursor.fetchone()


    except mysql.connector.Error as error:

        print(
            f"❌ Get Booster Role Error: {error}"
        )

        return None


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# =========================================================
# SAVE BOOSTER ROLE
# =========================================================

def save_booster_role(

    guild_id: int,

    user_id: int,

    role_id: int,

    role_name: str = "",

    color_1: str = None,

    color_2: str = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute("""
            INSERT INTO booster_roles
            (
                guild_id,
                user_id,
                role_id,
                role_name,
                color_1,
                color_2
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

            ON DUPLICATE KEY UPDATE

                role_id = VALUES(role_id),

                role_name = VALUES(role_name),

                color_1 = VALUES(color_1),

                color_2 = VALUES(color_2)

        """, (

            guild_id,

            user_id,

            role_id,

            role_name,

            color_1,

            color_2

        ))


        connection.commit()


        print(
            f"✅ Booster role tersimpan: "
            f"{role_name} | {role_id}"
        )


        return True


    except mysql.connector.Error as error:

        print(
            f"❌ Save Booster Role Error: {error}"
        )

        return False


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# =========================================================
# DELETE BOOSTER ROLE
# =========================================================

def delete_booster_role(

    guild_id: int,

    user_id: int

):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute("""
            DELETE FROM booster_roles

            WHERE guild_id = %s

            AND user_id = %s
        """, (

            guild_id,

            user_id

        ))


        connection.commit()


        print(
            f"🗑️ Booster role dihapus dari database: "
            f"{user_id}"
        )


        return True


    except mysql.connector.Error as error:

        print(
            f"❌ Delete Booster Role Error: {error}"
        )

        return False


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()