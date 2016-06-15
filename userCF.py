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

def getInversedIndex(dataset):
    inversed_index = dict()
    for u, item, like in dataset:
        if inversed_index.has_key(u) == False:
            inversed_index[u] = dict()
        inversed_index[u][item] = like
    return inversed_index    

def getUserSimilarity(train):
    train_item_users = dict()
    userSimilarityTable = dict()
    N = dict()
    
    for u, item, like in train:
        if train_item_users.has_key(item) == False:
            train_item_users[item] = set()
        train_item_users[item].add(u)
    
    for i, users in train_item_users.items():
        for u1 in users:
            if N.has_key(u1) == False:
                N[u1] = 0
            N[u1] += 1
            if userSimilarityTable.has_key(u1) == False:
                userSimilarityTable[u1] = dict()
            for u2 in users:
                if u1 != u2:
                    if userSimilarityTable[u1].has_key(u2) == False:
                        userSimilarityTable[u1][u2] = 0
                    userSimilarityTable[u1][u2] += 1
    
    for u1, users in userSimilarityTable.items():
        for u2 in users.keys():
            userSimilarityTable[u1][u2] = userSimilarityTable[u1][u2] / math.sqrt(N[u1] * N[u2])
    
    return userSimilarityTable

def getItemPopularity(train_user_items):
    item_popularity_table = dict()
    for u, items in train_user_items.items():
        for item in items.keys():
            if item_popularity_table.has_key(item) == False:
                item_popularity_table[item] = 0
            item_popularity_table[item] += 1
    return item_popularity_table

def recommend(user, train_user_items, user_similarity_table, N):
    R = dict()
    interacted_items = train_user_items[user]
    for u, simi in sorted(user_similarity_table[user].items(), key=itemgetter(1), reverse=True):
        items = train_user_items[u]
        for i, like in items.items():
            if interacted_items.has_key(i) == False:
                R[i] = 0
                R[i] += simi * like
    
    return sorted(R.items(), key=itemgetter(1), reverse=True)[0:N]

def getEvaluation(train_user_items, validation_user_items, user_similarity_table, item_popularity_table):
    hit = 0.0
    precision_all = 0.0
    recall_all = 0.0
    all_items = set()
    recommended_items = set()
    popularity = 0.0
    
    for u, items in train_user_items.items():
        for item in items.keys():
            all_items.add(item)
        recommendation_items = recommend(u, train_user_items, user_similarity_table, 5)
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

def evaluateUserCF(dataset):
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
        train_user_items = getInversedIndex(train)
        user_similarity_table = getUserSimilarity(train)
        item_popularity_table = getItemPopularity(train_user_items)
        validation_user_items = getInversedIndex(validation)
        print 'Round %d' % round
        precision, recall, coverage, popularity = getEvaluation(train_user_items, validation_user_items, 
                                                    user_similarity_table, item_popularity_table)
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
precision, recall, coverage, popularity = evaluateUserCF(dataset)
print 'Average'
print "precision = %f, recall = %f, coverage = %f, popularity = %f" % (precision, recall, coverage, popularity)
