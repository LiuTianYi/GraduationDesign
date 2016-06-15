# -*- coding: utf-8 -*-
from math import floor
import random
from operator import itemgetter
from numpy.random.mtrand import shuffle

def getRawLog(N, user_amount, item_amount, tag_amount):
    'Get raw log whose each record is (u, i, t)'
    if N <= 0:
        return []
    
    raw_log = []
    
    for uid in range(user_amount):
        for i in range(N):
            random_u = 'user ' + str(uid)
            random_i = 'item ' + str((int)(random.random() * item_amount))
            random_t = 'tag ' + str((int)(random.random() * tag_amount))
            raw_log.append((random_u, random_i, random_t))
    
    shuffle(raw_log)
    return raw_log

def getUserTags(raw_log):
    'Get user-tags records from raw_log'
    if raw_log == None or len(raw_log) == 0:
        return None
    
    user_tags = {}
    
    for u, i, t in raw_log:
        if user_tags.has_key(u) == False:
            user_tags[u] = {}
        if user_tags[u].has_key(t) == False:
            user_tags[u][t] = 0
        user_tags[u][t] += 1
    
    return user_tags

def getTagItems(raw_log):
    'Get tag-items records from raw_log'
    if raw_log == None or len(raw_log) == 0:
        return None
    
    tag_items = {}
    
    for u, i, t in raw_log:
        if tag_items.has_key(t) == False:
            tag_items[t] = {}
        if tag_items[t].has_key(i) == False:
            tag_items[t][i] = 0
        tag_items[t][i] += 1
        
    return tag_items

def getUserItems(raw_log):
    'Get user-items records from raw_log'
    if raw_log == None or len(raw_log) == 0:
        return None
    
    user_items = {}
    
    for u, i, t in raw_log:
        if user_items.has_key(u) == False:
            user_items[u] = {}
        if user_items[u].has_key(i) == False:
            user_items[u][i] = 0
        user_items[u][i] += 1
    
    return user_items

def getItemUsers(raw_log):
    'Get item-users records from raw log'
    if raw_log == None or len(raw_log) == 0:
        return None
    
    item_users = {}
    
    for u, i, t in raw_log:
        if item_users.has_key(i) == False:
            item_users[i] = {}
        if item_users[i].has_key(u) == False:
            item_users[i][u] = 0
        item_users[i][u] += 1
    
    return item_users

def getUsers(raw_log):
    'Get all users from log'
    users = set()
    for record in raw_log:
        if record[0] not in users:
            users.add(record[0])
    return users

def recommendByTag(user, iteracted_items, user_tags, tag_items, N):
    'Recommend N items for user by tags'
    if user == None or user_tags == None or tag_items == None or N <= 0:
        return None
    
    recommend_list = {}
    
    user_favorite_tags = sorted(user_tags[user].items(), key=itemgetter(1), reverse=True)
    for t, count1 in user_favorite_tags:
        tag_popular_items = sorted(tag_items[t].items(), key=itemgetter(1), reverse=True)
        for i, count2 in tag_popular_items:
            if i not in iteracted_items.keys():
                if recommend_list.has_key(i) == False:
                    recommend_list[i] = 0
                recommend_list[i] += count1 * count2
    
    return sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]

def displayRecommendList(recommend_list):
    for item in recommend_list:
        print item

def getPrecision(recommend_list, real_list):
    'Get precision of recommendation'
    if len(recommend_list) == 0:
        return 0
    
    hit = 0.0
    for item in recommend_list:
        if item in real_list:
            hit += 1
    precision = hit / len(recommend_list)
    return precision

def getRecall(recommend_list, real_list):
    'Get recall of recommendation'
    if len(real_list) == 0:
        return 0
    
    hit = 0.0
    for item in recommend_list:
        if item in real_list:
            hit += 1
    recall = hit / len(real_list)
    return recall

def getPopularity(item_list, item_users_records):
    'Get popularity from item list'
    popularity = 0.0
    if len(item_list) == 0:
        return popularity
    for item in item_list:
        if item_users_records.has_key(item) == True:
            popularity += len(item_users_records[item])
    popularity /= len(item_list)
    return popularity

def cross_validation(k, dataset, item_amount):
    'Calculate precision and recall on data set with k-fold cross validation'
    users = getUsers(dataset)
    all_recommend_items_set = set()
    avg_precision = 0.0
    avg_recall = 0.0
    avg_coverage = 0.0
    avg_popularity = 0.0
    
    part = len(dataset) / k
    for user in users:
        for turn in range(k):
            start = turn * part
            end = start + part
            train_set = dataset[0:start] + dataset[end:]
            test_set = dataset[start:end]
            
            user_tags = getUserTags(train_set)
            tag_items = getTagItems(train_set)
            user_items = getUserItems(train_set)
            item_users = getItemUsers(train_set)
            
            N = 20
            
            if user_items.has_key(user) == False:
                recommend_list = []
            else:
                recommend_items = recommendByTag(user, user_items[user], user_tags, tag_items, N)
                recommend_list = []
                for i in recommend_items:
                    recommend_list.append(i[0])
                all_recommend_items_set = all_recommend_items_set.union(set(recommend_list))
                avg_popularity += getPopularity(recommend_list, item_users)
                #displayRecommendList(recommend_list)
            
            test_user_items_records = getUserItems(test_set)
            if test_user_items_records.has_key(user) == False:
                real_list = []
            else:
                real_list = list(test_user_items_records[user].keys())
                
            precision = getPrecision(recommend_list, real_list)
            recall = getRecall(recommend_list, real_list)
            
            avg_precision += precision
            avg_recall += recall
    
        print 'recommend for %s : %s' % (user, recommend_list)
        
    avg_precision = avg_precision / (len(users) * k)
    avg_recall = avg_recall / (len(users) * k)    
    avg_coverage = (len(all_recommend_items_set) * 1.0) / (item_amount * 1.0)
    avg_popularity = avg_popularity / (len(users) * k)   
    print 'precision is %f, recall is %f, coverage is %f, popularity is %f' % (avg_precision, avg_recall, avg_coverage, avg_popularity)

N = 50
user_amount = 20
item_amount = 80
tag_amount = 10    
raw_log = getRawLog(N,user_amount,item_amount,tag_amount)
cross_validation(5, raw_log, item_amount)          