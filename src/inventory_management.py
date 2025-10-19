import mysql.connector
from mysql.connector import Error
import sys
from pathlib import Path

roles = {
    "Manufacturer": [
        "Define/Update Product",
        "Define/Update Product BOM",
        "Record Ingredient Receipt",
        "Create Product Batch",
        "Reports: On-hand | Nearly-out-of-stock | Almost-expired",
        "(Grad) Recall/Traceability"
    ],
    "Supplier": [
        "Declare Ingredients Supplied",
        "Maintain Formulations (materials, price, pack, effective dates)",
        "Create Ingredient Batch (for supplied ingredients)"
    ],
    "General (Viewer)": [
        "Product Ingredient List (with nested materials, ordered by quantity)"
    ],
    "View Queries": [
        "View saved queries or reports"
    ]
}

# Database configuration
config = {
        'host': 'localhost',
        'user': 'root',
        'database': 'dbms'
    }

def show_menu(options):
    for idx, option in enumerate(options, 1):
        print(f"[{idx}] {option}")
    print("[0] Back/Exit")

def manufacturer_actions():
    while True:
        print("\n[Manufacturer Actions]")
        show_menu(roles["Manufacturer"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["Manufacturer"])+1)):
            action = roles["Manufacturer"][int(choice)-1]
            print(f"\nExecuting '{action}'... (placeholder)")
        else:
            print("Invalid choice. Try again.")

def supplier_actions():
    while True:
        print("\n[Supplier Actions]")
        show_menu(roles["Supplier"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["Supplier"])+1)):
            action = roles["Supplier"][int(choice)-1]
            print(f"\nExecuting '{action}'... (placeholder)")
        else:
            print("Invalid choice. Try again.")

def viewer_actions():
    while True:
        print("\n[Viewer Actions]")
        show_menu(roles["General (Viewer)"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["General (Viewer)"])+1)):
            action = roles["General (Viewer)"][int(choice)-1]
            print(f"\nDisplaying '{action}'... (placeholder)")
        else:
            print("Invalid choice. Try again.")

def view_queries():
    while True:
        print("\n[View Queries]")
        show_menu(roles["View Queries"])
        choice = input("Select an option: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            print("\nShowing queries... (placeholder)")
        else:
            print("Invalid choice. Try again.")

def main():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print("Connected to MySQL database")

            # Create a cursor to execute queries
            cursor = connection.cursor()

            # Example: Initialize schema
            sql_path = Path(__file__).resolve().parent / "../sql/init.sql"
            with open(sql_path, "r") as f:
                sql_commands = f.read().split(';')

            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
            print("Tables created successfully")

            while True:
                print("\nSelect role: [1] Manufacturer  [2] Supplier  [3] General (Viewer) [4] View Queries  [0] Exit")
                role_choice = input("Enter choice: ").strip()
                if role_choice == "0":
                    print("Exiting...")
                    sys.exit()
                elif role_choice == "1":
                    manufacturer_actions()
                elif role_choice == "2":
                    supplier_actions()
                elif role_choice == "3":
                    viewer_actions()
                elif role_choice == "4":
                    view_queries()
                else:
                    print("Invalid choice. Try again.")

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    main()


