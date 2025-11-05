def define_update_product(cursor, mid):
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
                "INSERT INTO Product (P_ID, P_Name, Category_ID, Standard_Batch_Size, M_ID) VALUES (%s, %s, %s, %s, %s)",
                (pid, pname, category_id, batch_size, mid)
            )
            print("Product created.")
    except Exception as e:
        print(f"Error in define/update product: {e}")

def define_update_recipe(cursor, mid):
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
    except Exception as e:
        print(f"Error in define/update recipe: {e}")

def record_ingredient_receipt(cursor, mid):
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
    except Exception as e:
        print(f"Error in recording ingredient receipt: {e}")

def create_product_batch(cursor, mid):
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
        print("Product batch created.")
    except Exception as e:
        print(f"Error in creating product batch: {e}")

def report_on_hand(cursor, mid):
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

def report_nearly_oos(cursor, mid):
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

def report_almost_expired(cursor, mid):
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

def view_report(cursor, mid):
    print("--- Reports ---")
    try:
        report_on_hand(cursor, mid)
        report_nearly_oos(cursor, mid)
        report_almost_expired(cursor, mid)
    except Exception as e:
        print(f"Error in generating reports: {e}")

def recall_traceability(cursor, mid):
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
