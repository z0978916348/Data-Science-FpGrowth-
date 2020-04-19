import sys

from collections import Counter
import math

class TreeNode():
    
    def __init__(self, item, parent=None):
        self.item = item
        self.count = 1
        self.children = list()
        self.next = None
        self.parent = parent
    
    def __str__(self):
        return str(self.item)

class FpTree():

    def __init__(self):
        self.root = TreeNode(None)
    
    def Add_Transactions_into_FpTree(self, transactions):
        for transaction in transactions:
            current = self.root
            children = current.children
            for item in transaction:
                if len(children) == 0: # no children, no necessary to check children. 
                    newTreeNode = TreeNode(item, current)
                    current = newTreeNode
                    children.append(current)
                    children = newTreeNode.children
                else:
                    found = False
                    for child in children:
                        if child.item == item: # find the child which is as same as this item
                            child.count += 1
                            current = child
                            children = current.children
                            found = True
                            break
                    if not found: # item is not found in the children
                        newTreeNode = TreeNode(item, current)
                        current = newTreeNode
                        children.append(newTreeNode)
                        children = newTreeNode.children
    
    def Construct_Base_FpTree(self, patternBase):

        for pattern in patternBase:
            current = self.root
            children = current.children
            patternList = pattern.split(',')
            # print(patternList)
            for item in patternList:
                if len(children) == 0:
                    newTreeNode = TreeNode(item, current)
                    newTreeNode.count = patternBase[pattern]  # Base FpTree's count = Base's count
                    current = newTreeNode
                    children.append(newTreeNode)
                    children = newTreeNode.children
                else:
                    found = False
                    for child in children:
                        if child.item == item:
                            child.count += patternBase[pattern] 
                            current = child
                            children = child.children
                            found = True
                            break
                    if not found:
                        newTreeNode = TreeNode(item, current)
                        current = newTreeNode
                        newTreeNode.count = patternBase[pattern]
                        children.append(newTreeNode)
                        children = newTreeNode.children
                    found = False

    def Tree_Preorder_Traverse(self, root):   
        res = list()
        for i in root.children:
            if i:
                res.append(i)
                res = res + self.Tree_Preorder_Traverse(i)
        return res
    

class FpGrowth():
    
    def __init__(self, minSupport, DB):
        self.min_support = minSupport
        self.DB = DB
        self.FrequentPattern = dict()

    def Get_DB(self):
        return self.DB

    def Count_FrequentItem(self):  
        counter = Counter()
        for i in self.DB:
            counter += Counter(i)    # calculate item frequency
        return counter.most_common() # Return a list of the n most common elements and their counts from the most common to the least

    def Find_Non_Frequent_Item(self, frequentItem):
        NonFrequent = list()
        for i in frequentItem:
            if frequentItem[i] < self.min_support:
                NonFrequent.append(i)
        return NonFrequent

    def Exclude_Non_Frequent_Item(self, frequentItem, keyList):
        for i in keyList:
            del frequentItem[i]
        
        for i in self.DB:
            for j in keyList:
                if j in i:
                    i.remove(j)
        
        return frequentItem

    def Sort_Transactions(self, frequentItem):
        for i in self.DB:
            i.sort(key= lambda x: frequentItem[x], reverse=-1)

    def Build_PatternBase(self, treenode):           # return pattern without suffix and suffix count
        patternBase = str()
        suffixCount = treenode.count
        treenode = treenode.parent
        while treenode.item:
            patternBase = str(treenode) + ',' + patternBase
            treenode = treenode.parent    
        patternBase = patternBase[:-1]
        
        return patternBase, suffixCount

    def Join_PatternBase(self, treenode, base):
        patternBase = str()
        suffixCount = treenode.count
        joinPattern = str(treenode) + ',' + base
        treenode = treenode.parent
        while treenode.item:
            patternBase = str(treenode) + ',' + patternBase
            treenode = treenode.parent
        patternBase = patternBase[:-1]
        
        return patternBase, suffixCount, joinPattern
    
    def Build_ConditionalPattern(self, headertable):  # record { ConditionalPatternBase{suffix: patternBase{ patternbase : suffixCount}}}
        ConditionalPatternBase = dict()
        
        for pattern in headertable:
            temp = headertable[pattern]['head']
            patternBaseRecord = dict()
            while temp: 
                patternBase, suffixCount = self.Build_PatternBase(temp)
                if patternBase:
                    patternBaseRecord[patternBase] = suffixCount
                temp = temp.next
            if patternBaseRecord:
                ConditionalPatternBase[pattern] = patternBaseRecord
        
        return ConditionalPatternBase
    
    def For_Recursive_Mine(self, headertable, base):
        recursivePattern = dict()

        for pattern in headertable:
            temp = headertable[pattern]['head']
            if headertable[pattern]['total'] >= self.min_support:
                joinFrequent = pattern + ',' + base
                self.FrequentPattern[joinFrequent] = headertable[pattern]['total']  # Add frequent pattern
            
            while temp != None:
                
                basePatternAfterJoin, suffixCount, joinPattern = self.Join_PatternBase(temp, base)
                if basePatternAfterJoin:
                    try:
                        recursivePattern[joinPattern][basePatternAfterJoin] = suffixCount
                    except:
                        recursivePattern[joinPattern] = dict()
                        recursivePattern[joinPattern][basePatternAfterJoin] = suffixCount
                temp = temp.next
        return recursivePattern

    def Mining_FpTree(self, conditionalPatternBase):   # Recursive find frequent pattern
        
        for suffix in conditionalPatternBase:
            baseFpTree = FpTree()
            baseFpTree.Construct_Base_FpTree(conditionalPatternBase[suffix])

            baseHeaderTable = HeaderTable()
            basePreorder = baseFpTree.Tree_Preorder_Traverse(baseFpTree.root)
            # print(*basePreorder)
            baseHeaderTable.Base_Link_Previous(basePreorder) # Link and count total
            
            baseCondition = self.For_Recursive_Mine(baseHeaderTable.headerTable, suffix) # Join and Reduce frequency
          
            if baseCondition != {}:
                yield from self.Mining_FpTree(baseCondition)
                # print(baseCondition)
    
    def Rounding(self, value):
        value = math.floor(value * 100000)
        if value % 10 > 4:
            value += 10
        value = math.floor(value/10)
        return "{:.4f}".format(value/10000)
        
        
        
