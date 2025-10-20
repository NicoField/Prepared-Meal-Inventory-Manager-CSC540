# Prepared Meal Inventory Manager

A database-backed inventory management system for prepared meals, built with Python and MySQL.

## Setup Instructions

1. **Connect to NC State VPN**  
   - Download and connect to the [NC State VPN](https://ncsu.service-now.com/sp/en?id=kb_article&sys_id=232ec94d97e7f154a1e5f0c0f053af27).  
   - You must be connected or on NC State wifi to access the remote database.

2. **Configure Database Credentials**  
   - Run the following command to duplicate the configuration template:
     ```bash
     cp config/db_config.json.template config/db_config.json
     ```
   - Open `config/db_config.json` and replace the placeholder fields with your actual credentials:

3. **Run the Program**  
   - Once configured, execute the main program:
     ```bash
     python src/inventory_management.py
     ```

---
