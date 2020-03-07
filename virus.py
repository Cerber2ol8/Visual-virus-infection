import numpy as np
import types

class crowds(object):
    def __init__(self, count=1000):
        self.count = count
        #人群获得性免疫开关
        self.acquired_immunity = True
        self.acquired_immunity_poss = 0.8
        #随机移动步长
        self.move_width = 10

        self._location = np.random.normal(0,100,(self.count, 2))
        self._status = np.zeros(self.count,dtype=np.int)
        self._timer = np.zeros(self.count,dtype=np.int)

        #TODO 人口种类[区分是否为医护人员]
        #self._kind = np.zeros(self.count, dtype=np.int)

    
    """
        状态：    0:正常   1：感染潜伏期  2：发病确诊 3：治愈 -1:死亡       
    """
    @property
    def status(self):
        return self._status

    @property
    def timer(self):
        return self._timer

    @property
    def healthy(self):
        return self._location[self._status == 0]

    @property
    def infected(self):
        return self._location[self._status == 1]

    @property
    def confirmed(self):
        return self._location[self._status == 2]

    @property
    def cured(self):
        return self._location[self._status == 3]

    @property
    def dead(self):
        return self._location[self._status == -1]

    @property
    def alive(self):
        return self._location[self._status != -1]

    def reset(self):
        self._location = np.random.normal(0,100,(self.count, 2))
        self._status = np.zeros(self.count,dtype=np.int)
        self._timer = np.zeros(self.count,dtype=np.int)

    def move(self):
        width = self.move_width
        self._location[self._status != -1] = self._location[self._status != -1] + np.random.normal(0, width, (len(self.alive), 2))

        if len(self.dead) > 0:
            self._location[self._status == -1] = np.array([[-999,-999]]* len( self.dead)) 


class virus(object):
    def __init__(self):
        #p1  p2
        self.p1 = [5,10]
        self.p2 = [7,28]
        self._period1 = np.array([i+self.p1[0] for i in range(self.p1[1])])
        self._period2 = np.array([i+self.p2[0] for i in range(self.p2[0])])
        #致死率  >=0
        self.lethality = 0.03
        #治愈率    >=0
        self.cure_rate = 0.8
        #传染性
        self.transmissibility = -0.8  #易感程度，正态分布概率  0 为 50%  1为100%
        self.safe_distance = 6.0    #距离内会被传染

        return super().__init__()

    def affect(self, crowds, round):
        self.infect_possible(x=self.transmissibility,safe_distance=self.safe_distance,crowds=crowds, round=round)
        self.causing_death(crowds)
        self.cure(crowds,round)


    def cure(self, crowds, round):
        dt = round - crowds._timer
        #假定 当前治愈率随时间线性增加到总体治愈率  （统计学上有不合理之处）
        current_cure_rate = self.cure_rate * (dt / (self._period2.max() ))
        #模拟抖动
        current_cure_rate = current_cure_rate * (1 + (np.random.randint(-5,5) * 0.1))

        #确诊转为治愈    2-->3
        if self.cure_rate > 0:
            crowds._status[(crowds._status == 2) & (dt > self._period2.min()) &  (dt < self._period2.max())
                          & ((np.random.uniform(0,1,crowds.count) <= current_cure_rate))] += 1
        #print(crowds._timer[crowds._status == 2])
        #超时患者死亡 
        crowds._status[(crowds._status == 2) & 
                       (dt > self._period2.max())] = -1
        #if round %10 == 0:

        #    if round == 100:
        #        list = []
        #        for i in range(crowds.count):
        #            list.append([crowds._status[i], dt[i], crowds._timer[i]])
                #for l in list:
                #        if l[0] == 2:
                #            print(l)
                #print(len(crowds.dead))
                #exit()

    def infect_possible(self, x=0., safe_distance=4.0, crowds=None, round=None):
        """按概率感染接近的健康人
        x 的取值参考正态分布概率表，x=0 时感染概率是 50%
        """
        def get_distence(infected):
            dm = (crowds._location - inf) ** 2
            d = dm.sum(axis=1) ** 0.5
            return d

        for inf in crowds.infected:
            d = get_distence(inf)
            sorted_index = d.argsort()
            for i in sorted_index:
                if d[i] >= safe_distance:
                    break  
                if crowds.status[i] > 0 and crowds.status[i] < 3 or crowds.status[i] == -1:
                        continue
                if crowds.status[i] == 3 and crowds.acquired_immunity:
                    if crowds.acquired_immunity_poss - np.random.uniform(0,1) > 0:
                        continue
                if np.random.normal() > x:
                    continue
                crowds.status[i] = 1
                # 记录状态改变的时间
                crowds.timer[i] = round

        for inf in crowds.confirmed:
            d = get_distence(inf)
            sorted_index = d.argsort()
            for i in sorted_index:
                if d[i] >= safe_distance:
                    break  
                if crowds.status[i] > 0 and crowds.status[i] < 3 or crowds.status[i] == -1:
                    continue
                if crowds.status[i] == 3 and crowds.acquired_immunity:
                    if crowds.acquired_immunity_poss - np.random.uniform(0,1) > 0:
                        continue
                if np.random.normal() > x:
                    continue

                crowds.status[i] = 1
                # 记录状态改变的时间
                crowds.timer[i] = round

    def causing_death(self,crowds):
        num = int((int((len(crowds.confirmed) + 
                        len(crowds.cured)) * self.lethality) - 
                   len(crowds.dead)) * (1 + (np.random.randint(-5,5) * 0.1)))

        if len(crowds.confirmed) > 0:
            n = 0
            while n < num:
                i = np.random.randint(0, crowds.count)
                if crowds.status[i] != 2:
                    continue
                else:
                    crowds.status[i] = -1
                    n += 1

