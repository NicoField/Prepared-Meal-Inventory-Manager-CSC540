def declare_ingredient_supplied(cursor, sid):
    print("=== Declare Ingredient Supplied ===")
    try:
        iid = input("Enter Ingredient ID: ").strip()
        name = input("Enter Ingredient Name: ").strip()
        itype = input("Enter Ingredient Type (Atomic/Compound): ").strip()
        
        cursor.execute(
            "INSERT INTO Ingredient (I_ID, I_Name, I_Type) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE I_Name=%s, I_Type=%s",
            (iid, name, itype, name, itype)
        )
        print("Ingredient declared/updated.")
    except Exception as e:
        print(f"Error in declaring ingredient: {e}")

def maintain_formulations(cursor, sid):
    """Maintain formulations - uses CI_ID for compound ingredients"""
    print("=== Maintain Formulations ===")
    try:
        fid = input("Enter Formulation ID (leave blank to create): ").strip()
        ci_id = input("Enter Compound Ingredient ID (CI_ID): ").strip()
        version = input("Enter Version Number: ").strip()
        start_date = input("Enter Effective Start Date (YYYY-MM-DD): ").strip()
        end_date = input("Enter Effective End Date (YYYY-MM-DD): ").strip()
        price = input("Enter Unit Price: ").strip()
        pack_size = input("Enter Pack Size (oz): ").strip()
        
        if fid:
            cursor.execute(
                "UPDATE Formulation SET Version_No=%s, Eff_Start_Date=%s, Eff_End_Date=%s, Unit_Price=%s, Pack_Size=%s "
                "WHERE F_ID=%s AND CI_ID=%s AND S_ID=%s",
                (version, start_date, end_date, price, pack_size, fid, ci_id, sid)
            )
            print("Formulation updated.")
        else:
            cursor.execute(
                "INSERT INTO Formulation (CI_ID, S_ID, Version_No, Eff_Start_Date, Eff_End_Date, Unit_Price, Pack_Size) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (ci_id, sid, version, start_date, end_date, price, pack_size)
            )
            cursor.execute("SELECT LAST_INSERT_ID()")
            fid = cursor.fetchone()[0]
            print(f"Formulation created with ID: {fid}")
        
        #atomic ingredients to formulation
        while True:
            ai_id = input("  Add Atomic Ingredient ID (AI_ID, blank to stop): ").strip()
            if not ai_id:
                break
            qty = input("    Quantity (oz): ").strip()
            try:
                cursor.execute(
                    "INSERT INTO FormulationIngredient (F_ID, AI_ID, Quantity) VALUES (%s, %s, %s)",
                    (fid, ai_id, qty)
                )
                print(f"    Added AI_ID {ai_id} to formulation.")
            except Exception as inner_e:
                print(f"    Error linking atomic ingredient: {inner_e}")
        
        print("Formulation processing complete.")
    except Exception as e:
        print(f"Error in maintaining formulation: {e}")

def create_ingredient_batch(cursor, sid):
    """Create ingredient batch - lot number is auto-generated"""
    print("=== Create Ingredient Batch ===")
    try:
        iid = input("Enter Ingredient ID: ").strip()
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
    except Exception as e:
        print(f"Error in creating ingredient batch: {e}")
