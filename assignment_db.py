import oracledb # type: ignore

def connect_to_db():
    print("Welcome to Oracle Metadata Explorer!")
    print("-----------------------------------")
    username = input("Enter username: ")
    password = input("Enter password: ")
    service_name = input("Enter service name (e.g. FREEPDB1): ")

    try:
        dsn = f"localhost:8521/{service_name}"
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        print("\n Connected successfully!\n")
        return conn
    except Exception as e:
        print("\n Connection failed:", e)
        return None


def show_main_menu():
    print("Select the object type you want to view:")
    print("1. Tables")
    print("2. Views")
    print("3. Sequences")
    print("4. Users")
    print("5. Exit")
    return input("Enter option number: ")


def list_objects(conn, object_type):
    cursor = conn.cursor()
    if object_type == "1":
        cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        title = "Tables"
    elif object_type == "2":
        cursor.execute("SELECT view_name FROM user_views ORDER BY view_name")
        title = "Views"
    elif object_type == "3":
        cursor.execute("SELECT sequence_name FROM user_sequences ORDER BY sequence_name")
        title = "Sequences"
    elif object_type == "4":
        cursor.execute("SELECT username FROM all_users ORDER BY username")
        title = "Users"
    else:
        return []

    objects = [r[0] for r in cursor.fetchall()]
    print(f"\nAvailable {title}:")
    for i, name in enumerate(objects, 1):
        print(f"{i}. {name}")

    cursor.close()
    return objects


def show_table_metadata(conn, table_name):
    while True:
        print(f"\nYou selected: {table_name}")
        print("Choose what to view about", table_name)
        print("1. Columns")
        print("2. Constraints")
        print("3. Indexes")
        print("4. Back to main menu")
        choice = input("Enter option number: ")

        cursor = conn.cursor()

        if choice == "1":
            print(f"\n--- Columns for {table_name} ---")
            cursor.execute("""
                SELECT column_name, data_type, nullable
                FROM user_tab_columns
                WHERE table_name = :tname
                ORDER BY column_id
            """, {"tname": table_name})
        elif choice == "2":
            print(f"\n--- Constraints for {table_name} ---")
            cursor.execute("""
                SELECT constraint_name, constraint_type
                FROM user_constraints
                WHERE table_name = :tname
            """, {"tname": table_name})
        elif choice == "3":
            print(f"\n--- Indexes for {table_name} ---")
            cursor.execute("""
                SELECT index_name
                FROM user_indexes
                WHERE table_name = :tname
            """, {"tname": table_name})
        elif choice == "4":
            cursor.close()
            break
        else:
            print("Invalid choice.")
            cursor.close()
            continue

        rows = cursor.fetchall()
        if not rows:
            print("No data found.")
        else:
            for r in rows:
                print(r[0] if len(r) == 1 else r)
        cursor.close()


def main():
    conn = connect_to_db()
    if not conn:
        return

    while True:
       
        option = show_main_menu()
        if option == "5":
            print("\nExiting Oracle Metadata Explorer. Goodbye!")
            break

        objects = list_objects(conn, option)
        if not objects:
            print("No objects found or invalid option.")
            continue

        try:
            obj_num = int(input("Select an object number: "))
            if obj_num < 1 or obj_num > len(objects):
                print("Invalid selection.")
                continue
            selected_object = objects[obj_num - 1]
        except ValueError:
            print("Invalid input.")
            continue

        if option == "1":
            show_table_metadata(conn, selected_object)
        else:
            print(f"\nYou selected: {selected_object}\n")

    conn.close()
    print("Database connection closed.")


if __name__ == "__main__":
    main()
