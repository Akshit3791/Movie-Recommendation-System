import pickle
import gzip

print("File choti ho rahi hai, kripya 1-2 minute wait karein...")
# Purani 176MB ki file load karna
similarity = pickle.load(open('similarity.pkl', 'rb'))
# Nayi compressed file save karna
pickle.dump(similarity, gzip.open('similarity_compressed.pkl.gz', 'wb'))
print("Done! File compress ho gayi hai.")