class model(object):
    def __init__(self, people_count=1000, initial_infected_count=10):
        self.count = people_count
        self.initial_infected_count = initial_infected_count
        self.people = crowds(self.count)
        self.virus = virus()
        self.round = 0
        self.visualization = True
        self.plt = None
        #TODO:模型引入r0值
        #self.r0 = None

        #记录数据
        self.y_h = []
        self.y_i = []
        self.y_d = []
        self.y_c = []
        self.y_con = []
        self.r = []



        #输出数据
        self.out_swith = False


        self.reset()
        return super().__init__()


    def reset(self):
        self.people.reset()

        self.people_get_initial_infected(num=self.initial_infected_count, status=1)


    def people_get_initial_infected(self, num, status=1):
        """随机挑选人设置状态
        """
        assert self.count > num

        n = 0
        while n < num:
            i = np.random.randint(0, self.count)
            if self.people.status[i] >= status:
                continue
            else:
                self.people.status[i] = status
                n += 1


    def change_status(self):
        p1 = self.virus._period1
        p2 = self.virus._period2
        t = (self.round, self.round - self.people.timer, p1[np.random.randint(p1.min(),p1.max()) - p1.min()],p2[np.random.randint(p2.min(),p2.max()) - p2.min()])
        self.set_timer(t)
        self.set_status(t)
        

    def set_status(self,t):
        if isinstance(t,int):
            self.people._timer = t
        else:
            dt = t[1]
            d1 = t[2]
            d2 = t[3]
            #潜伏病例转为确诊 1-->2
            self.people._status[(self.people._status == 1) & 
                                ((dt == d1) | (dt > self.virus._period1.max()))] += 1


    def set_timer(self,t):
        if isinstance(t,int):
            self._timer = t
        else:
            dt = t[1]
            d1 = t[2]
            d2 = t[3]
            round = t[0]
            self.people._timer[(self.people._status == 1) &
                              ((dt == d1) | (dt > self.virus._period1.max()))] = self.round
            #print(len(self.people._timer[(self.people._status == 1) &
            #                  ((dt == d1) | (dt > self.virus._period1.max()))]) != 0)
            #self.people._timer[(self.people._status == 2) & 
             #                  (dt == d2) | (dt > self.virus._period2.max())] = self.round



    def virus_affect(self, crowds):
        self.virus.affect(crowds, self.round)

    def visualize(self):
        if self.plt != None:
            self.plt.cla()
            s1 = self.plt.scatter(self.people.healthy[:, 0], self.people.healthy[:, 1], s=10)
            s2 = self.plt.scatter(self.people.infected[:, 0], self.people.infected[:, 1], s=10, c='pink')
            s3 = self.plt.scatter(self.people.confirmed[:, 0], self.people.confirmed[:, 1], s=10, c='red')
            s4 = self.plt.scatter(self.people.cured[:, 0], self.people.cured[:, 1], s=10, c='green')
            self.plt.legend([s1, s2, s3, s4], ['healthy', 'infected', 'confirmed', 'cured'], loc='upper right', scatterpoints=1)
            t = "Round: %s, Healthy: %s, Infected: %s, Confirmed: %s, Cured: %s,Dead: %s" % \
                (self.round, len(self.people.healthy), len(self.people.infected), len(self.people.confirmed),len(self.people.cured),len(self.people.dead))
            self.plt.text(-200, -400, t, ha='left', wrap=True)
            self.plt.pause(.02)
            pass

    def update(self):
        
        self.change_status()
        self.virus_affect(self.people)
        self.people.move()
        self.round += 1
        self.read_data()
        #print(self.round)
        if self.out_swith:
            print(len(self.people.healthy),
                  len(self.people.infected),
                  len(self.people.confirmed),
                  len(self.people.cured),
                  len(self.people.dead))
        if self.visualization:
            self.visualize()

    def read_data(self):
        
        self.y_h.append(len(self.people.healthy) + len(self.people.cured))
        self.y_i.append(len(self.people.infected) + len(self.people.confirmed))
        self.y_c.append(len(self.people.cured))
        self.y_d.append(len(self.people.dead))
        self.y_con.append(len(self.people.confirmed))
        self.r.append(self.round)
    def plot(self):
        def lg(*args):
            r = []
            for arg in args:
                r.append(np.log10(arg))
            return r
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 8))
        #取对数
        #self.y_h,self.y_i,self.y_c,self.y_d = lg(self.y_h,self.y_i,self.y_c,self.y_d)

        l_h = plt.plot(self.r,self.y_h,label='Total Healthy')
        l_i = plt.plot(self.r,self.y_i,label='Total infected',color='pink')
        l_c = plt.plot(self.r,self.y_c,label='Cured',color='g')
        l_d = plt.plot(self.r,self.y_d,label='Dead',color='black')
        l_con = plt.plot(self.r,self.y_con,label='confirmed',color='r')
        plt.legend() 
        plt.title('Trend chart') 
        plt.show()


if __name__ == '__main__':
    """
        模型建立在以下假设成立的条件下：    （没有进行严谨的统计学处理）
        确诊病人都能及时就诊
        当前治愈率会随时间线性增加到总体治愈率  
        人群分布是正态分布
        人群会随机移动
        感染概率为正态分布
        病毒致死率与致死系数正相关，治愈率与治愈系数正相关
    """
    np.random.seed(0)

    m = model(people_count=500,initial_infected_count=1)

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

    m.reset()
    #交互式散点图，开启会影响效率
    m.visualization = False
    if m.visualization:
        import matplotlib.pyplot as plt
        m.plt = plt
        m.plt.figure(figsize=(10, 10), dpi=85)
        m.plt.ion()
        

    round = 500
    for i in range(round):
        m.update()
        print('computing {} %...'.format('%.1f' %(i/round * 100)))
    m.plot()
    if m.visualization:
        plt.pause(0)
     