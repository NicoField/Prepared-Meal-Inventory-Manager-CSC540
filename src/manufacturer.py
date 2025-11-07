from collections import defaultdict

def define_update_product(conn, cursor, mid):
    print("=== Define/Update Product ===")
    try:
        pid = input("Enter Product ID (leave blank to create): ").strip()
        pname = input("Enter Product Name: ").strip()
        category_id = input("Enter Category ID: ").strip()
        batch_size = input("Enter Standard Batch Size: ").strip()
        if pid:
            cursor.execute(
                "UPDATE Product SET P_Name=%s, Category_ID=%s, Standard_Batch_Size=%s WHERE P_ID=%s AND M_ID=%s",
                (pname, category_id, batch_size, pid, mid)
            )
            print("Product updated.")
        else:
            cursor.execute(
                "INSERT INTO Product (P_Name, Category_ID, Standard_Batch_Size, M_ID) VALUES (%s, %s, %s, %s)",
                (pname, category_id, batch_size, mid)
            )
            print("Product created.")
        conn.commit()
    except Exception as e:
        print(f"Error in define/update product: {e}")

def define_update_recipe(conn, cursor, mid):
    print("=== Define/Update Product BOM (Recipe) ===")
    try:
        pid = input("Enter Product ID: ").strip()
        cursor.execute("SELECT * FROM Product WHERE P_ID=%s AND M_ID=%s", (pid, mid))
        if not cursor.fetchone():
            print("Invalid Product ID or you don't own this product.")
            return
        rid = input("Enter Recipe ID (leave blank to create): ").strip()
        creation_date = input("Enter Creation Date (YYYY-MM-DD): ").strip()
        
        if rid:
            cursor.execute("DELETE FROM RecipeUsesIngredient WHERE R_ID=%s", (rid,))
            print("Existing ingredients for this recipe cleared.")
        else:
            cursor.execute("INSERT INTO Recipe (R_ID, P_ID, Creation_Date) VALUES (%s, %s, %s)", (rid or None, pid, creation_date))
            cursor.execute("SELECT LAST_INSERT_ID()")
            rid = cursor.fetchone()[0]
            print(f"Created Recipe ID: {rid}")
        
        while True:
            iid = input("Add Ingredient ID (blank to stop): ").strip()
            if not iid:
                break
            qty = input("  Quantity (oz): ").strip()
            cursor.execute(
                "INSERT INTO RecipeUsesIngredient (R_ID, I_ID, Quantity) VALUES (%s, %s, %s)",
                (rid, iid, qty)
            )
            print("Ingredient added.")
        print("Recipe updated.")
        conn.commit()
    except Exception as e:
        print(f"Error in define/update recipe: {e}")

def record_ingredient_receipt(conn, cursor, mid):
    """Record ingredient receipt - uses I_ID, S_ID, Batch_ID instead of lot number"""
    print("=== Record Ingredient Receipt ===")
    try:
        iid = input("Enter Ingredient ID: ").strip()
        sid = input("Enter Supplier ID: ").strip()
        bid = input("Enter Batch ID: ").strip()
        
        #lot number from components
        lot_number = f"{iid}-{sid}-{bid}"
        
        cursor.execute(
            "SELECT Quantity, Expiration_Date FROM IngredientBatch WHERE Ingredient_Lot_Number=%s", 
            (lot_number,)
        )
        batch = cursor.fetchone()
        if not batch:
            print("Ingredient batch not found.")
            return
        
        qty, exp_date = batch
        cursor.execute(
            "INSERT INTO Inventory (Ingredient_Lot_Number, M_ID, Quantity, Expiration_Date) VALUES (%s, %s, %s, %s)",
            (lot_number, mid, qty, exp_date)
        )
        print("Ingredient receipt recorded successfully.")
        conn.commit()
    except Exception as e:
        print(f"Error in recording ingredient receipt: {e}")

def create_product_batch(conn, cursor, mid):
    print("=== Create Product Batch ===")
    try:
        pid = input("Enter Product ID: ").strip()
        rid = input("Enter Recipe ID: ").strip()
        batch_id = input("Enter Batch ID: ").strip()
        quantity = input("Enter Quantity Produced: ").strip()
        prod_date = input("Enter Production Date (YYYY-MM-DD): ").strip()
        exp_date = input("Enter Expiration Date (YYYY-MM-DD): ").strip()
        cursor.execute(
            "INSERT INTO ProductBatch (P_ID, M_ID, Batch_ID, R_ID, Quantity, Production_Date, Expiration_Date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (pid, mid, batch_id, rid, quantity, prod_date, exp_date)
        )
        conn.commit()
        print("Product batch created.")
    except Exception as e:
        err_msg = str(e)
        print(f"Error in creating product batch: {err_msg}")

        if "Health Risk Detected" in err_msg:
            # err_msg is: "Health Risk Detected: Ingredients X&Y"
            text = err_msg.split("Health Risk Detected: ")[1]
            text = text.replace("Ingredients","").strip()
            text = text.replace(")", "").replace("'", "")

            i1, i2 = map(int, text.split("&"))
            product_lot_number = f"{pid}-{mid}-{batch_id}"
            cursor.execute(
                "INSERT INTO HealthRiskLog(Product_Lot_Number, I_ID1, I_ID2) VALUES (%s, %s, %s)",
                (product_lot_number, i1, i2)
            )
            conn.commit()
            print("Health Risk Logged.")

