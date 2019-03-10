import ahocorasick
import os
from chardet.universaldetector import UniversalDetector
import time
import re
import sys

def 获取文件大小(文件地址, 规范单位=0):
    '''
    :param 文件地址:  文件字节数 或者 文件路径
    :param 规范单位:  0=自动,1=B,2=KB,3=MB,4=GB,5=TB
    :return:
    '''
    if isinstance(文件地址,int):
        文件大小=文件地址
    else:
        try:
            if not os.path.isdir(文件地址):
                文件大小 = os.path.getsize(文件地址)
            else:
                raise 1
        except:
            return None, None, None, None
    文件大小_B=文件大小
    if 规范单位 <= 0:  # 自动规范
        if 文件大小 < 1024:
            后缀='B'
            名称='%d%s'%(文件大小,后缀)
        else:
            文件大小 /= 1024
            if 文件大小 < 1024:
                后缀 = 'KB'
            else:
                文件大小 /= 1024
                if 文件大小 < 1024:
                    后缀 = 'MB'
                else:
                    文件大小 /= 1024
                    if 文件大小 < 1024:
                        后缀 = 'GB'
                    else:
                        文件大小 /= 1024
                        后缀 = 'TB'
            名称='%.2f%s'%(文件大小,后缀)
    elif 规范单位 == 1:  # B
        后缀 = 'B'
        名称='%d%s'%(文件大小,后缀)
    elif 规范单位 == 2:  # KB
        文件大小=文件大小 / 1024
        后缀 = 'KB'
        名称='%.2f%s'%(文件大小,后缀)
    elif 规范单位 == 3:  # MB
        文件大小=文件大小 / 1024 / 1024
        后缀 = 'MB'
        名称='%.2f%s'%(文件大小,后缀)
    elif 规范单位 == 4:  # GB
        文件大小=文件大小 / 1024 / 1024 / 1024
        后缀 = 'GB'
        名称='%.2f%s'%(文件大小,后缀)
    else: # TB
        文件大小=文件大小 / 1024 / 1024 / 1024 / 1024
        后缀 = 'TB'
        名称='%.2f%s'%(文件大小,后缀)
    return 文件大小, 后缀, 文件大小_B, 名称

class 搜索字符串:
    def __init__(self,字符串列表=[]):
        self.A=ahocorasick.Automaton()
        self.匹配串数量=0
        增加个数=self.增加匹配串(字符串列表)
        if 增加个数>0:
            self.制作树()

    def 增加匹配串(self,字符串):
        增加个数=0
        if isinstance(字符串,list):
            for i in 字符串:
                self.A.add_word(i,(self.匹配串数量,i))
                self.匹配串数量+=1
                增加个数+=1
        else:
            self.A.add_word(字符串, (self.匹配串数量, 字符串))
            self.匹配串数量 += 1
            增加个数+=1
        return 增加个数

    def 制作树(self):
        self.A.make_automaton()
        return True

    def 匹配(self,字符串,匹配程度=1):
        匹配位置_编号_词表l=[] # [(匹配位置,(词编号,词)),..]
        匹配编号种类s={}
        for item in self.A.iter(字符串):
            if 匹配程度==0: # 匹配到第一个字符串跳出
                匹配位置_编号_词表l.append(item)
                匹配编号种类s[item[1][0]]=True
                break
            elif 匹配程度==1: # 匹配到所有字符串跳出
                if len(匹配编号种类s)==self.匹配串数量:
                    break
                if item[1][0] not in 匹配编号种类s:
                    匹配位置_编号_词表l.append(item)
                    匹配编号种类s[item[1][0]]=True
            else:
                匹配位置_编号_词表l.append(item)
                匹配编号种类s[item[1][0]]=True
        没有匹配到的字符串种数=self.匹配串数量-len(匹配编号种类s)
        return 匹配位置_编号_词表l,没有匹配到的字符串种数

