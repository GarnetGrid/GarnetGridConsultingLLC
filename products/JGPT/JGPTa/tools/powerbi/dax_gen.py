import argparse
import sys

def generate_dax(measure_name, base_column):
    """Generates standard time intelligence measures for a base metric."""
    
    measures = {}
    
    # Base Measure (if needed, usually user provides existing measure name)
    # If base_column looks like a column reference 'Table[Col]', we create a SUM first
    base_measure = measure_name
    if "[" in base_column:
        base_measure = f"Sum of {measure_name}"
        measures[base_measure] = f"SUM({base_column})"

    # YTD
    measures[f"{base_measure} YTD"] = f"CALCULATE([{base_measure}], DATESYTD('Date'[Date]))"
    
    # PY (Previous Year)
    measures[f"{base_measure} PY"] = f"CALCULATE([{base_measure}], SAMEPERIODLASTYEAR('Date'[Date]))"
    
    # YoY Growth
    measures[f"{base_measure} YoY"] = f"[{base_measure}] - [{base_measure} PY]"
    
    # YoY %
    measures[f"{base_measure} YoY %"] = f"DIVIDE([{base_measure} YoY], [{base_measure} PY])"
    
    # MOM (Month over Month)
    measures[f"{base_measure} MoM"] = f"[{base_measure}] - CALCULATE([{base_measure}], DATEADD('Date'[Date], -1, MONTH))"

    return measures

if __name__ == "__main__":
    print("📊 Garnet Grid DAX Generator 📊")
    print("--------------------------------")
    
    if len(sys.argv) < 2:
        name = input("Enter Measure Name (e.g., Total Sales): ")
        col = input("Enter Base Column or Measure (e.g., 'Sales'[Amount] or [Total Sales]): ")
    else:
        name = sys.argv[1]
        col = sys.argv[2]
        
    results = generate_dax(name, col)
    
    print("\n✅ Generated DAX Measures:\n")
    for m_name, dax in results.items():
        print(f"{m_name} = \n    {dax}\n")
