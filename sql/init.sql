DROP TABLE IF EXISTS ProductIngredientBatch;
DROP TABLE IF EXISTS ProductBatch;
DROP TABLE IF EXISTS IngredientBatch;
DROP TABLE IF EXISTS RecipeUsesIngredient;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS FormulationIngredient;
DROP TABLE IF EXISTS Formulation;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS DoNotCombine;
DROP TABLE IF EXISTS AtomicIngredient;
DROP TABLE IF EXISTS CompoundIngredient;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS Viewer;
DROP TABLE IF EXISTS HealthRiskLog;


CREATE TABLE Manufacturer (
    M_ID VARCHAR(10) PRIMARY KEY,
    M_Name VARCHAR(255) NOT NULL
);

CREATE TABLE Category (
    Category_ID INT PRIMARY KEY,
    Cat_Name ENUM('Dinner', 'Side', 'Dessert', 'Other') NOT NULL
);

CREATE TABLE Product (
    P_ID INT PRIMARY KEY,
    P_Name VARCHAR(255) NOT NULL,
    Category_ID INT NOT NULL,
    Standard_Batch_Size INT NOT NULL CHECK (Standard_Batch_Size > 0),
    M_ID VARCHAR(10) NOT NULL,
    FOREIGN KEY (M_ID) REFERENCES Manufacturer(M_ID),
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

CREATE TABLE Recipe (
    R_ID INT PRIMARY KEY,
    P_ID INT NOT NULL,
    Creation_Date DATE NOT NULL,
    FOREIGN KEY (P_ID) REFERENCES Product(P_ID)
);

CREATE TABLE Ingredient (
    I_ID INT PRIMARY KEY,
    I_Name VARCHAR(255) NOT NULL,
    I_Type VARCHAR(50) CHECK (I_Type IN ('Atomic', 'Compound'))
);

CREATE TABLE AtomicIngredient (
    AI_ID INT PRIMARY KEY,
    FOREIGN KEY (AI_ID) REFERENCES Ingredient(I_ID)
);

CREATE TABLE CompoundIngredient (
    CI_ID INT PRIMARY KEY,
    FOREIGN KEY (CI_ID) REFERENCES Ingredient(I_ID)
);


CREATE TABLE RecipeUsesIngredient (
    R_ID INT NOT NULL,
    I_ID INT NOT NULL,
    Quantity DECIMAL(10,2) CHECK (Quantity >= 0),
    PRIMARY KEY (R_ID, I_ID),
    FOREIGN KEY (I_ID) REFERENCES Ingredient(I_ID)
);

CREATE TABLE Supplier (
    S_ID VARCHAR(10) PRIMARY KEY,
    S_Name VARCHAR(255) NOT NULL
);

CREATE TABLE Viewer (
    V_ID VARCHAR(10) PRIMARY KEY,
    V_Name VARCHAR(255) NOT NULL
);

CREATE TABLE Formulation (
	F_ID INT PRIMARY KEY AUTO_INCREMENT,
    CI_ID INT NOT NULL,
    S_ID VARCHAR(10) NOT NULL,
    Version_No INT NOT NULL,
    Eff_Start_Date DATE NOT NULL,
    Eff_End_Date DATE NOT NULL,
    Unit_Price DECIMAL(10,2) NOT NULL CHECK (Unit_Price > 0),
    Pack_Size DECIMAL(10,2) NOT  NULL CHECK (Pack_Size > 0),
    FOREIGN KEY (CI_ID) REFERENCES CompoundIngredient(CI_ID),
    FOREIGN KEY (S_ID) REFERENCES Supplier(S_ID),
    UNIQUE (CI_ID, Version_No)
);

CREATE TABLE DoNotCombine (
    I_ID1 INT NOT NULL,
    I_ID2 INT NOT NULL,
    PRIMARY KEY (I_ID1, I_ID2),
    FOREIGN KEY (I_ID1) REFERENCES Ingredient(I_ID),
    FOREIGN KEY (I_ID2) REFERENCES Ingredient(I_ID),
    CHECK (I_ID1 <> I_ID2)
);

CREATE TABLE FormulationIngredient (
    F_ID INT NOT NULL,
    AI_ID INT NOT NULL,
    Quantity DECIMAL(10,2) NOT NULL CHECK (Quantity > 0),
    PRIMARY KEY (F_ID, AI_ID),
    FOREIGN KEY (F_ID) REFERENCES Formulation(F_ID),
    FOREIGN KEY (AI_ID) REFERENCES AtomicIngredient(AI_ID)
);

CREATE TABLE ProductBatch (
    P_ID INT NOT NULL,
    M_ID VARCHAR(10) NOT NULL,
    Batch_ID VARCHAR(10) NOT NULL,
    R_ID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity >= 0),
    Production_Date DATE NOT NULL,
    Expiration_Date DATE NOT NULL,

    Product_Lot_Number VARCHAR(100) GENERATED ALWAYS AS 
        (CONCAT(CAST(P_ID AS CHAR), '-', CAST(M_ID AS CHAR), '-', CAST(Batch_ID AS CHAR))) STORED,
    PRIMARY KEY (P_ID, M_ID, Batch_ID),
    UNIQUE (Product_Lot_Number),

    FOREIGN KEY (P_ID) REFERENCES Product(P_ID),
    FOREIGN KEY (M_ID) REFERENCES Manufacturer(M_ID),
    FOREIGN KEY (R_ID) REFERENCES Recipe(R_ID)
);