class 待匹配字符串:
    def __init__(self,待匹配字符串列表l,每个关键词最多几个匹配结果=2):
        self.搜索字符串_obj=搜索字符串(待匹配字符串列表l)
        self.匹配结果_全 =None
        self.匹配结果 =None
        self.每个关键词最多几个匹配结果=每个关键词最多几个匹配结果
        self.关键词_出现次数表d={}

    def 匹配(self,文本):
        self.匹配结果_全=self.搜索字符串_obj.匹配(文本,匹配程度=2)
        if self.匹配结果_全[1]>0:
            return False
        self._削减匹配结果()
        self.文本=文本
        return True

    def _削减匹配结果(self):
        if self.匹配结果_全==None:
            return False
        关键词_出现次数表d={} # {关键词:出现次数,..}
        self.匹配结果=[[],self.匹配结果_全[1]]
        for 匹配位置,词编号_词 in self.匹配结果_全[0]:
            if 词编号_词[1] not in 关键词_出现次数表d:
                关键词_出现次数表d[词编号_词[1]]=0
            关键词_出现次数表d[词编号_词[1]]+=1
            if 关键词_出现次数表d[词编号_词[1]]>self.每个关键词最多几个匹配结果:
                continue
            else:
                self.匹配结果[0].append([匹配位置,词编号_词])
        self.关键词_出现次数表d = 关键词_出现次数表d
        return True

    def 返回关键词出现次数(self):
        return self.关键词_出现次数表d

    def 返回匹配结果_含周围字符串(self,包含周围几个字符=10,加入颜色=True):
        含周围字符串_位置l=[] # [[字符串,其中第一个字符在文本中位置的百分比],..]
        if self.匹配结果 ==None:
            return None
        串头_串尾位置表=[] # [[串头位置,串尾位置],..]

        上一个串尾位置=-1
        for 匹配位置,编号_词表 in self.匹配结果[0]:
            词长度=len(编号_词表[1])
            匹配位置=匹配位置-词长度+1
            # 判断字符串是否整合
            if 上一个串尾位置>-1 and 上一个串尾位置>=匹配位置:
                串头_串尾位置表[-1][1]=匹配位置+词长度-1
                上一个串尾位置+=词长度
            else:
                串头_串尾位置表.append([匹配位置,匹配位置+词长度-1])
                上一个串尾位置=匹配位置+词长度

        上一个串尾位置=-1
        for 串头位置,串尾位置 in 串头_串尾位置表:
            if 加入颜色:
                标记字符串=待匹配字符串.颜色(self.文本[串头位置:串尾位置+1])
            else:
                标记字符串 =self.文本[串头位置:串尾位置+1]
            if 上一个串尾位置 > -1 and 串头位置-上一个串尾位置<=包含周围几个字符:
                置文本=self._前置或后置文本处理(self.文本,上一个串尾位置+1,串头位置)
                含周围字符串_位置l[-1][0].append(置文本)
                含周围字符串_位置l[-1][0].append(标记字符串)
            else:
                if len(含周围字符串_位置l)>0: # 上一个串尾补充
                    置文本=self._前置或后置文本处理(self.文本, 上一个串尾位置 + 1, 上一个串尾位置 + 1 + 包含周围几个字符)
                    含周围字符串_位置l[-1][0].append(置文本)
                含周围字符串_位置l.append([[], 串头位置 / len(self.文本)])
                # 开头补充
                上一个串尾位置=串头位置-包含周围几个字符
                if 上一个串尾位置<0:
                    上一个串尾位置=0
                置文本 = self._前置或后置文本处理(self.文本, 上一个串尾位置, 串头位置)
                含周围字符串_位置l[-1][0].append(置文本)
                含周围字符串_位置l[-1][0].append(标记字符串)
            上一个串尾位置=串尾位置
        置文本 = self._前置或后置文本处理(self.文本, 上一个串尾位置 + 1, 上一个串尾位置 + 1 + 包含周围几个字符)
        含周围字符串_位置l[-1][0].append(置文本)

        for i in range(len(含周围字符串_位置l)):
            含周围字符串_位置l[i][0]=''.join(含周围字符串_位置l[i][0])
        return 含周围字符串_位置l

    def _前置或后置文本处理(self,文本,首位置,尾位置):
        提取文本=文本[首位置:尾位置]
        提取文本=提取文本.replace('\n',r'\n')
        提取文本=提取文本.replace('\r',r'\r')
        return 提取文本

    @staticmethod
    def 颜色(字符串,红绿黄蓝紫青白=1):
        return '\033[0;3%s;0m%s\033[0m'%(str(红绿黄蓝紫青白),字符串)

    @staticmethod
    def 反颜色(字符串):
        return re.subn(r'\033\[0;3[0-9];0m|\033\[0m','',字符串)[0]

