# Prepared Meal Inventory Manager

A database-backed inventory management system for prepared meals, built with Python and MySQL.

## Setup Instructions

1. **Connect to NC State VPN**  
   - Download and connect to the [NC State VPN](https://ncsu.service-now.com/sp/en?id=kb_article&sys_id=232ec94d97e7f154a1e5f0c0f053af27).  
   - You must be connected or on NC State wifi to access the remote database.

2. **Configure Database Credentials**  
   - Run the following command to duplicate the configuration template:
     ```bash
     cp config/config.json.template config/config.json
     ```
   - Open `config/config.json` and replace the placeholder fields with your actual credentials:
  
3. **Install Requirements**
   - Python 3.13+
   - pip packages listed in requirements.txt
     These can be installed with:
     ```pip install -r requirements.txt```

5. **Run the Program**  
   - Once configured, install any required packages and execute the main program:
     ```bash
     python src/inventory_management.py
     ```
   - The program automatically loads init.sql and data.sql on startup. You will see the following menu:
     ```
     Select role: [1] Manufacturer [2] Supplier [3] General (Viewer) [4] View Queries [0] Exit
     Enter choice:
     ```
   - Once the role is selected, you will need to log in with one of the stored user ids with the appropriate role. Manufacturers have all roles, Suppliers have Supplier and Viewer, Viewers only have Viewer. All users can view queries. The user ids can be located in the data.sql file.
   - Each role has a sub menu to select actions:
     ```
     [Manufacturer Actions]
      [1] Define/Update Product
      [2] Define/Update Product BOM
      [3] Record Ingredient Receipt
      [4] Create Product Batch
      [5] Reports: On-hand | Nearly-out-of-stock | Almost-expired
      [6] (Grad) Recall/Traceability
      [0] Back/Exit
      ```
     ```
     [Supplier Actions]
      [1] Declare Ingredients Supplied
      [2] Maintain Formulations (materials, price, pack, effective dates)
      [3] Create Ingredient Batch (for supplied ingredients)
      [0] Back/Exit
      ```
     ```
     [Viewer Actions]
      [1] Product Ingredient List (with nested materials, ordered by quantity)
      [2] Compare Products for Incompatibilities
      [0] Back/Exit
      ```
---
