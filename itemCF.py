import math
from operator import itemgetter
import random

def initialize(dataset):
    allItems = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    itemsAmount = len(allItems)
    userAmount = 5
    user_items = dict()
    for i in range(100):
        u = random.randint(1, userAmount)
        pos = random.randint(0,itemsAmount - 1)
        if user_items.has_key(u) == False:
            user_items[u] = dict()
        while user_items[u].has_key(allItems[pos]):
            pos = (pos + 1) % itemsAmount
        like = random.random()
        user_items[u][allItems[pos]] = like
        dataset.append((u, allItems[pos], like))
    return dataset

def splitDataset(dataset, k, round):
    per_len = len(dataset) / k
    train = []
    validation = []
    for i in range(len(dataset)):
        if (round - 1) * per_len <= i and i < round * per_len:
            validation.append(dataset[i])
        else:
            train.append(dataset[i])
    #print 'train_len = %d, validation_len = %d' % (len(train), len(validation))
    return train, validation

def getInvertedIndex(dataset):
    inverted_index = dict()
    for u, item, like in dataset:
        if inverted_index.has_key(u) == False:
            inverted_index[u] = dict()
        inverted_index[u][item] = like
    return inverted_index    

def getItemSimilarity(train_user_items):
    itemSimilarityTable = dict()
    N = dict()
    for u, items in train_user_items.items():
        for i in items.keys():
            if N.has_key(i):
                N[i] += 1
            else:
                N[i] = 1
            if itemSimilarityTable.has_key(i) == False:
                itemSimilarityTable[i] = dict()
            for j in items.keys():
                if i != j:
                    if itemSimilarityTable[i].has_key(j):
                        itemSimilarityTable[i][j] += 1
                    else:
                        itemSimilarityTable[i][j] = 1
    
    for i, itemlist in itemSimilarityTable.items():
        for j, ij in itemlist.items():
            itemSimilarityTable[i][j] = ij / math.sqrt(N[i] * N[j])

    return itemSimilarityTable

def getItemPopularity(train_user_items):
    item_popularity_table = dict()
    for u, items in train_user_items.items():
        for item in items.keys():
            if item_popularity_table.has_key(item) == False:
                item_popularity_table[item] = 0
            item_popularity_table[item] += 1
    return item_popularity_table

def recommend(user, items, item_similarity_table, N):
    R = dict()
    for i, w in items.items():
        for item, s in sorted(item_similarity_table[i].items(), key=itemgetter(1), reverse=True):
            if item in items.keys():
                continue
            if R.has_key(item) == False:
                R[item] = 0
            R[item] += w * s
    return sorted(R.items(), key=itemgetter(1), reverse=True)[0:N]

def getEvaluation(train_user_items, validation_user_items, item_similarity_table, item_popularity_table):
    hit = 0.0
    precision_all = 0.0
    recall_all = 0.0
    all_items = set()
    recommended_items = set()
    popularity = 0.0
    for u, items in train_user_items.items():
        for item in items.keys():
            all_items.add(item)
        recommendation_items = recommend(u, items, item_similarity_table, 5)
        for item, w in recommendation_items:
            recommended_items.add(item)
            popularity += item_popularity_table[item]
        if validation_user_items.has_key(u) == False:
            hit += 0.0
            precision_all += len(recommendation_items)
            recall_all += 0.0
            continue
        for item, like in recommendation_items:
            if item in validation_user_items[u].keys():
                hit += 1.0
        precision_all += len(recommendation_items)
        recall_all += len(validation_user_items[u])
    
    precision = hit / (precision_all * 1.0)
    recall = hit / (recall_all * 1.0)
    coverage = (len(recommended_items) * 1.0) / (len(all_items) * 1.0)
    popularity = popularity / (precision_all * 1.0)
    
    print 'precision = %f, recall = %f, coverage = %f, popularity = %f' % (precision, recall, coverage, popularity)
    return precision, recall, coverage, popularity

def evaluateItemCF(dataset):
    length = len(dataset)
    k = int(math.floor(math.sqrt(length)))
    while k > 0:
        if length % k == 0:
            break
        k -= 1
    recall_avg = 0.0
    precision_avg = 0.0
    coverage_avg = 0.0
    popularity_avg = 0.0
    
    for round in range(1, k + 1):
        train, validation = splitDataset(dataset, k, round)
        train_user_items = getInvertedIndex(train)
        item_similarity_table = getItemSimilarity(train_user_items)
        item_popularity_table = getItemPopularity(train_user_items)
        validation_user_items = getInvertedIndex(validation)
        print 'Round %d' % round
        precision, recall, coverage, popularity = getEvaluation(train_user_items, validation_user_items, 
                                                    item_similarity_table, item_popularity_table)
        recall_avg += recall
        precision_avg += precision
        coverage_avg += coverage
        popularity_avg += popularity
        
    recall_avg = recall_avg / (k * 1.0)
    precision_avg = precision_avg / (k * 1.0)
    coverage_avg = coverage_avg / (k * 1.0)
    popularity_avg = popularity_avg / (k * 1.0)
    
    return precision_avg, recall_avg, coverage_avg, popularity_avg
          
dataset = []
dataset = initialize(dataset)
precision, recall, coverage, popularity = evaluateItemCF(dataset)
print 'Average'
print "precision = %f, recall = %f, coverage = %f, popularity = %f" % (precision, recall, coverage, popularity)