class 待匹配文本:
    def __init__(self,文本地址):
        with open(文本地址,'rb') as r:
            文本二进制=r.read()
            self.文本=self._尝试解析文件(文本二进制)
            if self.文本==None:
                r.seek(0)
                编码=self._解析文件编码(r)
                try:
                    self.文件编码=编码
                    self.文本=str(文本二进制,encoding=编码,errors='ignore')
                except:
                    self.文本=None

    def _尝试解析文件(self,文本二进制,尝试编码=('utf-8','utf-32el','utf-32le','utf-16el','utf-16le',
                                 'gb2312','gb18030','gbk')):
        文本=None
        for 编码 in 尝试编码:
            try:
                文本=str(文本二进制,encoding=编码)
                self.文件编码=编码
                return 文本
            except:
                continue
        return 文本

    def _解析文件编码(self, 文本指针, 超过一定行数跳出=200):
        detector = UniversalDetector()
        读取行数=0
        for line in 文本指针:
            if 超过一定行数跳出<读取行数:
                break
            读取行数+=1
            detector.feed(line)  # 逐行载入UniversalDetector对象中进行识别
            if detector.done:  # done为一个布尔值，默认为False，达到阈值时变为True
                break
        detector.close()
        文件编码 = detector.result['encoding']
        detector.reset()
        return 文件编码

    def 返回文本(self):
        return self.文本

    def 返回文件编码(self):
        return self.文件编码

class 命令参数:
    def __init__(self,后缀名名单=('.txt','.md','.json','.tex'),命令正则式=None):
        self.后缀名名单=后缀名名单
        self.命令正则式=命令正则式 # {编号:[提取正则式,删除替换正则式],..}

    def 获得命令参数(self,提示语='输入文件夹路径和关键词:'):
        路径和关键词=''
        while 路径和关键词.strip()=='':
            路径和关键词=input(提示语)
        路径和关键词, 命令编号_内容=self._提取命令(路径和关键词)
        路径和关键词=self._解析路径和关键词(路径和关键词)
        if 路径和关键词==None:
            return None,None,None,None
        #
        路径=路径和关键词[0]
        关键词列表=路径和关键词[1]
        输出路径=路径和关键词[2]
        if 路径==None or len(关键词列表)==0:
            return None,None,None,None
        print('匹配路径: "%s", 匹配关键词(%d): %s, 输出结果文件: "%s"'%(路径,len(关键词列表),str(关键词列表),输出路径))
        return 关键词列表,路径,输出路径,命令编号_内容

    def 遍历文件地址(self,路径,文件大小限制):
        if 路径==None:
            return None
        待遍历文件地址=self._返回符合要求的文件地址(路径,self.后缀名名单,文件大小限制)
        if len(待遍历文件地址)==0:
            return None
        return 待遍历文件地址

    def _提取命令(self,路径和关键词):
        命令编号_内容={}
        路径和关键词=' '+路径和关键词+' '
        if self.命令正则式!=None:
            for 编号,正则式l in self.命令正则式.items():
                提取正则式=正则式l[0]
                删除替换正则式=正则式l[1]
                匹配=re.search(提取正则式,路径和关键词)
                if 匹配==None:
                    continue
                命令编号_内容[编号]=匹配[0]
                路径和关键词=re.subn(删除替换正则式,' ',路径和关键词)[0]
        return 路径和关键词,命令编号_内容

    @staticmethod
    def _返回符合要求的文件地址(目录,后缀名名单,文件大小限制):
        '''

        :param 目录:
        :param 后缀名名单:
        :param 文件大小限制:  单位:MB
        :return:
        '''
        sys.stdout.write('\r')
        print('获得扫描文件地址中...',end='')
        开始时间=time.time()
        sys.stdout.flush()
        后缀名名单=frozenset([i.lower() for i in 后缀名名单])
        符合要求的文件地址=[]

        文件大小=获取文件大小(目录,3)[0]
        if 文件大小!=None and 文件大小<=文件大小限制: # 如果不是文件夹
            if os.path.splitext(目录)[1].lower() in 后缀名名单:
                符合要求的文件地址.append(目录)
            return 符合要求的文件地址

        for 路径,子目录,包含文件名 in os.walk(目录):
            for 一个文件名 in 包含文件名:
                文件路径=路径+'/'+一个文件名
                后缀名=os.path.splitext(一个文件名)[1].lower()
                if 后缀名 in 后缀名名单:
                    文件大小 = 获取文件大小(文件路径,3)[0]
                    if 文件大小!=None and 文件大小<=文件大小限制:
                        符合要求的文件地址.append(文件路径)
        sys.stdout.write('\r')
        print('扫描文件地址耗时: %.2f秒' % ((time.time() - 开始时间)))
        return 符合要求的文件地址

    @staticmethod
    def _解析路径和关键词(路径和关键词):
        分割结果 = []
        路径和关键词 = re.split('["\']', 路径和关键词)
        if len(路径和关键词) % 2 == 0:
            return None
        for i in range(len(路径和关键词)):
            一个片段 = 路径和关键词[i]
            if i % 2 == 0:
                if (i == 0 or i == len(路径和关键词) - 1) and len(一个片段) == 0:
                    continue
                if len(一个片段) == 0 or i != 0 and 一个片段[0] != ' ' or i != len(路径和关键词) - 1 and 一个片段[-1] != ' ':
                    return None
                一个片段 = 一个片段.strip()
                if len(一个片段) == 0:
                    continue
                else:
                    for 一个小片段 in re.split('[\t ]+', 一个片段):
                        分割结果.append(一个小片段)
                    continue
            分割结果.append(一个片段)
        # 整理分割结果
        路径 = None
        关键词列表 = []
        输出路径=None
        for 一个分割结果 in 分割结果:
            if len(一个分割结果) == 0:
                continue
            if 路径 == None and os.path.exists(一个分割结果):
                路径 = 一个分割结果
            elif 输出路径 == None and os.path.exists(一个分割结果):
                输出路径=一个分割结果
            else:
                关键词列表.append(一个分割结果)
        return 路径, 关键词列表,输出路径

