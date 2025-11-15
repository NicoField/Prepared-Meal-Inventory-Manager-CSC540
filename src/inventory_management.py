import sys
import os
import pymysql
import json
import re

import manufacturer as m
import supplier as s
import viewer as v
import queries as q

from pathlib import Path
from sshtunnel import SSHTunnelForwarder
from datetime import date

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
        "Product Ingredient List (with nested materials, ordered by quantity)",
        "Compare Products for Incompatibilities"
    ],
    "View Queries": [
        "Last Batch Ingredients for P_ID 100",
        "Supplier Spending for Manufacturer MFG002",
        "Product Unit Cost for Lot Number 100-MFG001-B0901",
        "Conflicting Ingredients for Product Lot 100-MFG001-B0901",
        "Manufacturers Not Supplied by Supplier 21"
    ]
}

def show_menu(options):
    for idx, option in enumerate(options, 1):
        print(f"[{idx}] {option}")
    print("[0] Back/Exit")

def manufacturer_actions(conn, cursor):
    mid = input("Enter user id: ").strip()
    cursor.execute("SELECT M_Name FROM Manufacturer WHERE M_ID = %s", (mid,))
    result = cursor.fetchone()
    if result:
        print(f"Welcome {result[0]}")
    else:
        print("Invalid user")
        return

    while True:
        print("\n[Manufacturer Actions]")
        show_menu(roles["Manufacturer"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["Manufacturer"]) + 1)):
            match choice:
                case "1":
                    m.define_update_product(conn, cursor, mid)
                case "2":
                    m.define_update_recipe(conn, cursor, mid)
                case "3":
                    m.record_ingredient_receipt(conn, cursor, mid)
                case "4":
                    m.create_product_batch(conn, cursor, mid)
                case "5":
                    m.view_report(cursor, mid)
                case "6":
                    m.recall_traceability(cursor, mid)
                case _:
                    print("Invalid choice. Try again.")
            conn.commit()
        else:
            print("Invalid choice. Try again.")

def supplier_actions(conn, cursor):
    sid = input("Enter user id: ").strip()
    cursor.execute("SELECT S_Name FROM Supplier WHERE S_ID = %s", (sid,))
    result = cursor.fetchone()
    if result:
        print(f"Welcome {result[0]}")
    else:
        print("Invalid user")
        return

    while True:
        print("\n[Supplier Actions]")
        show_menu(roles["Supplier"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["Supplier"]) + 1)):
            match choice:
                case "1":
                    s.declare_ingredient_supplied(conn, cursor, sid)
                case "2":
                    s.maintain_formulations(conn, cursor, sid)
                case "3":
                    s.create_ingredient_batch(conn, cursor, sid)
                case _:
                    print("Invalid choice. Try again.")
            conn.commit()
        else:
            print("Invalid choice. Try again.")

def viewer_actions(cursor):
    vid = input("Enter user id: ").strip()
    cursor.execute("SELECT V_Name FROM Viewer WHERE V_ID = %s", (vid,))
    result = cursor.fetchone()
    if result:
        print(f"Welcome {result[0]}")
    else:
        print("Invalid user")
        return

    while True:
        print("\n[Viewer Actions]")
        show_menu(roles["General (Viewer)"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["General (Viewer)"]) + 1)):
            try:
                match choice:
                    case "1":
                        v.view_product_ingredient_list(cursor)
                    case "2":
                        v.compare_products(cursor)
            except Exception as e:
                print(f"\nError while executing query: {e}")
        else:
            print("Invalid choice. Try again.")

def view_queries(cursor):
    while True:
        print("\n[View Queries]")
        show_menu(roles["View Queries"])
        choice = input("Select an action: ").strip()
        if choice == "0":
            break
        elif choice in map(str, range(1, len(roles["View Queries"]) + 1)):
            try:
                match choice:
                    case "1":
                        q.last_batch_ingredients(cursor)
                    case "2":
                        q.manufacturer_supplier_spending(cursor)
                    case "3":
                        q.product_unit_cost(cursor)
                    case "4":
                        q.conflicting_ingredients_for_batch(cursor)
                    case "5":
                        q.manufacturers_not_supplied_by(cursor)
            except Exception as e:
                print(f"\nError while executing query: {e}")
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
        parts = re.split(r'\b(CREATE|DROP)\b', sql_script, flags=re.IGNORECASE)
        stmts = []
        i = 1
        while i < len(parts):
            keyword = parts[i].upper()
            statement = parts[i + 1].strip()
            if statement:
                stmts.append(f"{keyword} {statement}")
            i += 2
        for part in stmts:
            part = part.strip()
            if not part:
                continue
            try:
                cursor.execute(part)
            except pymysql.MySQLError as e:
                print("Error executing statement:")
                print(part)
                print(e)
                break
        print("✅ init.sql executed successfully.")

        print(f"Executing data.sql...")
        with open(data_file, "r") as f:
            sql_script = f.read()
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt + ";")
        print("✅ data.sql executed successfully.")

        while True:
            print("\nSelect role: [1] Manufacturer [2] Supplier [3] General (Viewer) [4] View Queries [0] Exit")
            role_choice = input("Enter choice: ").strip()
            if role_choice == "0":
                print("Exiting...")
                cursor.close()
                connection.close()
                sys.exit()
            elif role_choice == "1":
                manufacturer_actions(connection, cursor)
            elif role_choice == "2":
                supplier_actions(connection, cursor)
            elif role_choice == "3":
                viewer_actions(cursor)
            elif role_choice == "4":
                view_queries(cursor)
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
