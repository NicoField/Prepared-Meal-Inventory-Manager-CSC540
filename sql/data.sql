INSERT INTO Category (Category_ID, Cat_Name)
VALUES
(2, 'Dinner'),
(3, 'Side');

INSERT INTO Manufacturer (M_ID, M_Name)
VALUES
("MFG001", "John Smith"),
("MFG002", "Alice Lee");

INSERT INTO Viewer (V_ID, V_Name)
VALUES
("VIEW001", "Bob Johnson");

INSERT INTO Supplier (S_ID, S_Name)
VALUES
("20", "Supplier A"),
("21", "Supplier B"),
("SUP001", "Jane Doe");

INSERT INTO Product (P_ID, P_Name, Category_ID, Standard_Batch_Size, M_ID)
VALUES
(100, 'Steak Dinner', 2, 500, "MFG001"),
(101, 'Mac & Cheese', 3, 300, "MFG002");

INSERT INTO Ingredient (I_ID, I_Name, I_Type)
VALUES
(101, 'Salt', "Atomic"),
(102, 'Pepper', "Atomic"),
(104, 'Sodium Phosphate', "Atomic"),
(106, 'Beef Steak', "Atomic"),
(108, 'Pasta', "Atomic"),
(201, 'Seasoning Blend', "Compound"),
(301, 'Super Seasoning', "Compound");

INSERT INTO DoNotCombine (I_ID1, I_ID2)
VALUES
(201, 104),
(106, 104);

INSERT INTO Formulation (F_ID, CI_ID, S_ID, Version_No, Eff_Start_Date, Eff_End_Date, Unit_Price, Pack_Size)
VALUES
(1, 201, 20, 1, "2025-01-01", "2025-11-30", 20.0, 8.0);

INSERT INTO FormulationIngredient (F_ID, AI_ID, Quantity)
VALUES
(1, 101, 6.0),
(1, 102, 2.0);

INSERT INTO Recipe (R_ID, P_ID, Creation_Date)
VALUES
(1000, 100, "2025-01-01"),
(1001, 101, "2025-01-01");

INSERT INTO RecipeUsesIngredient (R_ID, I_ID, Quantity)
VALUES
(1000, 106, 6.0),
(1000, 201, 0.2),
(1001, 108, 7.0),
(1001, 101, 0.5),
(1001, 102, 2.0);

INSERT INTO SupplierSuppliesIngredient (S_ID, I_ID)
VALUES
("20", 101),
("20", 102),
("20", 104),
("20", 106),
("20", 108),
("20", 201),
("20", 301),
("21", 101),
("21", 102),
("21", 104),
("21", 106),
("21", 108),
("21", 201),
("21", 301);

INSERT INTO IngredientBatch (I_ID, S_ID, Batch_ID, Quantity, Cost, Expiration_Date)
VALUES
(101, "20", "B0001", 1000, 0.1, "2026-11-15"),
(101, "21", "B0001", 800, 0.08, "2026-10-30"),
(101, "20", "B0002", 500, 0.1, "2026-11-01"),
(101, "20", "B0003", 500, 0.1, "2026-12-15"),
(102, "20", "B0001", 1200, 0.3, "2026-12-15"),
(106, "20", "B0005", 3000, 0.5, "2026-12-15"),
(106, "20", "B0006", 750, 0.5, "2026-12-20"),
(108, "20", "B0001", 1000, 0.25, "2026-9-28"),
(108, "20", "B0003", 6300, 0.25, "2026-12-31"),
(201, "20", "B0001", 100, 2.5, "2026-11-30"),
(201, "20", "B0002", 30, 2.5, "2026-12-30");

INSERT INTO Inventory (Ingredient_Lot_Number, M_ID, Quantity, Expiration_Date)
VALUES
("106-20-B0006", "MFG001", 750, "2026-11-15"),
("201-20-B0002", "MFG001", 30, "2026-10-30"),
("101-20-B0002", "MFG002", 180, "2026-11-15"),
("108-20-B0003", "MFG002", 2300, "2026-10-30"),
("102-20-B0001", "MFG002", 800, "2026-10-30");

INSERT INTO ProductBatch (P_ID, M_ID, Batch_ID, R_ID, Quantity, Production_Date, Expiration_Date)
VALUES
(100, "MFG001", "B0901", 1000, 100, "2025-09-26", "2025-11-15"),
(101, "MFG002", "B0101", 1001, 300, "2025-09-10", "2025-10-30");

INSERT INTO ProductIngredientBatch (Product_Lot_Number, Ingredient_Lot_Number, Quantity_Used)
VALUES
("100-MFG001-B0901", "106-20-B0006", 600),
("100-MFG001-B0901", "201-20-B0002", 20),
("101-MFG002-B0101", "101-20-B0002", 150),
("101-MFG002-B0101", "108-20-B0003", 2100),
("101-MFG002-B0101", "102-20-B0001", 600);