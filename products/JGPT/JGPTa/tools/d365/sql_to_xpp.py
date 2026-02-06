import re
import sys

def convert_sql_to_xpp(sql_query):
    """
    Converts a basic SQL SELECT statement to X++ select statement.
    Handles: SELECT fields FROM table WHERE condition
    """
    # Normalize whitespace
    sql = " ".join(sql_query.split()).strip()
    
    # Basic regex parsing (very naive, assumes simple structure)
    # Match: SELECT (fields) FROM (table) [WHERE (condition)]
    match = re.search(r"SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?", sql, re.IGNORECASE)
    
    if not match:
        return "// Error: Could not parse SQL. Ensure it is a simple 'SELECT fields FROM table WHERE ...' format."
    
    fields = match.group(1).strip()
    table = match.group(2).strip()
    where_clause = match.group(3)
    
    variable_name = table.lower() + "Table"
    
    # Build X++
    xpp = f"{table} {variable_name};\n\n"
    xpp += f"select forcePlaceholders {variable_name}"
    
    # Handle fields (X++ selects usually fetch the whole buffer or use field list)
    if fields != "*":
        # In X++, we don't typically list fields in the 'select' header unless doing a field list selection
        # For simplicity, this tool assumes buffer selection, but adds a comment
        xpp += f" // Fields: {fields}"
    
    # Handle WHERE
    if where_clause:
        # Simple logical operator conversion
        where_clause = where_clause.replace(" AND ", " && ").replace(" OR ", " || ").replace("=", "==")
        # Fix assignment vs equality (naive)
        where_clause = re.sub(r'(?<!=)=(?!=)', ' == ', where_clause) # replace single = with ==
        
        xpp += f"\n    where {variable_name}.{where_clause}"
    
    xpp += ";"
    
    return xpp

if __name__ == "__main__":
    print("🏢 SQL to X++ Converter 🏢")
    print("--------------------------")
    
    sql_input = ""
    if len(sys.argv) > 1:
        sql_input = sys.argv[1]
    else:
        print("Enter SQL Query (or 'exit'):")
        sql_input = input("> ")
        
    if sql_input:
        res = convert_sql_to_xpp(sql_input)
        print("\n[X++ Output]:\n")
        print(res)
        print("\n")
