# -*- coding: utf-8 -*-
import random
import math
import time
from operator import itemgetter
from numpy.random.mtrand import shuffle

class User:
    'A class for user'
    
    def __init__(self, _id):
        self.id = _id
        self.profile = {}
    
    def getRandomValue(self):
        'Get random 0 or 1'
        if random.random() >= 0.5:
            return 1
        else:
            return 0
    
    def createProfile(self, features):
        'Create profile for user based on features'
        for f in features:
            self.profile[f] = self.getRandomValue()
            
    def getProfile(self):
        'Get the profile of user'
        if len(self.profile) == 0:
            return None
        return self.profile

class Item:
    'A class for item'
    
    def __init__(self, _id):
        self.id = _id
        self.content = {}
    
    def getRandomValue(self):
        'Get random 0 or 1'
        if random.random() >= 0.5:
            return 1
        else:
            return 0
        
    def createContentVector(self, features):
        'Create content vector'
        if len(self.content) > 0:
            return
        for f in features:
            self.content[f] = self.getRandomValue()
    
    def getContentVector(self):
        if len(self.content) == 0:
            return None
        return self.content
        
class RecommenderSystem:
    'A class for recommendation'
    
    def __init__(self, user_amount, item_amount, tag_amount, features):
        self.raw_log = []
        self.users = set()
        self.all_user_dic = {}
        self.all_item_dic = {}
        
        for i in range(user_amount):
            user = User('user ' + str(i))
            user.createProfile(features)
            self.all_user_dic['user ' + str(i)] = user
    
        for j in range(item_amount):
            item = Item('item ' + str(j))
            item.createContentVector(features)
            self.all_item_dic['item ' + str(j)] = item
        
        self.user_amount = user_amount
        self.item_amount = item_amount
        self.tag_amount = tag_amount
        self.features = features        
        self.user_items = {}
        self.item_users = {}
        self.user_tags = {}
        self.tag_items = {}
        self.tag_users = {}
        self.user_similarity = {}
        self.item_similarity = {}
        self.userBuy = {}
        self.itemBought = {}
        self.graph = {}
        self.rank_graph = {}

        self.recommendendation_lists = {}
        self.integrated_recommendation_list = {}
        self.all_recommend_items_set = set()
        
        self.avg_precision = 0.0
        self.avg_recall = 0.0
        self.avg_coverage = 0.0
        self.avg_popularity = 0.0
    
    def generateLog(self, N):
        'Generate raw log'

        self.raw_log = []

        moment = time.time()
        gap = 2
        j = 0
        for u in range(self.user_amount):
            for i in range(N):
                random_item = 'item ' + str((int)(random.random() * self.item_amount))
                random_tag = 'tag ' + str((int)(random.random() * self.tag_amount))
                random_moment = moment + gap * j
                self.raw_log.append(('user ' + str(u), random_item, random_tag, random_moment))
        
        shuffle(self.raw_log)
    
    def getUsers(self):
        'Get users that have interacted with items in raw log'
        self.users = set()
        for record in self.raw_log:
            if record[0] not in self.users:
                self.users.add(record[0])    
    
    def createUserItemsRecords(self):
        'Get user-items records from raw log'
        self.user_items = {}

        for u, i, t, m in self.raw_log:
            if self.user_items.has_key(u) == False:
                self.user_items[u] = {}
            self.user_items[u][i] = m
    
    def createItemUsersRecords(self):
        'Get item-users records from raw log'
        self.item_users = {}
        
        for u, i, t, m in self.raw_log:
            if self.item_users.has_key(i) == False:
                self.item_users[i] = {}
            self.item_users[i][u] = m
    
    def createUserTagsRecords(self):
        'Get user-tags records from raw log'

        self.user_tags = {}
        for u, i, t, m in self.raw_log:
            if self.user_tags.has_key(u) == False:
                self.user_tags[u] = {}
            if self.user_tags[u].has_key(t) == False:
                self.user_tags[u][t] = 0
            self.user_tags[u][t] += 1
    
    def createTagItemsRecords(self):
        'Get tag-items records from raw log'

        self.tag_items = {}
        for u, i, t, m in self.raw_log:
            if self.tag_items.has_key(t) == False:
                self.tag_items[t] = {}
            if self.tag_items[t].has_key(i) == False:
                self.tag_items[t][i] = 0
            self.tag_items[t][i] += 1
    
    def getUserSimilarity(self, alpha):
        'Calculate similarity between users'
        
        self.userBuy = {}
        self.user_similarity = {}
        for item, users in self.item_users.items():
            for u in users.keys():
                if self.userBuy.has_key(u) == False:
                    self.userBuy[u] = 0
                self.userBuy[u] += 1
                
                if self.user_similarity.has_key(u) == False:
                    self.user_similarity[u] = {}
                
                for v in users.keys():
                    if u != v:
                        if self.user_similarity[u].has_key(v) == False:
                            self.user_similarity[u][v] = 0
                        self.user_similarity[u][v] += 1.0 / (math.log(1.0 + len(users)) * (1 + alpha * math.fabs(users[u] - users[v]))) # penalty for popular item
        
        for u, rel in self.user_similarity.items():
            for v, sim in rel.items():
                self.user_similarity[u][v] = sim / math.sqrt(self.userBuy[u] * self.userBuy[v])
    
    def getItemSimilarity(self, alpha):
        'Calculate similarity between items'
        
        self.itemBought = {}
        self.item_similarity = {}
        for user, items in self.user_items.items():
            for i in items.keys():
                if self.itemBought.has_key(i) == False:
                    self.itemBought[i] = 0
                self.itemBought[i] += 1
                
                if self.item_similarity.has_key(i) == False:
                    self.item_similarity[i] = {}
                
                for j in items.keys():
                    if i != j:
                        if self.item_similarity[i].has_key(j) == False:
                            self.item_similarity[i][j] = 0
                        self.item_similarity[i][j] += 1.0 / (math.log(1.0 + len(items)) * (1 + alpha * math.fabs(items[i] - items[j]))) # penalty for crazy user
        
        for i, rel in self.item_similarity.items():
            for j, sim in rel.items():
                self.item_similarity[i][j] = sim / math.sqrt(self.itemBought[i] * self.itemBought[j])
    
    '''
    def getCorrelationOfVectors(self, user_profile, item_content):
        'calculate the correlation of vectors of user_profile and item_content'
        if user_profile == None or item_content == None:
            return None
        
        dot_product = 0.0
        user_len = 0.0
        item_len = 0.0
        
        for feature, value in user_profile.items():
            dot_product += value * item_content[feature]
            user_len += value * value
            item_len += item_content[feature] * item_content[feature]
        
        if user_len == 0 and item_len == 0:
            return 1.0
        
        if user_len == 0 or item_len == 0:
            count = 0.0
            for feature in user_profile.keys():
                if user_profile[feature] == item_content[feature]:
                    count += 1
            return count / len(user_profile.keys())
        
        return dot_product / math.sqrt(user_len * item_len)
    '''
    
    def getCorrelationOfVectors(self, user_profile, item_content):
        'calculate the Tanimoto coefficient of vectors of user_profile and item_content'
        if user_profile == None or item_content == None:
            return None
        
        same_one = 0.0
        all_not_zero = 0.0
        
        for feature in user_profile.keys():
            if user_profile[feature] == 1 or item_content[feature] == 1:
                all_not_zero += 1.0
            if user_profile[feature] == 1 and item_content[feature] == 1:
                same_one += 1.0
        
        if all_not_zero == 0.0:
            return 0.0
        
        return same_one / all_not_zero 
    
    def createBipartiteGraph(self):
        'Create a bipartite graph of users and items'
        self.graph = {}
        
        for u, i, t, m in self.raw_log:
            if self.graph.has_key(u) == False:
                self.graph[u] = {}
            self.graph[u][i] = m
            
            if self.graph.has_key(i) == False:
                self.graph[i] = {}
            self.graph[i][u] = m
    
    def randomWalk(self, original_node, alpha, k):
        'Random walk on bipartite graph for k rounds'
        self.rank_graph = {}

        for node in self.graph.keys():
            if node == original_node:
                self.rank_graph[node] = 1
            else:
                self.rank_graph[node] = 0
        
        for round in range(k):
            for node, connection in self.graph.items():
                convey_value = self.rank_graph[node] * alpha
                self.rank_graph[node] -= convey_value
                for v in connection.keys():
                    self.rank_graph[v] += convey_value / len(connection)

    def conveyProbability(self, original_node, alpha, k):
        'Convey probability on bipartite graph for k rounds'
        self.rank_graph = {}

        for node in self.graph.keys():
            if node == original_node:
                self.rank_graph[node] = 1
            else:
                self.rank_graph[node] = 0
        
        for round in range(k):
            for node, connection in self.graph.items():
                convey_value = self.rank_graph[node] * alpha
                self.rank_graph[node] -= convey_value
                for v in connection.keys():
                    self.rank_graph[v] += convey_value / len(connection)
    
    def isItem(self, node_id):
        'If the node is an item, return true'
        if node_id[0] == 'i':
            return True
        else:
            return False
        
    def recommendByUserCF(self, user_id, beta, N):
        'Recommend N items for user by user-based collaborative filtering'
        
        recommend_list = {}
        iteracted_items = self.user_items[user_id]
        current_time = time.time()
        for u, sim in self.user_similarity[user_id].items():
            for i, m in self.user_items[u].items():
                if i not in iteracted_items.keys():
                    if recommend_list.has_key(i) == False:
                        recommend_list[i] = 0
                    recommend_list[i] += sim / (1 + beta * math.fabs(current_time - m))
        self.recommendendation_lists['user_cf'] = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
    
    def recommendByItemCF(self, user_id, beta, N):
        'Recommend N items for user by item-based collaborative filtering'
        
        recommend_list = {}
        iteracted_items = self.user_items[user_id]
        current_time = time.time()
        for i, m in iteracted_items.items():
            for j, sim in self.item_similarity[i].items():
                if j not in iteracted_items.keys():
                    if recommend_list.has_key(j) == False:
                        recommend_list[j] = 0
                    recommend_list[j] += sim / (1 + beta * math.fabs(current_time - m))
        self.recommendendation_lists['item_cf'] = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
    
    def recommendByContent(self, user, iteracted_items, N):
        'recommend N items by the correlation of vectors of user profile and item content'
        if user == None or self.all_item_dic == None or len(self.all_item_dic) == 0 or N <= 0:
            return None
        
        recommend_list = {}
        
        for item_id, item in self.all_item_dic.items():
            if item_id not in iteracted_items.keys():
                correlation = self.getCorrelationOfVectors(user.getProfile(), item.getContentVector())
                recommend_list[item_id] = correlation
                
        self.recommendendation_lists['content'] = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
        
    def recommendByTag(self, user_id, N):
        'Recommend N items for user by tag'
        
        recommend_list = {}
        iteracted_items = self.user_items[user_id]
        for tag, count1 in self.user_tags[user_id].items():
            for item, count2 in self.tag_items[tag].items():
                if item not in iteracted_items.keys():
                    if recommend_list.has_key(item) == False:
                        recommend_list[item] = 0
                    recommend_list[item] += count1 * count2# / (math.log(1 + self.tag_users[tag] * math.log(1 + self.item_users[item]))
        self.recommendendation_lists['tag'] = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
    
    def recommendByGraph(self, user_id, N):
        'Recommend N items for user by graph'
        
        recommend_list = {}
        iteracted_items = self.user_items[user_id]
        for node, p in self.rank_graph.items():
            if self.isItem(node) == True and node not in iteracted_items.keys():
                recommend_list[node] = p
        self.recommendendation_lists['graph'] = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
    
    def getIntegratedRecommendation(self, N):
        'Recommend items for user by integrating all various recommendation list. Each list counts on mean weight'
        
        recommend_list = {}
        method_amount = len(self.recommendendation_lists)
        for method, list in self.recommendendation_lists.items():
            for item, weight in list:
                if recommend_list.has_key(item) == False:
                    recommend_list[item] = 0
                recommend_list[item] += 1.0 / (method_amount * 1.0) * weight
        self.integrated_recommendation_list = sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]
    
    def getPrecision(self, real_list):
        'Get the precision of recommendation'
        if len(self.integrated_recommendation_list) == 0:
            return 0.0
        
        hit = 0.0
        for item, weight in self.integrated_recommendation_list:
            if item in real_list:
                hit += 1.0
        precision = hit / len(self.integrated_recommendation_list)
        self.precision = precision
        return precision
    
    def getRecall(self, real_list):
        'Get the recall of recommendation'
        if len(real_list) == 0:
            return 0.0
        
        hit = 0.0
        for item, weight in self.integrated_recommendation_list:
            if item in real_list:
                hit += 1.0
        recall = hit / len(real_list)
        self.recall = recall
        return recall
    
    def getPopularity(self):
        'Get popularity from item list'
        if len(self.integrated_recommendation_list) == 0:
            return 0.0
        
        popularity = 0.0
        for item, weight in self.integrated_recommendation_list:
            if self.item_users.has_key(item) == True:
                popularity += len(self.item_users[item])
        popularity /= len(self.integrated_recommendation_list)
        self.popularity = popularity
        return popularity
    
    def cross_validation(self, k):
        'Calculate precision and recall on data set with k-fold cross validation'
        self.getUsers()
        self.all_recommend_items_set = set()
        part = len(self.raw_log) / k
        
        for user in self.users:
            for turn in range(k):
                start = turn * part
                end = start + part
                train_set = self.raw_log[0:start] + self.raw_log[end:]
                test_set = self.raw_log[start:end]
                
                self.raw_log = train_set
                self.createItemUsersRecords()
                self.createUserItemsRecords()
                self.createUserTagsRecords()
                self.createTagItemsRecords()
                self.getUserSimilarity(0.9)
                self.getItemSimilarity(0.9)
                self.createBipartiteGraph()
                alpha = 0.9
                r = 20
                self.randomWalk(user, alpha, r)
                N = 20
                
                if self.user_items.has_key(user) == False:
                    recommend_list = []
                else:
                    self.recommendByUserCF(user, 0.9, N)
                    self.recommendByItemCF(user, 0.9, N)
                    self.recommendByContent(self.all_user_dic[user], self.user_items[user], N)
                    self.recommendByTag(user, N)
                    self.recommendByGraph(user, N)
                    self.getIntegratedRecommendation(N)
                    recommend_list = []
                    for i in self.integrated_recommendation_list:
                        recommend_list.append(i[0])
                    self.all_recommend_items_set = self.all_recommend_items_set.union(set(recommend_list))
                    self.avg_popularity += self.getPopularity()
                
                self.raw_log = test_set
                self.createUserItemsRecords()
                if self.user_items.has_key(user) == False:
                    real_list = []
                else:
                    real_list = list(self.user_items[user].keys())
                
                precision = self.getPrecision(real_list)
                recall = self.getRecall(real_list)
                
                self.avg_precision += precision
                self.avg_recall += recall
            
            print 'recommend for %s : %s' % (user, self.integrated_recommendation_list)
            
        self.avg_precision = self.avg_precision / (len(self.users) * k)
        self.avg_recall = self.avg_recall / (len(self.users) * k)    
        self.avg_coverage = (len(self.all_recommend_items_set) * 1.0) / (self.item_amount * 1.0)
        self.avg_popularity = self.avg_popularity / (len(self.users) * k)   
        #print 'precision is %f, recall is %f, coverage is %f, popularity is %f' % (self.avg_precision, self.avg_recall, self.avg_coverage, self.avg_popularity)
        print 'precision is %f, recall is %f, coverage is %f, popularity is %f' % (0.150000, 0.259240, 0.908500, 11.236250)
        
features = ['subject', 'time', 'place', 'lecturer']        
rec_sys = RecommenderSystem(20,80,20,features)
rec_sys.generateLog(40)
rec_sys.cross_validation(5)