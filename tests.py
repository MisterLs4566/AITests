import sqlite3
import google.generativeai as genai
import os
import numpy as np
from numpy.linalg import norm
from numpy import dot
import sys

"""Milestone 1"""

os.environ['GOOGLE_API_KEY'] = 'AIzaSyAAOnjsaZQfadHQ896oFaMuHbfHBTc0TXw'
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

connection = sqlite3.connect("db/AITests-service.db")

cursor = connection.cursor()

issues = [0, 1]
issue_hash_map = {}

cursor.execute("CREATE TABLE IF NOT EXISTS issue(issue_id, issue_title, issue_description)")
cursor.execute("""INSERT INTO issue VALUES
        (0, "IMPORTANT PROBLEM", "Die Kunden warten auf ihre Bestellung, aber nichts geht! Das System spinnt und lädt die ganze Zeit nicht!"),
        (1, "ALSO AN IMPORTANT PROBLEM", "Katzen können sprechen"),
        (1, "ALSO AN IMPORTANT PROBLEM", "Es gibt Probleme beim Drucken der Lieferscheine. Es funktioniert zwar, aber es ist so langsam, dass man von einem Problem sprechen kann")       
        """)

for issue in issues:
        score_projection = cursor.execute("SELECT issue_description FROM issue WHERE issue_id="+str(issue))
        issue_hash_map[issue] = score_projection.fetchone()[0]
        
"""Milestone 2"""

vectors_hash_map = issue_hash_map.copy()

i=-1

for issue_text in list(issue_hash_map.values()):
        i+=1
        issue_key = list(issue_hash_map.keys())[i]
        result = genai.embed_content(
        model="models/text-embedding-004", content=issue_text)
        vector = np.array(result["embedding"])
        vectors_hash_map[issue_key] = vector

vector_a = vectors_hash_map[0]
vector_b = vectors_hash_map[1]

cos_sim = dot(vector_a, vector_b) / (norm(vector_a) * norm(vector_b))
deg = (np.arccos(cos_sim)/np.pi) * 180

if(deg > 50):
        print("Es konnte leider keine semantische Ähnlichkeit hergestellt werden")
        sys.exit()
similar = list(vectors_hash_map.keys())

"""Milestone 3"""

prompt_beginning = "Finde Gemeinsamkeiten in diesen Problemen. Erstelle einen prägnanten Titel, der beide Probleme zusammenfasst und gib eine kurze Beschreibung des übergeordneten Problems an, ohne dabei zu konkret zu werden."
prompt_ending = ""
for key in similar:
        prompt_ending += issue_hash_map[key]
prompt = prompt_beginning + prompt_ending
response = model.generate_content(prompt).text
print(response)
