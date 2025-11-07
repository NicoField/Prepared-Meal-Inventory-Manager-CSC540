def declare_ingredient_supplied(conn, cursor, sid):
    print("=== Declare Ingredient Supplied ===")
    try:
        name = input("Enter Ingredient Name: ").strip()
        itype = input("Enter Ingredient Type (Atomic/Compound): ").strip()

        cursor.execute(
            """
            INSERT INTO Ingredient (I_Name, I_Type) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE I_ID = LAST_INSERT_ID(I_ID)
            """,
            (name, itype)
        )
        conn.commit()

        # retrieve the id
        iid = cursor.lastrowid

        cursor.execute(
            """
            INSERT IGNORE INTO SupplierSuppliesIngredient (S_ID, I_ID)
            VALUES (%s, %s)
            """,
            (sid, iid)
        )
        conn.commit()

        print(f"Ingredient '{name}' now associated with supplier {sid} under ID {iid}.")

    except Exception as e:
        print(f"Error in declaring ingredient: {e}")

def maintain_formulations(conn, cursor, sid):
    print("=== Maintain Formulations ===")
    try:
        cursor.execute("""
            SELECT i.I_ID, i.I_Name
            FROM Ingredient i
            JOIN SupplierSuppliesIngredient ssi ON ssi.I_ID = i.I_ID
            WHERE ssi.S_ID = %s AND i.I_Type='Compound'
            ORDER BY i.I_Name
        """, (sid,))

        compounds = cursor.fetchall()
        if not compounds:
            print("This supplier does not supply any compound ingredients yet.")
            return

        print("\nSelect a compound ingredient to modify:")
        for idx, row in enumerate(compounds):
            print(f"  [{idx+1}] {row[1]}")

        while True:
            choice = input("Select compound ingredient (number): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(compounds):
                break
            print("Invalid selection. Try again.")

        ci_id = compounds[int(choice)-1][0]
        comp_name = compounds[int(choice)-1][1]

        cursor.execute("""
            SELECT F_ID, Version_No, Eff_Start_Date, Eff_End_Date, Unit_Price, Pack_Size
            FROM Formulation
            WHERE S_ID=%s AND CI_ID=%s
            ORDER BY Version_No DESC
        """, (sid, ci_id))

        existing_forms = cursor.fetchall()

        if existing_forms:
            print(f"\nExisting Formulations for '{comp_name}':")
            print("F_ID | Version | Start      | End        | Price | Pack Size")
            print("-----+---------+------------+------------+-------+-------------")
            for f in existing_forms:
                print(f"{f[0]:>4} | {f[1]:>7} | {str(f[2]):<10} | {str(f[3]):<10} | {f[4]:>5} | {f[5]:>9}")
        else:
            print(f"\nNo existing formulations found for '{comp_name}'.")

        cursor.execute("""
            SELECT MAX(Version_No)
            FROM Formulation
            WHERE S_ID=%s AND CI_ID=%s
        """, (sid, ci_id))
        max_ver_row = cursor.fetchone()
        max_version = max_ver_row[0] if max_ver_row and max_ver_row[0] is not None else 0


        version = max_version + 1
        start_date = input("Enter Effective Start Date (YYYY-MM-DD). Must not overlap with existing formulation: ").strip()
        end_date = input("Enter Effective End Date (YYYY-MM-DD). Must not overlap with existing formulation: ").strip()
        price = input("Enter Unit Price: ").strip()
        pack_size = input("Enter Pack Size (oz): ").strip()
        
        cursor.execute(
            "INSERT INTO Formulation (CI_ID, S_ID, Version_No, Eff_Start_Date, Eff_End_Date, Unit_Price, Pack_Size) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (ci_id, sid, version, start_date, end_date, price, pack_size)
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        fid = cursor.fetchone()[0]
        print(f"Formulation created with F_ID: {fid}")

        # atomic ingredients loop
        while True:
            ainame = input("  Add Atomic Ingredient Name (blank to stop): ").strip()
            if not ainame:
                break

            # lookup atomic id
            cursor.execute("SELECT I_ID FROM Ingredient WHERE I_Name=%s AND I_Type='Atomic'", (ainame,))
            arow = cursor.fetchone()
            if not arow:
                print(f"Atomic ingredient '{ainame}' not found. Please add it first from 'Declare Ingredient Supplied'.")
                continue

            ai_id = arow[0]

            # ensure supplier actually supplies this ingredient
            cursor.execute("SELECT 1 FROM SupplierSuppliesIngredient WHERE S_ID=%s AND I_ID=%s", (sid, ai_id))
            if cursor.fetchone() is None:
                print(f"Supplier does NOT supply {ainame}. Cannot use in formulation.")
                continue

            qty = input("    Quantity (oz): ").strip()

            try:
                cursor.execute(
                    "INSERT INTO FormulationIngredient (F_ID, AI_ID, Quantity) VALUES (%s, %s, %s)",
                    (fid, ai_id, qty)
                )
                print(f"    Added {ainame} ({ai_id}) to formulation.")
            except Exception as inner_e:
                print(f"    Error linking atomic ingredient: {inner_e}")

        conn.commit()
        print("Formulation processing complete.")

    except Exception as e:
        print(f"Error in maintaining formulation: {e}")

def create_ingredient_batch(conn, cursor, sid):
    """Create ingredient batch - lot number is auto-generated"""
    print("=== Create Ingredient Batch ===")
    try:
        cursor.execute("""
            SELECT i.I_ID, i.I_Name
            FROM SupplierSuppliesIngredient ssi
            JOIN Ingredient i ON ssi.I_ID = i.I_ID
            WHERE ssi.S_ID=%s
            ORDER BY i.I_Name
        """, (sid,))
        rows = cursor.fetchall()

        print("Select Ingredient:")
        for idx, row in enumerate(rows, start=1):
            print(f"  [{idx}] {row[1]}")

        choice = int(input("Enter choice number: "))
        iid = rows[choice - 1][0]

        bid = input("Enter Batch ID: ").strip()
        qty = input("Enter Quantity: ").strip()
        cost = input("Enter Cost: ").strip()
        expdate = input("Enter Expiration Date (YYYY-MM-DD, must be 90+ days from today): ").strip()
        cursor.execute(
            "INSERT INTO IngredientBatch (I_ID, S_ID, Batch_ID, Quantity, Cost, Expiration_Date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (iid, sid, bid, qty, cost, expdate)
        )
        print(f"Ingredient batch created. Lot Number: {iid}-{sid}-{bid}")
        conn.commit()
    except Exception as e:
        print(f"Error in creating ingredient batch: {e}")

def view_active_formulations(conn, cursor, sid):
    print("\n=== Current Active Formulations ===")
    print(f"Supplier ID: {sid}\n")
    query = """
        SELECT Supplier_Name, Compound_Ingredient_Name, Ingredients, Unit_Price, Pack_Size, Version
        FROM ActiveSupplierFormulationsView
        WHERE Supplier_Name IN (
            SELECT S_Name FROM Supplier WHERE S_ID = %s
        )
        ORDER BY Compound_Ingredient_Name;
    """
    cursor.execute(query, (sid,))
    
    rows = cursor.fetchall()
    if not rows:
        print(f"No active formulations found for supplier ID {sid}.")
        return
    
    # Calculate max widths for neat printing
    headers = ["Supplier Name", "Compound Ingredient", "Ingredients", "Unit Price", "Pack Size", "Version"]
    col_widths = [len(h) for h in headers]
    
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # Print header
    print(" | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * w for w in col_widths))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)))