def manufacturers_not_supplied_by(cursor):    
    cursor.execute("""
    SELECT m.M_ID, m.M_Name
    FROM Manufacturer m
    WHERE m.M_ID NOT IN (
        SELECT DISTINCT pb.M_ID
        FROM ProductBatch pb
        JOIN ProductIngredientBatch pib 
            ON pb.Product_Lot_Number = pib.Product_Lot_Number
        JOIN IngredientBatch ib 
            ON pib.Ingredient_Lot_Number = ib.Ingredient_Lot_Number
        WHERE ib.S_ID = 21
    )
    ORDER BY m.M_ID;
    """)
    
    results = cursor.fetchall()
    
    print(f"\nManufacturers not supplied by supplier 21:")
    for mid, mname in results:
        print(f"  - {mid}: {mname}")

def conflicting_ingredients_for_batch(cursor):    
    cursor.execute("""
    WITH batch_ingredients AS (
        SELECT i.I_ID
        FROM ProductIngredientBatch pib
        JOIN IngredientBatch ib ON pib.Ingredient_Lot_Number = ib.Ingredient_Lot_Number
        JOIN Ingredient i ON ib.I_ID = i.I_ID
        WHERE pib.Product_Lot_Number = '100-MFG001-B0901'
    )
    SELECT DISTINCT i.I_Name
    FROM DoNotCombine d
    JOIN Ingredient i ON 
        (i.I_ID = d.I_ID1 AND d.I_ID2 IN (SELECT I_ID FROM batch_ingredients))
        OR (i.I_ID = d.I_ID2 AND d.I_ID1 IN (SELECT I_ID FROM batch_ingredients));
    """)
    
    results = cursor.fetchall()
    print(f"\nIngredients that cannot be included in batch 100-MFG001-B0901:")
    for (name,) in results:
        print(f"  - {name}")

def product_unit_cost(cursor):    
    cursor.execute("""
    SELECT 
        pb.Product_Lot_Number,
        pb.Quantity AS Produced_Units,
        SUM(pib.Quantity_Used * ib.Cost) AS Total_Cost,
        (SUM(pib.Quantity_Used * ib.Cost) / pb.Quantity) AS Unit_Cost
    FROM ProductBatch pb
    JOIN ProductIngredientBatch pib
        ON pb.Product_Lot_Number = pib.Product_Lot_Number
    JOIN IngredientBatch ib
        ON pib.Ingredient_Lot_Number = ib.Ingredient_Lot_Number
    WHERE pb.Product_Lot_Number = '100-MFG001-B0901'
    GROUP BY pb.Product_Lot_Number, pb.Quantity;
    """)
    
    result = cursor.fetchone()
    lot, produced, total_cost, unit_cost = result
    print(f"\nBatch: {lot}")
    print(f"Produced Units: {produced}")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Unit Cost: ${unit_cost:.2f}")

def manufacturer_supplier_spending(cursor):
    cursor.execute("""
    SELECT 
        s.S_Name,
        SUM(pib.Quantity_Used * ib.Cost) AS Total_Spent
    FROM ProductBatch pb
    JOIN ProductIngredientBatch pib 
        ON pb.Product_Lot_Number = pib.Product_Lot_Number
    JOIN IngredientBatch ib 
        ON pib.Ingredient_Lot_Number = ib.Ingredient_Lot_Number
    JOIN Supplier s 
        ON ib.S_ID = s.S_ID
    WHERE pb.M_ID = 'MFG002'
    GROUP BY s.S_ID, s.S_Name
    ORDER BY Total_Spent DESC;
    """)
    
    results = cursor.fetchall()
    print(f"\nSuppliers for manufacturer MFG002:")
    for supplier, total in results:
        print(f"  - {supplier}: ${total:.2f}")


def last_batch_ingredients(cursor):
    cursor.execute("""
        SELECT i.I_Name, ib.Ingredient_Lot_Number
        FROM ProductBatch pb
        JOIN ProductIngredientBatch pib ON pb.Product_Lot_Number = pib.Product_Lot_Number
        JOIN IngredientBatch ib ON pib.Ingredient_Lot_Number = ib.Ingredient_Lot_Number
        JOIN Ingredient i ON ib.I_ID = i.I_ID
        WHERE pb.P_ID = 100
          AND pb.Production_Date = (
              SELECT MAX(Production_Date)
              FROM ProductBatch
              WHERE P_ID = 100
          )
    """)

    results = cursor.fetchall()
    print(f"\nIngredients used in the last batch of product ID 100 by manufacturer MFG001:")
    for name, lot in results:
        print(f"  - {name} (Lot: {lot})")