CREATE TABLE IngredientBatch (
    I_ID INT NOT NULL,
    S_ID VARCHAR(10) NOT NULL,
    Batch_ID VARCHAR(10) NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity >= 0),
    Cost DECIMAL(10,2) NOT NULL CHECK (Cost >= 0),
    Expiration_Date DATE NOT NULL,

    Ingredient_Lot_Number VARCHAR(100) GENERATED ALWAYS AS 
        (CONCAT(CAST(I_ID AS CHAR), '-', CAST(S_ID AS CHAR), '-', CAST(Batch_ID AS CHAR))) STORED,
    PRIMARY KEY (I_ID, S_ID, Batch_ID),
    UNIQUE (Ingredient_Lot_Number),

    FOREIGN KEY (I_ID) REFERENCES Ingredient(I_ID),
    FOREIGN KEY (S_ID) REFERENCES Supplier(S_ID)
);

CREATE TABLE ProductIngredientBatch (
    Product_Lot_Number VARCHAR(100) NOT NULL,
    Ingredient_Lot_Number VARCHAR(100) NOT NULL,
    Quantity_Used INT NOT NULL CHECK (Quantity_Used > 0),
    PRIMARY KEY (Product_Lot_Number, Ingredient_Lot_Number),
    FOREIGN KEY (Product_Lot_Number) REFERENCES ProductBatch(Product_Lot_Number),
    FOREIGN KEY (Ingredient_Lot_Number) REFERENCES IngredientBatch(Ingredient_Lot_Number)
);

CREATE TABLE Inventory (
    Ingredient_Lot_Number VARCHAR(50) PRIMARY KEY,
    M_ID VARCHAR(10) NOT NULL,
    Quantity INT NOT NULL,
    Expiration_Date DATE,
    FOREIGN KEY (M_ID) REFERENCES Manufacturer(M_ID)
);

CREATE TABLE HealthRiskLog (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Product_Lot_Number VARCHAR(100) NOT NULL,
    I_ID1 INT NOT NULL,
    I_ID2 INT NOT NULL,
    Violation_Date DATETIME DEFAULT CURRENT_TIMESTAMP
);









CREATE OR REPLACE VIEW RecentHealthRiskViolationsView AS
SELECT 
    Product_Lot_Number,
    I_ID1,
    I_ID2,
    Violation_Date
FROM HealthRiskLog
WHERE Violation_Date >= NOW() - INTERVAL 30 DAY
ORDER BY Violation_Date DESC;

CREATE OR REPLACE VIEW ActiveSupplierFormulationsView AS
SELECT
    s.S_Name AS Supplier_Name,
    ci.I_Name AS Compound_Ingredient_Name,
    GROUP_CONCAT(CONCAT(ai.I_Name, ' (', fi.Quantity, ')') SEPARATOR ', ') AS Ingredients,
    f.Unit_Price,
    f.Pack_Size,
    f.Version_No AS Version
FROM Formulation f
JOIN Supplier s ON f.S_ID = s.S_ID
JOIN Ingredient ci ON f.CI_ID = ci.I_ID
JOIN FormulationIngredient fi ON f.F_ID = fi.F_ID
JOIN Ingredient ai ON fi.AI_ID = ai.I_ID
WHERE CURRENT_DATE BETWEEN f.Eff_Start_Date AND f.Eff_End_Date
  AND f.Version_No = (
      SELECT MAX(f2.Version_No)
      FROM Formulation f2
      WHERE f2.CI_ID = f.CI_ID
  )
GROUP BY s.S_Name, ci.I_Name, f.Unit_Price, f.Pack_Size, f.Version_No;








