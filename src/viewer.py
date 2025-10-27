def get_flattened_ingredients(cursor, product_id):
    """
    Returns a set of all ingredient IDs for a given product, including nested ingredients
    for compound ingredients (1 level deep).
    """
    ingredients_set = set()

    # Get top-level ingredients
    cursor.execute("""
        SELECT i.I_ID, i.I_Type
        FROM Recipe r
        JOIN RecipeUsesIngredient rui ON rui.R_ID = r.R_ID
        JOIN Ingredient i ON i.I_ID = rui.I_ID
        WHERE r.P_ID = %s
    """, (product_id,))
    top_ingredients = cursor.fetchall()

    for i_id, i_type in top_ingredients:
        ingredients_set.add(i_id)

        # If compound, get nested ingredients
        if i_type == 'Compound':
            cursor.execute("""
                SELECT fi.AI_ID
                FROM Formulation f
                JOIN FormulationIngredient fi ON f.F_ID = fi.F_ID
                WHERE f.CI_ID = %s
            """, (i_id,))
            nested_ids = [row[0] for row in cursor.fetchall()]
            ingredients_set.update(nested_ids)

    return ingredients_set


def compare_products_for_incompatibilities(cursor, product_id1, product_id2):
    """
    Compares two products for incompatibilities based on DoNotCombine table.
    Prints all offending ingredient pairs.
    """
    # Flatten ingredients for both products
    ingredients1 = get_flattened_ingredients(cursor, product_id1)
    ingredients2 = get_flattened_ingredients(cursor, product_id2)

    combined_ingredients = ingredients1.union(ingredients2)

    # Check for offending pairs in DoNotCombine table
    cursor.execute("""
        SELECT d.I_ID1, d.I_ID2, i1.I_Name, i2.I_Name
        FROM DoNotCombine d
        JOIN Ingredient i1 ON d.I_ID1 = i1.I_ID
        JOIN Ingredient i2 ON d.I_ID2 = i2.I_ID
        WHERE d.I_ID1 IN %s AND d.I_ID2 IN %s
    """, (tuple(combined_ingredients), tuple(combined_ingredients)))

    conflicts = cursor.fetchall()

    if conflicts:
        print(f"\nFound {len(conflicts)} incompatibility(ies) between the products:")
        for i1_id, i2_id, i1_name, i2_name in conflicts:
            print(f"  - {i1_name} and {i2_name} should not be combined")
    else:
        print("\nNo incompatibilities found between the products.")

def select_product(cursor):
    """
    Lists all products and allows the user to select one by number.
    Returns the chosen product's P_ID.
    """
    cursor.execute("SELECT P_ID, P_Name FROM Product ORDER BY P_Name")
    products = cursor.fetchall()

    if not products:
        print("No products available.")
        return None

    print("\nAvailable Products:")
    for idx, (p_id, name) in enumerate(products, start=1):
        print(f"{idx}. {name} (ID: {p_id})")

    while True:
        try:
            choice = int(input("Enter the number of the product: "))
            if 1 <= choice <= len(products):
                return products[choice - 1][0]
            else:
                print(f"Please enter a number between 1 and {len(products)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def compare_products(cursor):
    """
    Command-line UI to select two products and compare them for incompatibilities.
    """
    print("\nSelect the first product to compare:")
    product1_id = select_product(cursor)
    if product1_id is None:
        return

    print("\nSelect the second product to compare:")
    product2_id = select_product(cursor)
    if product2_id is None:
        return

    print("\nChecking for incompatibilities...")
    compare_products_for_incompatibilities(cursor, product1_id, product2_id)

def view_product_ingredient_list(cursor):
    """
    Prints products organized by Manufacturer -> Category -> Product
    and lists nested ingredients (1 level deep) ordered by quantity.
    """
    # Query top-level products and ingredients
    query = """
    SELECT 
        m.M_Name, 
        c.Cat_Name, 
        p.P_Name,
        i.I_ID,
        i.I_Name,
        rui.Quantity,
        i.I_Type
    FROM Product p
    JOIN Manufacturer m ON p.M_ID = m.M_ID
    JOIN Category c ON p.Category_ID = c.Category_ID
    JOIN Recipe r ON r.P_ID = p.P_ID
    JOIN RecipeUsesIngredient rui ON rui.R_ID = r.R_ID
    JOIN Ingredient i ON i.I_ID = rui.I_ID
    ORDER BY m.M_Name, c.Cat_Name, p.P_Name, rui.Quantity DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    if not results:
        print("No products found.")
        return

    current_manufacturer = None
    current_category = None
    current_product = None

    for manufacturer, category, product, i_id, ingredient, quantity, i_type in results:
        if manufacturer != current_manufacturer:
            current_manufacturer = manufacturer
            print(f"\nManufacturer: {manufacturer}")
            current_category = None
            current_product = None

        if category != current_category:
            current_category = category
            print(f"  Category: {category}")
            current_product = None

        if product != current_product:
            current_product = product
            print(f"    Product: {product}")

        # Print top-level ingredient
        print(f"      * {ingredient} ({quantity})")

        # If compound, fetch nested ingredients (1 level)
        if i_type == 'Compound':
            cursor.execute("""
                SELECT i.I_Name, fi.quantity
                FROM Formulation f
                JOIN FormulationIngredient fi ON f.F_ID = fi.F_ID
                JOIN Ingredient i ON i.I_ID = fi.AI_ID
                WHERE f.CI_ID = %s
                ORDER BY fi.quantity DESC
            """, (i_id,))
            nested_ingredients = cursor.fetchall()
            for nested_name, nested_qty in nested_ingredients:
                print(f"        - {nested_name} ({nested_qty})")
