from datetime import date
from collections import defaultdict

def print_table(rows, headers):
    if not rows:
        print("No results.")
        return
    col_widths = [max(len(str(cell)) for cell in [h] + [row[i] for row in rows]) for i, h in enumerate(headers)]
    header_line = " | ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join([str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)]))

def choose_from_list(options, prompt):
    for i, opt in enumerate(options, 1):
        print(f"[{i}] {opt}")
    idx = int(input(prompt)) - 1
    if idx < 0 or idx >= len(options):
        print("Invalid selection.")
        return None
    return idx

def define_update_product(conn, cursor, mid):
    print("=== Define/Update Product ===")
    try:
        cursor.execute("SELECT Category_ID, Cat_Name FROM Category")
        categories = cursor.fetchall()
        if not categories:
            print("No categories found.")
            return
        print("Select a category:")
        for idx, cat in enumerate(categories, 1):
            print(f"[{idx}] {cat[1]}")
        cidx = int(input("Enter the number for your category: ")) - 1
        if cidx < 0 or cidx >= len(categories):
            print("Invalid category number.")
            return
        category_id = categories[cidx][0]

        pname = input("Enter Product Name: ").strip()
        batch_size = int(input("Enter Standard Batch Size: ").strip())

        cursor.execute(
            "INSERT INTO Product (P_Name, Category_ID, Standard_Batch_Size, M_ID) VALUES (%s, %s, %s, %s)",
            (pname, category_id, batch_size, mid)
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        pid = cursor.fetchone()[0]
        print(f"Product created: ID={pid}, Name={pname}")
        conn.commit()
    except Exception as e:
        print(f"Error in define/update product: {e}")

def define_update_recipe(conn, cursor, mid):
    print("=== Define/Update Product BOM (Recipe) ===")
    try:
        cursor.execute("SELECT P_ID, P_Name FROM Product WHERE M_ID=%s", (mid,))
        products = cursor.fetchall()
        if not products:
            print("You don't own any products.")
            return
        print("Select a product for the BOM:")
        pidx = choose_from_list([f"{pid} - {pname}" for pid, pname in products], "Enter product number: ")
        if pidx is None:
            return
        pid = products[pidx][0]

        creation_date = date.today()
        cursor.execute("INSERT INTO Recipe (P_ID, Creation_Date) VALUES (%s, %s)", (pid, creation_date))
        cursor.execute("SELECT LAST_INSERT_ID()")
        rid = cursor.fetchone()[0]
        print(f"Creating new recipe version (ID={rid}) for Product {pid}.")

        ingredients_added = []
        while True:
            cursor.execute("SELECT I_ID, I_Name FROM Ingredient")
            ingredient_list = cursor.fetchall()
            if not ingredient_list:
                print("No ingredients available.")
                break
            print("Select an ingredient to add to recipe:")
            iidx = choose_from_list([f"{iid} - {iname}" for iid, iname in ingredient_list], "Enter ingredient number (or blank to finish): ")
            if iidx is None:
                break
            iid = ingredient_list[iidx][0]
            qty = float(input("  Quantity (oz): ").strip())
            cursor.execute(
                "INSERT INTO RecipeUsesIngredient (R_ID, I_ID, Quantity) VALUES (%s, %s, %s)",
                (rid, iid, qty)
            )
            ingredients_added.append(iid)
            again = input("Add another ingredient to this recipe? (y/n): ").strip().lower()
            if again != 'y':
                break
        print("Recipe updated.")
        conn.commit()
    except Exception as e:
        print(f"Error in define/update recipe: {e}")

def record_ingredient_receipt(conn, cursor, mid):
    print("=== Record Ingredient Receipt ===")
    try:
        #FEFO 
        use_fefo = input("Use FEFO auto selection for ingredients? (y/n): ").strip().lower() == 'y'
        cursor.execute("SELECT I_Name FROM Ingredient")
        ing_names = [row[0] for row in cursor.fetchall()]
        if not ing_names:
            print("No ingredient names found.")
            return
        print("Available ingredients:")
        idx = choose_from_list(ing_names, "Select ingredient number: ")
        if idx is None:
            return
        ing_name = ing_names[idx]

        cursor.execute("SELECT I_ID FROM Ingredient WHERE I_Name=%s", (ing_name,))
        iid = cursor.fetchone()[0]

        if use_fefo:
            #Select from earliest expiry
            cursor.execute("""
                SELECT Ingredient_Lot_Number, Quantity, Expiration_Date, S_ID 
                FROM IngredientBatch 
                WHERE I_ID=%s AND Expiration_Date>=CURDATE()
                AND Quantity>0
                ORDER BY Expiration_Date ASC LIMIT 1""", (iid,))
            lot = cursor.fetchone()
            if not lot:
                print("No eligible lots found.")
                return
            print(f"Auto-selected Lot: {lot[0]} (Qty: {lot[1]}, Exp: {lot[2]}, Supplier: {lot[3]})")
            qty_receive = int(input("Enter quantity to record as received: ").strip())
            cursor.execute(
                "INSERT INTO Inventory (Ingredient_Lot_Number, M_ID, Quantity, Expiration_Date) VALUES (%s, %s, %s, %s)",
                (lot[0], mid, qty_receive, lot[2])
            )
        else:
            #Manual lot selection
            cursor.execute("""
                SELECT Ingredient_Lot_Number, Quantity, Expiration_Date, S_ID 
                FROM IngredientBatch 
                WHERE I_ID=%s AND Expiration_Date>=CURDATE()
                AND Quantity>0""", (iid,))
            lots = cursor.fetchall()
            if not lots:
                print("No available lots for this ingredient.")
                return
            print("Select a lot to receive:")
            lotchoices = [f"{l[0]} (Qty: {l[1]}, Exp: {l[2]}, Supplier: {l[3]})" for l in lots]
            lidx = choose_from_list(lotchoices, "Enter lot number: ")
            if lidx is None:
                return
            lot = lots[lidx]
            qty_receive = int(input("Enter quantity to record as received: ").strip())
            cursor.execute(
                "INSERT INTO Inventory (Ingredient_Lot_Number, M_ID, Quantity, Expiration_Date) VALUES (%s, %s, %s, %s)",
                (lot[0], mid, qty_receive, lot[2])
            )
        print("Ingredient receipt recorded.")
        conn.commit()
    except Exception as e:
        print(f"Error in recording ingredient receipt: {e}")

def create_product_batch(conn, cursor, mid):
    print("=== Create Product Batch ===")
    try:
        cursor.execute("SELECT P_ID, P_Name, Standard_Batch_Size FROM Product WHERE M_ID=%s", (mid,))
        products = cursor.fetchall()
        if not products:
            print("No products found.")
            return
        print("Select a product to batch:")
        pidx = choose_from_list([f"{pid} - {pname}" for pid, pname, _ in products], "Enter product number: ")
        if pidx is None:
            return
        pid, pname, std_batch_size = products[pidx]

        #Find most recent recipe
        cursor.execute("SELECT R_ID FROM Recipe WHERE P_ID=%s ORDER BY Creation_Date DESC LIMIT 1", (pid,))
        row = cursor.fetchone()
        if not row:
            print("No recipes available for this product.")
            return
        rid = row[0]

        bid = input("Enter Batch ID: ").strip()

        mul = int(input(f"Enter number of batches to produce (Standard batch size: {std_batch_size}): "))
        quantity = mul * std_batch_size

        prod_date = date.today()
        exp_date = input("Enter Expiration Date for batch (YYYY-MM-DD): ").strip()
        #insert ProductBatch
        cursor.execute(
            "INSERT INTO ProductBatch (P_ID, M_ID, Batch_ID, R_ID, Quantity, Production_Date, Expiration_Date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (pid, mid, bid, rid, quantity, prod_date, exp_date)
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        batch_id = cursor.fetchone()[0]

        #Consume ingredients
        cursor.execute(
            "SELECT I_ID, Quantity FROM RecipeUsesIngredient WHERE R_ID=%s", (rid,)
        )
        ingredients = cursor.fetchall()
        for iid, total_needed in ingredients:
            qty_needed = total_needed * mul
            print(f"\nConsuming {qty_needed} of ingredient ID {iid} for product batch.")
            use_fefo = input("Auto-select lots by FEFO? (y/n): ").strip().lower() == 'y'
            remaining = qty_needed
            while remaining > 0:
                if use_fefo:
                    cursor.execute(
                        "SELECT Ingredient_Lot_Number, Quantity, Expiration_Date FROM Inventory WHERE I_ID=%s AND M_ID=%s AND Quantity>0 ORDER BY Expiration_Date ASC LIMIT 1", (iid, mid)
                    )
                else:
                    cursor.execute(
                        "SELECT Ingredient_Lot_Number, Quantity, Expiration_Date FROM Inventory WHERE I_ID=%s AND M_ID=%s AND Quantity>0", (iid, mid)
                    )
                avail = cursor.fetchone()
                if not avail:
                    print("Not enough inventory for this ingredient!")
                    break
                lotno, avail_qty, lot_exp = avail
                consume = min(avail_qty, remaining)
                cursor.execute(
                    "UPDATE Inventory SET Quantity = Quantity - %s WHERE Ingredient_Lot_Number=%s AND M_ID=%s",
                    (consume, lotno, mid)
                )
                cursor.execute(
                    "INSERT INTO ProductIngredientBatch (Product_Lot_Number, Ingredient_Lot_Number, Quantity_Used) VALUES ((SELECT Product_Lot_Number FROM ProductBatch WHERE Batch_ID=%s AND P_ID=%s), %s, %s)",
                    (batch_id, pid, lotno, consume)
                )
                print(f"Consumed {consume} from lot {lotno}.")
                remaining -= consume

        print("Product batch created and inventory updated.")
        conn.commit()
    except Exception as e:
        print(f"Error in creating product batch: {e}")

def report_on_hand(cursor, mid):
    print("=== On Hand Inventory ===")
    try:
        cursor.execute("SELECT Ingredient_Lot_Number, Quantity, Expiration_Date FROM Inventory WHERE M_ID=%s", (mid,))
        rows = cursor.fetchall()
        print_table(rows, ["Lot#", "Qty", "Expires"])
    except Exception as e:
        print(f"Error fetching on-hand inventory: {e}")

def report_nearly_oos(cursor, mid):
    print("=== Nearly Out Of Stock Products ===")
    try:
        cursor.execute("""
            SELECT p.P_ID, p.P_Name, IFNULL(SUM(pb.Quantity),0) as OnHand, p.Standard_Batch_Size
            FROM Product p LEFT JOIN ProductBatch pb ON p.P_ID = pb.P_ID
            WHERE p.M_ID=%s
            GROUP BY p.P_ID, p.P_Name, p.Standard_Batch_Size
            HAVING OnHand < p.Standard_Batch_Size
        """, (mid,))
        rows = cursor.fetchall()
        print_table(rows, ["Product ID", "Name", "OnHand", "StdBatchSize"])
    except Exception as e:
        print(f"Error fetching nearly out of stock products: {e}")

def report_almost_expired(cursor, mid):
    print("=== Inventory Expiring Soon (<10 days) ===")
    try:
        cursor.execute("""
            SELECT Ingredient_Lot_Number, Quantity, Expiration_Date
            FROM Inventory
            WHERE M_ID=%s AND DATEDIFF(Expiration_Date, CURDATE()) <= 10
        """, (mid,))
        rows = cursor.fetchall()
        print_table(rows, ["Lot#", "Qty", "Expires"])
    except Exception as e:
        print(f"Error fetching almost expired inventory: {e}")

def view_report(cursor, mid):
    print("--- Reports ---")
    report_on_hand(cursor, mid)
    report_nearly_oos(cursor, mid)
    report_almost_expired(cursor, mid)

def recall_traceability(cursor, mid):
    print("=== Recall/Traceability by Ingredient Lot ===")
    try:
        lotnum = input("Enter Ingredient Lot Number for recall: ").strip()
        cursor.execute("""
            SELECT pib.Product_Lot_Number, pb.P_ID, pb.Production_Date, pb.Expiration_Date, pib.Quantity_Used
            FROM ProductIngredientBatch pib
            JOIN ProductBatch pb ON pib.Product_Lot_Number = pb.Product_Lot_Number
            WHERE pib.Ingredient_Lot_Number=%s
        """, (lotnum,))
        rows = cursor.fetchall()
        print_table(rows, ["Product Lot#", "Product ID", "Prod Date", "Expires", "Qty Used"])
    except Exception as e:
        print(f"Error in recall/traceability: {e}")