CREATE TRIGGER check_overlap
BEFORE INSERT ON Formulation
FOR EACH ROW
IF EXISTS (
    SELECT 1
    FROM Formulation
    WHERE CI_ID = NEW.CI_ID
      AND S_ID = NEW.S_ID
      AND NEW.Eff_Start_Date <= Eff_End_Date
      AND NEW.Eff_End_Date >= Eff_Start_Date
) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Effective period overlaps with existing entry.';
END IF;

CREATE TRIGGER check_expiration_before_batch_insert
BEFORE INSERT ON IngredientBatch
FOR EACH ROW
IF NEW.Expiration_Date < DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Expiration date must be at least 90 days from today.';
END IF;

CREATE TRIGGER check_expiration_before_inventory_insert
BEFORE INSERT ON Inventory
FOR EACH ROW
IF NEW.Expiration_Date < DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Expiration date must be at least 90 days from today.';
END IF;

CREATE TRIGGER prevent_expired_consumption
BEFORE INSERT ON ProductIngredientBatch
FOR EACH ROW
IF (SELECT Expiration_Date 
    FROM Inventory
    WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number
      AND M_ID = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(NEW.Product_Lot_Number, '-', 2), '-', -1) AS UNSIGNED)
    LIMIT 1) < CURDATE()
THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Cannot consume from an expired ingredient batch.';
END IF;

CREATE TRIGGER update_batch_on_inventory_insert
AFTER INSERT ON Inventory
FOR EACH ROW
BEGIN
    DECLARE current_qty INT;

    -- Get current ingredient batch quantity
    SELECT Quantity INTO current_qty
    FROM IngredientBatch
    WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number;

    -- If batch not found
    IF current_qty IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Ingredient batch not found when adding to inventory.';
    END IF;

    -- If insufficient batch quantity
    IF current_qty < NEW.Quantity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Insufficient quantity in ingredient batch to move to inventory.';
    END IF;

    -- Deduct from IngredientBatch
    UPDATE IngredientBatch
    SET Quantity = Quantity - NEW.Quantity
    WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number;
END;

CREATE TRIGGER update_batch_on_inventory_update
AFTER UPDATE ON Inventory
FOR EACH ROW
BEGIN
    DECLARE qty_diff INT;
    DECLARE current_qty INT;

    -- Calculate how much quantity was added (positive) or removed (negative)
    SET qty_diff = NEW.Quantity - OLD.Quantity;

    -- Only adjust IngredientBatch if inventory increased
    IF qty_diff > 0 THEN
        SELECT Quantity INTO current_qty
        FROM IngredientBatch
        WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number;

        IF current_qty IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Error: Ingredient batch not found in inventory.';
        END IF;

        IF current_qty < qty_diff THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Error: Not enough ingredient quantity in inventory.';
        END IF;

        UPDATE IngredientBatch
        SET Quantity = Quantity - qty_diff
        WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number;
    END IF;
END;

CREATE TRIGGER update_inventory_on_consumption
AFTER INSERT ON ProductIngredientBatch
FOR EACH ROW
BEGIN
    DECLARE current_qty INT;

    -- Get current quantity from inventory
    SELECT Quantity INTO current_qty
    FROM Inventory
    WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number
      AND M_ID = SUBSTRING_INDEX(SUBSTRING_INDEX(NEW.Product_Lot_Number, '-', 2), '-', -1);

    -- If not found, raise error
    IF current_qty IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Ingredient lot not found in inventory.';
    END IF;

    -- If insufficient quantity, raise error
    IF current_qty < NEW.Quantity_Used THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Insufficient ingredients in inventory.';
    END IF;

    -- Otherwise, update the inventory
    UPDATE Inventory
    SET Quantity = Quantity - NEW.Quantity_Used
    WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number
      AND M_ID = SUBSTRING_INDEX(SUBSTRING_INDEX(NEW.Product_Lot_Number, '-', 2), '-', -1);
END;

CREATE TRIGGER insert_into_atomic_subclass
AFTER INSERT ON Ingredient
FOR EACH ROW
INSERT INTO AtomicIngredient (AI_ID)
SELECT NEW.I_ID
WHERE NEW.I_Type = 'Atomic';

CREATE TRIGGER insert_into_compound_subclass
AFTER INSERT ON Ingredient
FOR EACH ROW
INSERT INTO CompoundIngredient (CI_ID)
SELECT NEW.I_ID
WHERE NEW.I_Type = 'Compound';

