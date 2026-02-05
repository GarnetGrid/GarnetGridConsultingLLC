import re
import os

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' | ', raw_html)
    return cleantext

def parse_experience(file_path):
    print(f"Parsing Experience from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find "Experience" header pattern
    # Looking for >Experience<
    
    # Split by "Experience" might be too broad, but let's try to locate the neighborhood.
    # The snippet showed: <p class="...">Experience</p>
    
    # Let's find all occurrences of "Experience" and grab a chunk of text after it.
    
    indices = [m.start() for m in re.finditer(r'>Experience<', content)]
    
    results = []
    
    for idx in indices:
        print(f"Found 'Experience' at index {idx}")
        # Look ahead 5000 chars to see structure
        chunk = content[idx:idx+5000]
        print("--- DEBUG CHUNK ---")
        print(chunk[:1000]) # Print first 1000 chars of chunk
        print("--- END DEBUG CHUNK ---")
        
        # Try finding looking for typical LinkedIn archive structure:
        # Often div class="p-4" or similar generic classes
        # Let's search for "Garnet Grid" in this chunk to see how it's wrapped
        
        if "Garnet Grid" in chunk:
            print("FOUND Garnet Grid in this chunk!")

        # In minified HTML, lists might be <li class="..."> or just nested divs
        # Let's try to grab text by looking for date patterns directly in the chunk
        
        # Regex to find "Title at Company" pattern or similar
        # "President at Garnet Grid Consulting LLC"
        
        # Let's simplisticly extract all text from the chunk and print it
        clean_chunk = clean_html(chunk)
        print(f"Cleaned chunk preview: {clean_chunk[:500]}")
        
        # New strategy: Return the cleaned text lines that contain dates
        parts = [p.strip() for p in clean_chunk.split('|') if p.strip()]
        for p in parts:
             # Heuristic: Contains date or duration
             if (re.search(r'20\d\d', p) or "Present" in p) and len(p) < 200:
                  results.append(p)
                 
    return results

def parse_skills(file_path):
    print(f"Parsing Skills from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Simply clean all HTML and look for a list of skills if possible
    # Or look for "Skills" header
    
    text = clean_html(content)
    # Split by pipes
    parts = [p.strip() for p in text.split('|') if p.strip()]
    
    # Try to find "Skills" marker
    try:
        start = parts.index("Skills")
        return parts[start:start+100]
    except ValueError:
        return parts[:100]

def main():
    base_dir = "linkedin_data"
    exp_file = os.path.join(base_dir, "Jakub Rezayev _ LinkedIn.html")
    exp_all_file = os.path.join(base_dir, "Jakub Rezayev _ LinkedInall.html")
    skills_file = os.path.join(base_dir, "Jakub Rezayev _ LinkedInskills.html")
    
    print("--- EXPERIENCE (Main) ---")
    try:
        exps = parse_experience(exp_file)
        seen = set()
        for i, e in enumerate(exps):
            if e not in seen:
                print(f"[{i}] {e}")
                print("-" * 20)
                seen.add(e)
    except Exception as e:
        print(f"Error parsing main experience: {e}")

    print("\n--- EXPERIENCE (All) ---")
    try:
        exps = parse_experience(exp_all_file)
        seen = set()
        for i, e in enumerate(exps):
            if e not in seen:
                print(f"[{i}] {e}")
                print("-" * 20)
                seen.add(e)
    except Exception as e:
        print(f"Error parsing all experience: {e}")

    print("\n--- SKILLS ---")
    try:
        s_lines = parse_skills(skills_file)
        print(" | ".join(s_lines))
    except Exception as e:
        print(f"Error parsing skills: {e}")

    print("\n--- CERTIFICATIONS ---")
    try:
        certs_file = os.path.join(base_dir, "Jakub Rezayev _ LinkedInccerts.html")
        c_lines = parse_skills(certs_file) # Re-use skills parser for now as it just dumps text
        print(" | ".join(c_lines))
    except Exception as e:
        print(f"Error parsing certs: {e}")

if __name__ == "__main__":
    main()