class HeaderTable():
    
    def __init__(self, frequentItem=None):
        self.frequentItem = frequentItem
        self.headerTable = dict()
        if frequentItem:
            for i in frequentItem:
                self.headerTable[i] = dict()
                self.headerTable[i]['total'] = frequentItem[i]
                self.headerTable[i]['head'] = None

    def Link_Previous(self, Preorder): # Set headertable's head and link each head's next
        preorderList = Preorder
        for node in preorderList:
            if self.headerTable[node.item]['head'] == None: # not exist in headertable
                self.headerTable[node.item]['head'] = node
            else:
                temp = self.headerTable[node.item]['head']  # existed, add it next to the previous treenode
                while temp.next:
                    temp = temp.next
                temp.next = node

    def Base_Link_Previous(self, Preorder):
        basePreorderList = Preorder
        for node in basePreorderList:
            if node.item not in self.headerTable:
                self.headerTable[node.item] = dict()
                self.headerTable[node.item]['head'] = node
                self.headerTable[node.item]['total'] = node.count
            else:
                temp = self.headerTable[node.item]['head']
                while temp.next:
                    temp = temp.next
                temp.next = node
                self.headerTable[node.item]['total'] += node.count

    def print_header_table(self):
        print('Item','\t','Freq','\t'+'Parent')
        for i in self.headerTable:
            print(i,'\t',self.headerTable[i]['total'],end='\t')
            t = self.headerTable[i]['head']
            #print(t)
            while t:
                print(str(t.parent),end="->")
                t = t.next
            print('NULL')

    def Printer(self):
        for i in self.headerTable:
            print('Item = ', i, ' ', self.headerTable[i])

if __name__ == "__main__":
    
    minSupportRate = sys.argv[1]
    inputFile = sys.argv[2]
    outputFile = sys.argv[3]

    transactions = list()
    with open(inputFile, 'r') as f:
        for i in f:
            transactions.append(i[0:-1].split(','))

    minSupport = len(transactions) * float(minSupportRate)

    # Initialize
    FpGrowth = FpGrowth(minSupport, transactions)
    
    # Step1: Scan DataBase to find frequent 1_item set (support >= min_support)
    frequentItem = dict(FpGrowth.Count_FrequentItem())
   
    # Step2: Build a header table sorted by their frequency in descending order
    headerTable = HeaderTable(frequentItem)
    # headerTable.Printer()

    # Step3: Scan DB again. Exclude non-frequent items and sort them

    # find non-frequent
    nonFrequentItem = FpGrowth.Find_Non_Frequent_Item(frequentItem) 
    # exclude non_frequent 
    frequentItem = FpGrowth.Exclude_Non_Frequent_Item(frequentItem, nonFrequentItem)
    # sort transactions
    FpGrowth.Sort_Transactions(frequentItem)
    
    # Step4: Construct FpTree 

    # 1. initialize tree and create root
    MyFpTree = FpTree()

    # 2. add transactions into the FpTree
        # 2-1. if prefix exists, add 1 to the value of prefix. Otherwise, create a new node and set its value to 1
          
    transactions = FpGrowth.Get_DB()
    MyFpTree.Add_Transactions_into_FpTree(transactions)

        # 2-2. Link from the previous same frequent item node or from the header table  
    
    Preorder = MyFpTree.Tree_Preorder_Traverse(MyFpTree.root)
    headerTable.Link_Previous(Preorder)
    
    # Step5 Mining FP tree

    # 1. Select an item x in headertable (low frequency first) to ne the suffix. Obtain the subtree with all leaves as x 
    
    conditionalPatternBase = FpGrowth.Build_ConditionalPattern(headerTable.headerTable) # record a dict 
                                                                                        # { ConditionalPatternBase{suffix: patternBase{ patternbase : suffixCount}}}
    # print(conditionalPatternBase)
    # 2. Except x, set each node's value as sum of its child's value
    # 3. Delete which have sum of values < min_support. 
    #    Use the remaining item to construct a conditional FpTree and mine frequent patterns on it to obtain Fp with item x
    # 4. Repeat 1, 2, 3

    it = iter(FpGrowth.Mining_FpTree(conditionalPatternBase))
    while True:
        try:
            Next = next(it)
        except StopIteration:
            break

    FpGrowth.FrequentPattern.update(frequentItem)
    
    patternAndSupport = dict()

    for i in FpGrowth.FrequentPattern:
        sortTemp = list(map(str, sorted(list(map(int,i.split(','))))))
        strKey = ','.join(sortTemp)
        patternAndSupport[strKey] = FpGrowth.Rounding(FpGrowth.FrequentPattern[i]/len(transactions))
    
    patternAndSupport = sorted(patternAndSupport.items(), key= lambda x: (len(x[0].split(',')), list(map(int, x[0].split(',')))))
    
    with open(outputFile,'w') as f:
        for i in patternAndSupport:
            f.write(str(i[0])+":"+str(i[1])+'\n')
    


    

    
    