CREATE TRIGGER check_health_risk_before_batch
BEFORE INSERT ON ProductBatch
FOR EACH ROW
BEGIN
    DECLARE I1 INT;
    DECLARE I2 INT;
    DECLARE done INT DEFAULT 0;
    DECLARE msg VARCHAR(255);

    DECLARE cur_pairs CURSOR FOR
        SELECT r1.I_ID, r2.I_ID
        FROM RecipeUsesIngredient r1
        JOIN RecipeUsesIngredient r2
          ON r1.R_ID = r2.R_ID
         AND r1.I_ID < r2.I_ID
        WHERE r1.R_ID = NEW.R_ID;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur_pairs;

    read_loop: LOOP
        FETCH cur_pairs INTO I1, I2;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Check for conflict and block batch if exists
        IF EXISTS (
            SELECT 1
            FROM DoNotCombine d
            WHERE (CAST(d.I_ID1 AS SIGNED) = I1 AND CAST(d.I_ID2 AS SIGNED) = I2)
               OR (CAST(d.I_ID1 AS SIGNED) = I2 AND CAST(d.I_ID2 AS SIGNED) = I1)
        ) THEN
            SET msg = CONCAT('Health Risk Detected: Ingredients ', CAST(I1 AS CHAR), ' & ', CAST(I2 AS CHAR));
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
        END IF;

    END LOOP;

    CLOSE cur_pairs;
END;







CREATE PROCEDURE IF NOT EXISTS LogHealthRisk(
    IN p_batch VARCHAR(100),
    IN p_I1 INT,
    IN p_I2 INT
)
BEGIN
    START TRANSACTION;
        INSERT INTO HealthRiskLog(Product_Lot_Number, I_ID1, I_ID2)
        VALUES (p_batch, p_I1, p_I2);
    COMMIT;
END;

CREATE PROCEDURE IF NOT EXISTS RecordProductionBatch(
    IN p_P_ID INT,
    IN p_M_ID VARCHAR(10),
    IN p_Batch_ID VARCHAR(10),
    IN p_R_ID INT,
    IN p_Quantity INT,
    IN p_Production_Date DATE,
    IN p_Expiration_Date DATE,
    IN p_IngredientData JSON  -- JSON array of {Ingredient_Lot, Quantity_Used}
)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE total_items INT;
    DECLARE total_cost DECIMAL(10,2) DEFAULT 0.0;
    DECLARE ingredient_lot VARCHAR(100);
    DECLARE qty_used INT;
    DECLARE ingredient_cost DECIMAL(10,2);

    -- Step 1: Insert ProductBatch
    INSERT INTO ProductBatch (P_ID, M_ID, Batch_ID, R_ID, Quantity, Production_Date, Expiration_Date)
    VALUES (p_P_ID, p_M_ID, p_Batch_ID, p_R_ID, p_Quantity, p_Production_Date, p_Expiration_Date);

    SET total_items = JSON_LENGTH(p_IngredientData);

    -- Step 2: Loop through JSON ingredient list
    WHILE i < total_items DO
        SET ingredient_lot = JSON_UNQUOTE(JSON_EXTRACT(p_IngredientData, CONCAT('$[', i, '].Ingredient_Lot')));
        SET qty_used = JSON_EXTRACT(p_IngredientData, CONCAT('$[', i, '].Quantity_Used'));

        -- Get cost per unit from IngredientBatch
        SELECT Cost INTO ingredient_cost
        FROM IngredientBatch
        WHERE Ingredient_Lot_Number = ingredient_lot;

        -- Step 3: Insert into ProductIngredientBatch
        INSERT INTO ProductIngredientBatch (Product_Lot_Number, Ingredient_Lot_Number, Quantity_Used)
        VALUES (
            CONCAT(p_P_ID, '-', p_M_ID, '-', p_Batch_ID),
            ingredient_lot,
            qty_used
        );

        -- Step 4: Accumulate cost
        SET total_cost = total_cost + (ingredient_cost * qty_used);

        SET i = i + 1;
    END WHILE;

    -- Step 5: Compute cost per unit and return
    SET @unit_cost = total_cost / p_Quantity;
    SELECT total_cost AS Total_Cost, @unit_cost AS Unit_Cost;
END;

CREATE PROCEDURE IF NOT EXISTS TraceRecall(IN in_ingredient_lot VARCHAR(100))
BEGIN
    -- Return all product lots that used this ingredient lot
    SELECT Product_Lot_Number, Quantity_Used
    FROM ProductIngredientBatch
    WHERE Ingredient_Lot_Number = in_ingredient_lot;
END;