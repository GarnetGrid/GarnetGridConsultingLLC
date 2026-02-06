import json
import sys
import os

def scan_measures(file_path):
    print(f"📖 Scanning {file_path} for measures...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Traverse complex PBI object model (simplified path)
        # Usually: model -> tables -> measures
        model = data.get('model', {})
        tables = model.get('tables', [])
        
        count = 0
        for t in tables:
            t_name = t.get('name')
            measures = t.get('measures', [])
            for m in measures:
                m_name = m.get('name')
                m_expression = m.get('expression', '')
                if isinstance(m_expression, list):
                    m_expression = "\n".join(m_expression)
                
                print(f"\n### [{t_name}] {m_name}")
                print("```dax")
                print(m_expression)
                print("```")
                count += 1
                
        print(f"\n✅ Found {count} measures.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doc_measures.py <model.bim or schema.json>")
    else:
        scan_measures(sys.argv[1])
