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