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
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Effective period overlaps with existing entry.';
END IF;

CREATE TRIGGER check_expiration_before_batch_insert
BEFORE INSERT ON IngredientBatch
FOR EACH ROW
IF NEW.Expiration_Date < DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expiration date must be at least 90 days from today.';
END IF;

CREATE TRIGGER check_expiration_before_inventory_insert
BEFORE INSERT ON Inventory
FOR EACH ROW
IF NEW.Expiration_Date < DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expiration date must be at least 90 days from today.';
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
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot consume from an expired ingredient batch.';
END IF;

CREATE TRIGGER update_batch_on_inventory_insert
AFTER INSERT ON Inventory
FOR EACH ROW
UPDATE IngredientBatch
SET Quantity = Quantity + NEW.Quantity
WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number;

CREATE TRIGGER update_inventory_on_consumption
AFTER INSERT ON ProductIngredientBatch
FOR EACH ROW
UPDATE Inventory
SET Quantity = Quantity - NEW.Quantity_Used
WHERE Ingredient_Lot_Number = NEW.Ingredient_Lot_Number
  AND M_ID = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(NEW.Product_Lot_Number, '-', 2), '-', -1) AS UNSIGNED);

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