class 执行者:
    def __init__(self,包含周围几个字符,文件大小限制,后缀名名单,每个关键词最多几个匹配结果,只显示前几条,命令正则式,取交集):
        self.包含周围几个字符=包含周围几个字符
        self.文件大小限制=文件大小限制
        self.每个关键词最多几个匹配结果=每个关键词最多几个匹配结果
        self.只显示前几条=只显示前几条
        self.取交集=取交集

        self.命令参数_obj = 命令参数(后缀名名单,命令正则式)

    def _解析命令(self,命令编号_内容):
        if 命令编号_内容==None:
            return
        for 命令编号,内容 in 命令编号_内容.items():
            if 命令编号=='i':
                self.包含周围几个字符=int(内容)
            elif 命令编号=='s':
                self.文件大小限制=int(内容)
            elif 命令编号=='m':
                self.每个关键词最多几个匹配结果=int(内容)
            elif 命令编号=='r':
                self.只显示前几条=int(内容)
            elif 命令编号=='u':
                self.取交集=int(内容)
                if self.取交集!=0:
                    self.取交集=1

    def _获得一次查询结果(self,每隔多久报一次结果,提示语): # 单位 毫秒
        关键词列表, 路径, 输出路径, 命令编号_内容=self.命令参数_obj.获得命令参数(提示语)
        self._解析命令(命令编号_内容)
        待遍历文件地址=self.命令参数_obj.遍历文件地址(路径,self.文件大小限制)
        if 待遍历文件地址==None or len(待遍历文件地址)==0 or 关键词列表==None or len(关键词列表)==0:
            print('(输入格式: 文件路径 关键词 ... 关键词 [结果输出地址])')
            return None,None

        开始时间=int(time.time()*1000) # 单位 毫秒
        报时时间=开始时间
        总文件大小=0
        最大文件大小=(0,'B',0,'0B')
        最小文件大小=(float("inf"),'B',float("inf"),'infB')

        待匹配字符串_obj=待匹配字符串(关键词列表,self.每个关键词最多几个匹配结果)
        文件地址_匹配结果l=[] # [[文件地址,含周围字符串_位置l,关键词_出现次数表d,重要度],..]
        for i in range(len(待遍历文件地址)):
            文件地址=待遍历文件地址[i]
            当前时间=int(time.time()*1000)
            if 报时时间==开始时间 or 当前时间-报时时间>=每隔多久报一次结果:
                报时时间=当前时间
                sys.stdout.write('\r')
                if len(文件地址_匹配结果l)>0:
                    最后找到的文件=文件地址_匹配结果l[-1][0]
                else:
                    最后找到的文件=''
                print('匹配进度: %d/%d, 已耗时: %.2f秒, 已找到: %d→"%s", 进行到文件: "%s"'%
                      (i+1,len(待遍历文件地址),(当前时间-开始时间)/1000,len(文件地址_匹配结果l),最后找到的文件,文件地址),
                      end='')
                sys.stdout.flush()

            文件大小=获取文件大小(文件地址,规范单位=0)
            总文件大小+=文件大小[2]
            if 文件大小[2]>最大文件大小[2]:
                最大文件大小=文件大小
            if 文件大小[2]<最小文件大小[2]:
                最小文件大小=文件大小

            待匹配文本_obj=待匹配文本(文件地址)
            文本=待匹配文本_obj.返回文本()
            if 文本==None or not 待匹配字符串_obj.匹配(文本):
                continue
            含周围字符串_位置l=待匹配字符串_obj.返回匹配结果_含周围字符串(self.包含周围几个字符)
            关键词_出现次数表d=待匹配字符串_obj.返回关键词出现次数()
            重要程度=self._重要程度计算(关键词_出现次数表d) # 用于排序显示
            文件地址_匹配结果l.append([文件地址,含周围字符串_位置l,关键词_出现次数表d,重要程度])
        总文件大小=获取文件大小(总文件大小, 规范单位=0)

        sys.stdout.write('\r')
        print('总匹配对象数: %d, 匹配成功数: %d, 共耗时: %.2f秒, 总文件数据: %s, 单个最大文件: %s'%
              (len(待遍历文件地址),len(文件地址_匹配结果l),(int(time.time()*1000)-开始时间)/1000,总文件大小[3],最大文件大小[3]))
        return 文件地址_匹配结果l,输出路径

    def _重要程度计算(self,关键词_出现次数表d):
        总次数=0
        for 关键词,出现次数 in 关键词_出现次数表d.items():
            总次数+=出现次数
        return 总次数

    def _输出匹配结果(self,文件地址_匹配结果l,只显示前几条,输出到文件='',排序=True):
        个数=0
        结果l=[]
        if 排序:
            文件地址_匹配结果l_排序=sorted(文件地址_匹配结果l,key=lambda t:t[3],reverse=True)
        else:
            文件地址_匹配结果l_排序=文件地址_匹配结果l
        for 文件地址,含周围字符串_位置l,关键词_出现次数表d,重要程度 in 文件地址_匹配结果l_排序:
            if 个数>=只显示前几条:
                break
            个数+=1

            输出='\n%d: "%s"'%(个数,文件地址)
            print(输出)
            结果l.append(输出)

            输出='关键词出现次数: %s'%(str(sorted(关键词_出现次数表d.items(),key=lambda t:t[1],reverse=True)))
            print(输出)
            结果l.append(输出)

            for 字符串, 位置 in 含周围字符串_位置l:
                位置字符串=待匹配字符串.颜色('%.2f%%'%(位置*100),4)

                输出='位置: %s, 匹配概览: ..."%s"...'%(位置字符串,字符串)
                print(输出)
                结果l.append(待匹配字符串.反颜色(输出))

        if 个数<len(文件地址_匹配结果l):
            print('(......剩%d个文件未显示)\n'%(len(文件地址_匹配结果l)-个数))
        else:
            print()
        if 输出到文件!=None and len(输出到文件)>0:
            with open(输出到文件,'w',encoding='utf-8') as w:
                for 一行 in 结果l:
                    w.write(一行+'\r\n')

    def 不断查询(self,每隔多久报一次结果=100,结果排序=True):
        while True:
            提示语='周围-i%d 大小-s%d 显示词-m%d 前几条-r%d：'%\
                (self.包含周围几个字符,
                 self.文件大小限制,
                 self.每个关键词最多几个匹配结果,
                 self.只显示前几条,
                 # self.取交集,
                 )
            文件地址_匹配结果l,输出路径=self._获得一次查询结果(每隔多久报一次结果,提示语)
            if 文件地址_匹配结果l==None or len(文件地址_匹配结果l)==0:
                print('没有匹配到结果!\n')
                continue
            self._输出匹配结果(文件地址_匹配结果l,self.只显示前几条,输出路径,结果排序)


