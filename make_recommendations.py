import pickle
import numpy as np

print("Loading similarity.pkl...")

movies = pickle.load(open("movie_dict.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

print("Creating compact recommendations...")

recommendations = {}

for i in range(len(movies["title"])):
    distances = similarity[i]

    top_indices = np.argsort(distances)[::-1]

    top_indices = [
        index for index in top_indices
        if index != i
    ][:5]

    recommendations[i] = top_indices

with open("recommendations.pkl", "wb") as f:
    pickle.dump(recommendations, f)

print("Done!")
print("recommendations.pkl created successfully.")