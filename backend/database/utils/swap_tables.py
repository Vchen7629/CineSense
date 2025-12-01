# Swap staging and production tables
def swap_tables(cursor, staging_table, prod_table):
    print(f"Swapping {staging_table} <-> {prod_table}...")

    temp_table = f"{prod_table}_temp"

    # Rename in transaction
    cursor.execute(f"ALTER TABLE {prod_table} RENAME TO {temp_table}")
    cursor.execute(f"ALTER TABLE {staging_table} RENAME TO {prod_table}")
    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {staging_table}")

    print(f"Tables swapped successfully")