import sys
import os
import pymysql
import json

from pathlib import Path
from sshtunnel import SSHTunnelForwarder

base_dir = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(base_dir, "config", "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

sql_folder = os.path.join(os.path.dirname(__file__), "..", "sql")
init_file = os.path.join(sql_folder, "init.sql")
trigger_file = os.path.join(sql_folder, "triggers.sql")
data_file = os.path.join(sql_folder, "data.sql")

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

def show_menu(options):
    for idx, option in enumerate(options, 1):
        print(f"[{idx}] {option}")
    print("[0] Back/Exit")

def manufacturer_actions(cursor):
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

def supplier_actions(cursor):
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

def viewer_actions(cursor):
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

def view_queries(cursor):
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
    with SSHTunnelForwarder(
        (config["ssh_host"], 22),
        ssh_username=config["ssh_user"],
        ssh_password=config["ssh_password"],
        remote_bind_address=(config["mysql_host"], 3306)
    ) as tunnel:
        connection = pymysql.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=config["ssh_user"],
            password=config["mysql_password"],
            database=config["ssh_user"],
            autocommit=True
        )
        
        cursor = connection.cursor()
        print(f"Executing init.sql...")
        with open(init_file, "r") as f:
            sql_script = f.read()

        # Split by semicolon for multiple statements
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt + ";")

        print("✅ init.sql executed successfully.")
        
        print(f"Executing triggers.sql...")
        with open(trigger_file) as f:
            sql_text = f.read()

        # Remove BOM and extra whitespace
        sql_text = sql_text.strip()

        # Split on "CREATE" to isolate each statement
        parts = sql_text.split("CREATE")
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Add the "CREATE" keyword back to the part
            stmt = "CREATE " + part

            try:
                cursor.execute(stmt)
            except pymysql.MySQLError as e:
                print("Error executing statement:")
                print(stmt)
                print(e)
                break

        print("✅ triggers.sql executed successfully.")

        print(f"Executing data.sql...")

        with open(data_file, "r") as f:
            sql_script = f.read()

        # Split by semicolon for multiple statements
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt + ";")

        print("✅ data.sql executed successfully.")

        while True:
            print("\nSelect role: [1] Manufacturer  [2] Supplier  [3] General (Viewer) [4] View Queries  [0] Exit")
            role_choice = input("Enter choice: ").strip()
            if role_choice == "0":
                print("Exiting...")
                cursor.close()
                connection.close()
                sys.exit()
            elif role_choice == "1":
                manufacturer_actions(cursor)
            elif role_choice == "2":
                supplier_actions(cursor)
            elif role_choice == "3":
                viewer_actions(cursor)
            elif role_choice == "4":
                view_queries(cursor)
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()


