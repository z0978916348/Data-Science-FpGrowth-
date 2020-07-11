# Data-Science-FpGrowth-

    給定transactions和min support (頻率)，實作演算法找出frequent patterns
    每一行代表一筆transaction，一筆transaction的Item之間用”,”區隔無空格
    每筆transaction的items皆依數字大小由小到大排序，至少有一個item

### Input: 
    輸入存有transactions的txt檔
    Item以數字表示，範圍為0~999
    Transactions 最多 100000筆
    每一行代表一筆transaction，一筆transaction的Item之間用”,”區隔無空格
    每筆transaction的items皆依數字大小由小到大排序，至少有一個item

### Output:
    輸出一個txt檔
    一行為一組frequent pattern，frequent pattern後接上”:”再接上support (出現頻率)
    Frequent pattern順序從item數量少的到item數量多的，item數量相同者item編號小的排在前面
    每筆frequent pattern中的item也是由小排到大
    Support四捨五入到小數點後第4位(比較完之後才四捨五入)

# Algorithm: FpGrowth algorithm

