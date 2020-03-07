# Visual-virus-infection
可视化病毒传播过程模型
并非统计学模型，只是简单的过程模拟。 基于 [virusdemo](https://github.com/davycloud/virusdemo) 的可视化病毒传播过程
![image](https://github.com/Cerber2ol8/Visual-virus-infection/edit/master/17T5HQRXO{1](G]]%[`W)MC.png)
(https://raw.githubusercontent.com/Cerber2ol8/Visual-virus-infection/master/99Z%FWX]4(YM8VLOZ3BNIET.png
)
(https://raw.githubusercontent.com/Cerber2ol8/Visual-virus-infection/master/AX140TF6VF3JLN_B0USV5O9.png
)
(https://raw.githubusercontent.com/Cerber2ol8/Visual-virus-infection/master/W@FXJ(1PM`93L[E[ZI}1{[M.png
)
(https://raw.githubusercontent.com/Cerber2ol8/Visual-virus-infection/master/YXKB8ZZV(T[@JV3(G]82SP6.png
)
(https://raw.githubusercontent.com/Cerber2ol8/Visual-virus-infection/master/}IXT77A8@I[TX9O6)~EPI7G.png
)

    """
        模型建立在以下假设成立的条件下：    （没有进行严谨的统计学处理）
        确诊病人都能及时就诊
        当前治愈率会随时间线性增加到总体治愈率  
        人群分布是正态分布
        人群会随机移动
        感染概率为正态分布
        病毒致死率与致死系数正相关，治愈率与治愈系数正相关
    """
    
    
    #人群特性参数
    #人群获得性免疫 True治愈之后,有概率不会再感染
    m.people.acquired_immunity = True
    m.people.acquired_immunity_poss = 0.8 #免疫概率
    #随机移动步长 越大每次移动范围越大
    m.people.move_width = 10
    #TODO区分人群限制移动

    #病毒特性参数
    """
        病毒相关数据（并不准确）
        病毒种类      致死率      潜伏期p1       确诊治疗期p2     
        埃博拉        50%-90%    5-10           14-28
        2019-nCorV   2%-4%      1-14           7-48
        SARS         9.6%
        甲型h1n1      1-4%
        美国流感      0.05%
    """
    n = 3  #时间尺度系数
    #p1  p2
    m.virus.p1 = [int(5*n),int(10*n)]
    m.virus.p2 = [int(7*n),int(28*n)]
    m.virus._period1 = np.array([i+m.virus.p1[0] for i in range(m.virus.p1[1])])
    m.virus._period2 = np.array([i+m.virus.p2[0] for i in range(m.virus.p2[0])])
    #致死系数 越大致死能力越强   >=0
    m.virus.lethality = 0.04
    #治愈系数 越大越容易被治愈   >=0
    m.virus.cure_rate = 1
    #传染性
    m.virus.transmissibility = -0.6  #反映病毒易感程度，正态分布概率  0 为 50%  1为100%
    m.virus.safe_distance = 10.0     #有概率被传染的范围
    #人群特性参数
    #人群获得性免疫 True治愈之后,有概率不会再感染
    m.people.acquired_immunity = True
    m.people.acquired_immunity_poss = 0.8 #免疫概率
    #随机移动步长 越大每次移动范围越大
    m.people.move_width = 10
    #TODO区分人群限制移动

    #病毒特性参数
    """
        病毒相关数据（并不准确）
        病毒种类      致死率      潜伏期p1       确诊治疗期p2     
        埃博拉        50%-90%    5-10           14-28
        2019-nCorV   2%-4%      1-14           7-48
        SARS         9.6%
        甲型h1n1      1-4%
        美国流感      0.05%
    """
    n = 3  #时间尺度系数
    #p1  p2
    m.virus.p1 = [int(5*n),int(10*n)]
    m.virus.p2 = [int(7*n),int(28*n)]
    m.virus._period1 = np.array([i+m.virus.p1[0] for i in range(m.virus.p1[1])])
    m.virus._period2 = np.array([i+m.virus.p2[0] for i in range(m.virus.p2[0])])
    #致死系数 越大致死能力越强   >=0
    m.virus.lethality = 0.04
    #治愈系数 越大越容易被治愈   >=0
    m.virus.cure_rate = 1
    #传染性
    m.virus.transmissibility = -0.6  #反映病毒易感程度，正态分布概率  0 为 50%  1为100%
    m.virus.safe_distance = 10.0     #有概率被传染的范围