执行者_obj=执行者(包含周围几个字符=20, # -i
            文件大小限制=100, # 单位:MB -s
            每个关键词最多几个匹配结果=1, # -m
            只显示前几条=30, # -r
            取交集=1, # -u 暂时没有实现此功能
            后缀名名单=['.txt','.md','.json','.tex',
                   '.c','.php','.css','.html','.js','.py','.m','.java','.cpp','.h','.htm'
                   ],
            命令正则式={'i':['(?<= -i)[0-9]+(?= )',' -i[0-9]+ '],
                   's':['(?<= -s)[0-9]+(?= )',' -s[0-9]+ '],
                   'm':['(?<= -m)[0-9]+(?= )',' -m[0-9]+ '],
                   'r':['(?<= -r)[0-9]+(?= )',' -r[0-9]+ '],
                   'u':['(?<= -u)[0-9]+(?= )',' -u[0-9]+ '],
                   }) # {编号:[提取正则式,删除替换正则式],..}
执行者_obj.不断查询(每隔多久报一次结果=90, # 单位:毫秒
             结果排序=True)


'''
待匹配文本._解析文件编码().超过一定行数跳出->加快解码速度
执行者._重要程度计算()->排序方式

修改命令对应需要修改->命令正则式,执行者._解析命令(),提示语,注释
'''