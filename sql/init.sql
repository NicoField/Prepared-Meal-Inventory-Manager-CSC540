DROP TABLE IF EXISTS ProductIngredientBatch;
DROP TABLE IF EXISTS ProductBatch;
DROP TABLE IF EXISTS IngredientBatch;
DROP TABLE IF EXISTS RecipeIngredient;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS FormulationIngredient;
DROP TABLE IF EXISTS Formulation;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS DoNotCombine;
DROP TABLE IF EXISTS AtomicIngredient;
DROP TABLE IF EXISTS CompoundIngredient;


CREATE TABLE Manufacturer (
    M_ID INT PRIMARY KEY,
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
    M_ID INT NOT NULL,
    FOREIGN KEY (M_ID) REFERENCES Manufacturer(M_ID),
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

CREATE TABLE Recipe (
    R_ID INT PRIMARY KEY,
    P_ID INT NOT NULL,
    Creation_Date DATE NOT NULL,
    FOREIGN KEY (P_ID) REFERENCES Product(P_ID)
);

CREATE TABLE AtomicIngredient (
    AI_ID INT PRIMARY KEY,
    AI_Name VARCHAR(255) NOT NULL
);

CREATE TABLE CompoundIngredient (
    CI_ID INT PRIMARY KEY,
    CI_Name VARCHAR(255) NOT NULL
);

CREATE TABLE RecipeIngredient (
	RI_ID INT PRIMARY KEY AUTO_INCREMENT,
    R_ID INT NOT NULL,
    AI_ID INT NULL,
    CI_ID INT NULL,
    Quantity INT CHECK (Quantity >= 0),
    FOREIGN KEY (R_ID) REFERENCES Recipe(R_ID),
    FOREIGN KEY (AI_ID) REFERENCES AtomicIngredient(AI_ID),
    FOREIGN KEY (CI_ID) REFERENCES CompoundIngredient(CI_ID),
    
    CHECK (
        (CI_ID IS NOT NULL AND AI_ID IS NULL) OR
        (CI_ID IS NULL AND AI_ID IS NOT NULL)
    ),
    UNIQUE (R_ID, AI_ID),
    UNIQUE (R_ID, CI_ID)
);

CREATE TABLE Formulation (
	F_ID INT PRIMARY KEY AUTO_INCREMENT,
    CI_ID INT NOT NULL,
    Creation_Date DATE NOT NULL,
    Unit_Price INT NOT NULL CHECK (Unit_Price > 0),
    Pack_Size INT NOT  NULL CHECK (Pack_Size > 0),
    FOREIGN KEY (CI_ID) REFERENCES CompoundIngredient(CI_ID)
);

CREATE TABLE DoNotCombine (
    AI_ID1 INT NOT NULL,
    AI_ID2 INT NOT NULL,
    PRIMARY KEY (AI_ID1, AI_ID2),
    FOREIGN KEY (AI_ID1) REFERENCES AtomicIngredient(AI_ID),
    FOREIGN KEY (AI_ID2) REFERENCES AtomicIngredient(AI_ID),
    CHECK (AI_ID1 <> AI_ID2)
);

CREATE TABLE FormulationIngredient (
    F_ID INT NOT NULL,
    AI_ID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    PRIMARY KEY (F_ID, AI_ID),
    FOREIGN KEY (F_ID) REFERENCES Formulation(F_ID),
    FOREIGN KEY (AI_ID) REFERENCES AtomicIngredient(AI_ID)
);

CREATE TABLE Supplier (
    S_ID INT PRIMARY KEY,
    S_Name VARCHAR(255) NOT NULL
);

CREATE TABLE ProductBatch (
    PB_ID INT PRIMARY KEY,
    P_ID INT NOT NULL,
    M_ID INT NOT NULL,
    R_ID INT NOT NULL,
    Expiration_Date DATE,
    Quantity INT NOT NULL CHECK (Quantity >= 0),

    Product_Lot_Number VARCHAR(50) GENERATED ALWAYS AS 
		(CONCAT(CAST(P_ID AS CHAR), '-', CAST(M_ID AS CHAR), '-', CAST(PB_ID AS CHAR))) STORED,
    
    UNIQUE (Product_Lot_Number),

    FOREIGN KEY (P_ID) REFERENCES Product(P_ID),
    FOREIGN KEY (M_ID) REFERENCES Manufacturer(M_ID),
    FOREIGN KEY (R_ID) REFERENCES Recipe(R_ID)
);

CREATE TABLE IngredientBatch (
    IB_ID INT PRIMARY KEY,
    AI_ID INT NULL,
    CI_ID INT NULL,
    S_ID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity >= 0),
    Cost DECIMAL(10,2) NOT NULL CHECK (Cost >= 0),
    Expiration_Date DATE NOT NULL,

    Ingredient_Lot_Number VARCHAR(100) GENERATED ALWAYS AS 
        (CONCAT(
			CASE 
				WHEN AI_ID IS NOT NULL THEN CAST(AI_ID AS CHAR)
				ELSE CAST(CI_ID AS CHAR)
			END,
			'-',
			CAST(S_ID AS CHAR),
			'-',
			CAST(IB_ID AS CHAR))
        ) STORED,
    UNIQUE (Ingredient_Lot_Number),

    FOREIGN KEY (CI_ID) REFERENCES CompoundIngredient(CI_ID),
    FOREIGN KEY (AI_ID) REFERENCES AtomicIngredient(AI_ID),
    FOREIGN KEY (S_ID) REFERENCES Supplier(S_ID),
    
    CHECK (
        (CI_ID IS NOT NULL AND AI_ID IS NULL) OR
        (CI_ID IS NULL AND AI_ID IS NOT NULL)
    )
);

CREATE TABLE ProductIngredientBatch (
    PB_ID INT NOT NULL,
    IB_ID INT NOT NULL,
    Quantity_Used DECIMAL(10,2) NOT NULL CHECK (Quantity_Used > 0),
    PRIMARY KEY (PB_ID, IB_ID),
    FOREIGN KEY (PB_ID) REFERENCES ProductBatch(PB_ID),
    FOREIGN KEY (IB_ID) REFERENCES IngredientBatch(IB_ID)
);