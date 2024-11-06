import sqlite3
import google.generativeai as genai
import os
import numpy as np
from numpy.linalg import norm
from numpy import dot
import sys

os.environ['GOOGLE_API_KEY'] = ''
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

connection = sqlite3.connect("C:\\Users\\asolo\\OneDrive\\Dokumente\\Linus\\AITests\\db\AITests-service.db")

cursor = connection.cursor()

issues = [1, 2, 3]
issue_hash_map = {}

cursor.execute("CREATE TABLE IF NOT EXISTS issue(issue_id, issue_title, issue_description)")
cursor.execute("""INSERT INTO issue VALUES
        (1, "Issue1", "issue description 1"),
        (2, "Issue2", "issue description 2),
        (3, "Issue3", "issue description 3")       
        """)

for issue in issues:
        description_projection = cursor.execute("SELECT issue_description FROM issue WHERE issue_id="+str(issue))
        issue_hash_map[issue] = description_projection.fetchone()[0]

vectors_hash_map = issue_hash_map.copy()

i=-1

for issue_text in list(issue_hash_map.values()):
        i+=1
        issue_key = list(issue_hash_map.keys())[i]
        result = genai.embed_content(
        model="models/text-embedding-004", content=issue_text)
        vector = np.array(result["embedding"])
        vectors_hash_map[issue_key] = vector

# Matrixvergleich
similarity = []
for x in range(0, len(list(vectors_hash_map.values()))):
        for y in range(0, len(list(vectors_hash_map.values()))):
                vector_a = list(vectors_hash_map.values())[x]
                vector_b = list(vectors_hash_map.values())[y]
                cos_sim = round(dot(vector_a, vector_b) / (norm(vector_a) * norm(vector_b)), 9)
                deg = (np.arccos(cos_sim)/np.pi) * 180
                if(y==0):
                        similarity.append({list(issue_hash_map.keys())[x] : list(issue_hash_map.values())[x]})
                if(deg < 25):
                        similarity[x][list(issue_hash_map.keys())[y]] = list(issue_hash_map.values())[y]

result = []
prompt_ending = ""
prompt = ""
x = 0
for group in similarity:
        similarity[x] = dict(sorted(group.items()))
        x+=1
for x in range(0, len(similarity)):
        for y in range(0, len(similarity)):
                if(similarity[x] == similarity[y] and x!=y):
                        similarity[x] = {0:"gleiche Gruppe: "+str(x)}
prompt_beginning = "Please provide a summary title and a detailed description that captures the essence of the related issues mentioned. The summary title should be approximately 50 characters long, and the description should be around 100-150 words in length: "

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
 