def report_on_hand(conn, cursor, mid):
    print("=== On Hand Inventory ===")
    try:
        cursor.execute(
            "SELECT * FROM Inventory WHERE M_ID=%s", (mid,)
        )
        results = cursor.fetchall()
        if not results:
            print("No inventory found for your manufacturer.")
        for row in results:
            print(row)
    except Exception as e:
        print(f"Error fetching on-hand inventory: {e}")

def report_nearly_oos(conn, cursor, mid):
    print("=== Nearly Out of Stock Products ===")
    try:
        cursor.execute(
            "SELECT p.P_ID, p.P_Name, SUM(i.Quantity) as Total_Quantity, p.Standard_Batch_Size "
            "FROM Product p "
            "LEFT JOIN Inventory i ON i.M_ID = p.M_ID "
            "WHERE p.M_ID=%s "
            "GROUP BY p.P_ID, p.P_Name, p.Standard_Batch_Size "
            "HAVING Total_Quantity < p.Standard_Batch_Size OR Total_Quantity IS NULL",
            (mid,)
        )
        results = cursor.fetchall()
        if not results:
            print("No products are nearly out of stock.")
        for row in results:
            print(row)
    except Exception as e:
        print(f"Error fetching nearly out of stock products: {e}")

def report_almost_expired(conn, cursor, mid):
    print("=== Almost Expired Inventory (<10 days) ===")
    try:
        cursor.execute(
            "SELECT * FROM Inventory "
            "WHERE M_ID=%s AND DATEDIFF(Expiration_Date, CURDATE()) <= 10", (mid,)
        )
        results = cursor.fetchall()
        if not results:
            print("No inventory is expiring within 10 days.")
        for row in results:
            print(row)
    except Exception as e:
        print(f"Error fetching almost expired inventory: {e}")

def view_report(conn, cursor, mid):
    print("--- Reports ---")
    try:
        report_on_hand(conn, cursor, mid)
        report_nearly_oos(conn, cursor, mid)
        report_almost_expired(conn, cursor, mid)
    except Exception as e:
        print(f"Error in generating reports: {e}")

def recall_traceability(conn, cursor, mid):
    print("=== Recall/Traceability ===")
    try:
        lot_number = input("Enter Product_Lot_Number: ").strip()
        cursor.execute(
            "SELECT * FROM ProductBatch WHERE Product_Lot_Number=%s", (lot_number,)
        )
        batch = cursor.fetchone()
        if not batch:
            print("Batch not found.")
            return
        
        print(f"Product Batch Details: {batch}")
        
        cursor.execute(
            "SELECT * FROM ProductIngredientBatch WHERE Product_Lot_Number=%s", (lot_number,)
        )
        results = cursor.fetchall()
        if not results:
            print("No associated ingredients found for this batch.")
        else:
            print("Associated Ingredient Batches:")
            for row in results:
                print(row)
    except Exception as e:
        print(f"Error in recall/traceability: {e}")

def view_health_violations(conn, cursor, mid):
    print("=== Recent Health Risk Violations (Last 30 Days) ===")

    cursor.execute("SELECT Product_Lot_Number, I_ID1, I_ID2, Violation_Date FROM RecentHealthRiskViolationsView")
    rows = cursor.fetchall()

    if not rows:
        print("No recent violations.")
        return

    # nice formatted print
    print("{:<25} {:<10} {:<10} {:<20}".format("Product Lot", "Ing1", "Ing2", "Violation Date"))
    print("-" * 70)

    for row in rows:
        print("{:<25} {:<10} {:<10} {:<20}".format(row[0], row[1], row[2], str(row[3])))

def view_product_boms(conn, cursor, mid):
    print("\n=== Flattened Product BOM ===")
    print(f"Manufacturer ID: {mid}\n")

    cursor.execute("""
        SELECT P_ID, P_Name, I_Name, Total_Quantity
        FROM ProductBOMView
        WHERE P_ID IN (SELECT P_ID FROM Product WHERE M_ID = %s)
        ORDER BY P_ID, I_Name;
    """, (mid,))
    
    boms = defaultdict(list)
    for pid, pname, iname, qty in cursor.fetchall():
        boms[(pid, pname)].append(f"{iname} ({qty:.4f})")

    # Prepare rows
    rows = []
    for (pid, pname), ingredients in boms.items():
        ingredients_str = ', '.join(ingredients)
        rows.append([str(pid), pname, ingredients_str])

    # Calculate column widths
    col_widths = [max(len(row[i]) for row in rows + [["Product ID", "Product Name", "Ingredients"]]) for i in range(3)]

    # Print header
    header = ["Product ID", "Product Name", "Ingredients"]
    print(" | ".join(header[i].ljust(col_widths[i]) for i in range(3)))
    print("-+-".join('-' * col_widths[i] for i in range(3)))

    # Print rows
    for row in rows:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(3)))

