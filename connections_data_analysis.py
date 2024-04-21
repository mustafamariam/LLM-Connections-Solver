# -*- coding: utf-8 -*-
"""
**Connections Category Analysis**
This script conducts an analysis of the Connections Answers.

*   Gets summary statistics of the dataset size & number of unique words in the Answers and Categories.
*   Gets the most common words in the Answers and Categories.
*   Conducts a KMeans clustering on the Categories for semantic analysis.

Assumes downloaded: categoriesConn.csv, connectionsRes.csv
Dependencies: pandas, sklearn
Used ChatGPT to obtain KMeans clustering code.
"""

import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from collections import defaultdict

"""
Get word counts
Parameters: 
- df: .csv file as DataFrame object
- type: "answer" or "category"
Returns:
- word_count: dictionary of words & counts
"""
def get_word_counts(df, type):
    word_count = {}

    for index, row in df.iterrows():
      if type =="answer":
        texts = ast.literal_eval(row[0])
        for text in texts:
          if text in word_count:
              word_count[text] += 1
          else:
              word_count[text] = 1
      else:
        text = row[0]
        if text in word_count:
              word_count[text] += 1
        else:
            word_count[text] = 1

    return word_count

"""
Get repeating words
Parameters: 
- word_count: dictionary of words & counts
Returns:
- repeats: list of tuples containing word counts
"""
def get_repeats(word_counts):
  repeats = []

  for word in word_counts.keys():
    if word_counts[word] > 1:
      repeats.append((word, word_counts[word]))

  return repeats

"""
Get most common words
Parameters: 
- word_count: dictionary of words & counts
- n (optional): number of most common words to output
  default 5.
Returns:
- most_common_words: dictionary of n most common words
"""
def get_most_common_words(word_counts, n=5):
    word_counts_sorted = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    most_common_words = word_counts_sorted[:n]
    return most_common_words

"""
Get KMeans clusters
Parameters: 
- word_count: dictionary of words & counts
- max_clusters (optional): maximum number of clusters
  default 20.
Returns:
- clusters: a dictionary of clusters & labels
"""
def get_clusters(word_counts, max_clusters=20):
    words = [word for word, count in word_counts.items() for _ in range(count)]
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(words)

    # Perform silhouette score algorithm to get optimal cluster amount
    best_score = -1
    best_k = 0
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        labels = kmeans.labels_
        score = silhouette_score(X, labels)
        if score > best_score:
            best_score = score
            best_k = k

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    kmeans.fit(X)
    cluster_labels = kmeans.labels_

    clusters = defaultdict(list)
    for word, label in zip(words, cluster_labels):
        clusters[label].append(word)

    return clusters

"""
Print cluster sizes
Parameters: 
- clusters: a dictionary of clusters & labels
"""
def print_cluster_sizes(clusters):
  for id, words in clusters.items():
      print(f"Cluster {id + 1}: {len(words)} items")


# Get all clusters above min_size.
# Option to remove_largest cluster
"""
Print cluster information, including id and words
Parameters: 
- clusters: a dictionary of clusters & labels
- min_size: (optional) int of minimum cluster size
  default 10.
- remove_largest: (optional) boolean of whether to
  ignore largest cluster default True.
"""
def print_cluster_info(clusters, min_size=10, remove_largest=True):
  if remove_largest:
    max_length = max(len(words) for words in clusters.values())
  else:
    max_length = -1
  for id, words in clusters.items():
      if len(words) >=min_size and len(words) != max_length:
        print(f"Cluster {id + 1}:")
        for word in words:
            print(f" - {word}")

if __name__ == "__main__":
   
   # Sample use case:

   # Import the Categories and Answers datasets
   categories_df = pd.read_csv('categoriesConn.csv')
   answers_df = pd.read_csv('connectionsRes.csv')

   # Debugging for extra header/names
   header = pd.DataFrame([answers_df.columns.tolist()], columns=answers_df.columns)
   answers_df = pd.concat([header, answers_df], ignore_index=True)
   answers_df.columns = range(len(answers_df.columns))
   categories_df.columns = range(len(categories_df.columns))

   # Get summary statistics for Categories
   categories_size = categories_df.shape[0]
   categories_counts = get_word_counts(categories_df, "category")
   categories_repeats = len(get_repeats(categories_counts))
   print("Total number of Category words: " + str(categories_size) + "\n")
   print("Number of repeats in Categories: " + str(categories_repeats) + "\n")
   print("Percentage of unique Category words: " + str(1 - (categories_repeats/categories_size))+ "\n")
   
   # Get summary statistics for Answers
   answers_size = answers_df.shape[0] * 16
   answers_counts = get_word_counts(answers_df, "answer")
   answers_repeats = len(get_repeats(answers_counts))
   print("Total number of Answer words: " + str(answers_size)+ "\n")
   print("Number of repeats in Answers: " + str(answers_repeats)+ "\n")
   print("Percentage of unique Answer words: " + str(1 - (answers_repeats/(answers_size)))+ "\n")

   # Get 5 most common Category words
   common_categories = get_most_common_words(categories_counts)
   print("The 5 most common Category words are:" + "\n")
   print(common_categories)
   print("\n")

   # Get 10 most common Answer words
   common_answers = get_most_common_words(answers_counts, 10)
   print("The 10 most common Answer words are:" + "\n")
   print(common_answers)
   print("\n")

   # Print Category clusters sizes
   print("Category sizes:"+ "\n")
   categories_clusters = get_clusters(categories_counts)
   print_cluster_sizes(categories_clusters)
   print("\n")
   
   # Get Category clusters information
   print("Category clusters:"+ "\n")
   print_cluster_info(categories_clusters, 10, True)

