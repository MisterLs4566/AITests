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

connection = sqlite3.connect("C:\\Users\\asolo\\OneDrive\\Dokumente\\Linus\\AITests\\db\AITests-service.db")

cursor = connection.cursor()

issues = [4, 7, 8]
issue_hash_map = {}

cursor.execute("CREATE TABLE IF NOT EXISTS issue(issue_id, issue_title, issue_description)")
cursor.execute("""INSERT INTO issue VALUES
        (4, "IMPORTANT PROBLEM", "Lieferscheine werden durch defektes Ticketing System nicht gedruckt"),
        (7, "Probleme", "Katzen essen Hunde"),
        (8, "ALSO AN IMPORTANT PROBLEM", "Scheine werden durch defektes Ticketing System nicht gedruckt")       
        """)

for issue in issues:
        description_projection = cursor.execute("SELECT issue_description FROM issue WHERE issue_id="+str(issue))
        issue_hash_map[issue] = description_projection.fetchone()[0]
        
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

#print(len(vectors_hash_map))

# Matrixvergleich
similarity = []
for x in range(0, len(list(vectors_hash_map.values()))):
        for y in range(0, len(list(vectors_hash_map.values()))):
                #print(list(vectors_hash_map.keys())[x])
                vector_a = list(vectors_hash_map.values())[x]
                #print(list(vectors_hash_map.keys())[y])
                vector_b = list(vectors_hash_map.values())[y]
                #print(vector_b)
                cos_sim = round(dot(vector_a, vector_b) / (norm(vector_a) * norm(vector_b)), 9)
                #print(cos_sim)
                deg = (np.arccos(cos_sim)/np.pi) * 180
                #print(deg)
                if(y==0):
                        #print(list(issue_hash_map.keys())[x])
                        #print(list(issue_hash_map.values())[x])
                        similarity.append({list(issue_hash_map.keys())[x] : list(issue_hash_map.values())[x]})
                if(deg < 25):
                        #print(list(issue_hash_map.keys())[y])
                        #print("Hallo " + list(issue_hash_map.values())[y])
                        similarity[x][list(issue_hash_map.keys())[y]] = list(issue_hash_map.values())[y]

"""Milestone 3"""

result = []
prompt_ending = ""
prompt = ""
#print(similarity)
#print(len(similarity))
#print(similarity)

#sort dictionarys by keys
x = 0
for group in similarity:
        similarity[x] = dict(sorted(group.items()))
        x+=1
# delete similar groups:
for x in range(0, len(similarity)):
        for y in range(0, len(similarity)):
                if(similarity[x] == similarity[y] and x!=y):
                        similarity[x] = {0:"gleiche Gruppe: "+str(x)}

#print(similarity)

prompt_beginning = "Gib mir einen einzigen zusammenfassenden Titel aus, der für diese Probleme passt. Nicht mehr als einen Titel!"


for group in similarity:
        if(len(group)>1):
                for key in group:
                        prompt_ending = prompt_ending + str(group[key]) + ", "
                        prompt = prompt + prompt_beginning + prompt_ending
                response = "Titel: " + model.generate_content(prompt).text + " -> "+str(group)
                result.append(response)
                prompt_ending = ""
                prompt = ""

print(result)
 