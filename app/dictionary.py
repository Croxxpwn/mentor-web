# -*- coding:utf-8 -*-
import cPickle
from datetime import time


# DYNAMIC

class TimeInfo:
    def __init__(self, day, time_start,time_end, times):
        self.day = day
        self.time_start = time_start
        self.time_end = time_end
        self.times = times


men_id2timelist = {}


def reload_dynamic_data():
    DYNAMIC_DIR_PATH = 'app/static/res/dynamic/'
    global men_id2timelist
    men_id2timelist = cPickle.load(open(DYNAMIC_DIR_PATH + 'data_men_id2timelist', 'rb'))


def write_dynamic_data():
    DYNAMIC_DIR_PATH = 'app/static/res/dynamic/'
    cPickle.dump(men_id2timelist, open(DYNAMIC_DIR_PATH + 'data_men_id2timelist', 'wb'), True)


def getMentorTimeInfos(men_id):
    timelist = men_id2timelist if men_id in men_id2timelist else []
    return timelist


def clearMentorTimeInfos(men_id):
    men_id2timelist[men_id] = []
    write_dynamic_data()


def addMentorTimeInfo(men_id, timeinfo):
    if men_id in men_id2timelist:
        men_id2timelist[men_id] = []
    men_id2timelist[men_id].append(timeinfo)
    write_dynamic_data()


# STATIC

department_id2name = {
    '020400': u'宣传部/新闻中心',
    '011200': u'外国语学院',
    '011600': u'飞行学院',
    '021700': u'财务处',
    '023000': u'招标采购管理中心',
    '022800': u'国内合作办公室',
    '020800': u'安全保卫部（处）',
    '011300': u'交通科学与工程学院',
    '021600': u'人事处/人才工作办公室',
    '010100': u'材料科学与工程学院',
    '012500': u'国际学院',
    '040900': u'网络信息中心',
    '011400': u'可靠性与系统工程学院',
    '021900': u'国际交流合作处/港澳台事务办公室',
    '021500': u'研究生院',
    '050300': u'航空期刊杂志社',
    '012400': u'中法工程师学院',
    '012200': u'继续教育学院',
    '011500': u'宇航学院',
    '022900': u'法律事务办公室',
    '012800': u'马克思主义学院',
    '010600': u'计算机学院',
    '022200': u'资产管理处',
    '050600': u'北航实验学校小学部',
    '013000': u'工程训练中心',
    '012300': u'高等理工学院',
    '050100': u'后勤集团',
    '040100': u'沙河校区管理与建设委员会',
    '020600': u'纪委办公室、监察处',
    '011700': u'仪器科学与光电工程学院',
    '041100': u'国际交叉科学研究院',
    '050400': u'校医院',
    '010400': u'能源与动力工程学院',
    '040600': u'校友总会',
    '020900': u'保密处',
    '013400': u'北斗丝路学院',
    '020500': u'统战部',
    '010700': u'机械工程及自动化学院',
    '022600': u'科学技术研究院',
    '020700': u'学生工作部（处）、武装部',
    '040700': u'北航学报编辑部',
    '012700': u'化学学院',
    '013500': u'国际通用工程学院',
    '020000': u'机关部处',
    '010200': u'电子信息工程学院',
    '040400': u'北航教育基金会',
    '022300': u'后勤保障处/后勤党委',
    '010500': u'航空科学与工程学院',
    '012600': u'新媒体艺术与设计学院',
    '020100': u'党政办公室',
    '013800': u'医工交叉创新研究院',
    '040500': u'档案馆/校史馆',
    '011000': u'生物与医学工程学院',
    '011800': u'北京学院',
    '012100': u'软件学院',
    '013100': u'体育部',
    '020200': u'发展规划处（部）',
    '041000': u'人才交流中心',
    '011100': u'人文社会科学学院（公共管理学院）',
    '050700': u'北航资产经营有限公司',
    '012000': u'法学院',
    '020300': u'组织部/党校',
    '011900': u'物理科学与核能工程学院',
    '021800': u'审计处',
    '010900': u'数学与系统科学学院',
    '000000': u'学校领导',
    '030200': u'校团委',
    '010300': u'自动化科学与电气工程学院',
    '041200': u'国家实验室办公室',
    '030100': u'校工会',
    '050500': u'北航实验学校中学部',
    '010800': u'经济管理学院',
    '022000': u'招生就业处/招生办公室/学生就业指导服务中心',
    '021100': u'教务处',
    '013300': u'空间与环境学院',
    '022500': u'离退休党委/离退休工作处',
    '023100': u'校园规划建设与资产管理处',
    '013200': u'人文与社会科学高等研究院',
    '022400': u'校园规划与基本建设处',
    '021000': u'机关党委（机关行政办公室）',
    '012900': u'无人机研究所',
    '040800': u'图书馆',
    '030300': u'北航科协',
    '017300': u'士谔书院',
    '017400': u'冯如书院',
    '017500': u'士嘉书院',
    '017600': u'守锷书院',
    '017700': u'致真书院',
    '017900': u'知行书院',
    '019900': u'航空科学与技术国家实验室大飞机班',
}
department_name2id = {
    u'宣传部/新闻中心': '020400',
    u'外国语学院': '011200',
    u'飞行学院': '011600',
    u'财务处': '021700',
    u'招标采购管理中心': '023000',
    u'国内合作办公室': '022800',
    u'安全保卫部（处）': '020800',
    u'交通科学与工程学院': '011300',
    u'人事处/人才工作办公室': '021600',
    u'材料科学与工程学院': '010100',
    u'国际学院': '012500',
    u'网络信息中心': '040900',
    u'可靠性与系统工程学院': '011400',
    u'国际交流合作处/港澳台事务办公室': '021900',
    u'研究生院': '021500',
    u'航空期刊杂志社': '050300',
    u'中法工程师学院': '012400',
    u'继续教育学院': '012200',
    u'宇航学院': '011500',
    u'法律事务办公室': '022900',
    u'马克思主义学院': '012800',
    u'计算机学院': '010600',
    u'资产管理处': '022200',
    u'北航实验学校小学部': '050600',
    u'工程训练中心': '013000',
    u'高等理工学院': '012300',
    u'后勤集团': '050100',
    u'沙河校区管理与建设委员会': '040100',
    u'纪委办公室、监察处': '020600',
    u'仪器科学与光电工程学院': '011700',
    u'国际交叉科学研究院': '041100',
    u'校医院': '050400',
    u'能源与动力工程学院': '010400',
    u'校友总会': '040600',
    u'保密处': '020900',
    u'北斗丝路学院': '013400',
    u'统战部': '020500',
    u'机械工程及自动化学院': '010700',
    u'科学技术研究院': '022600',
    u'学生工作部（处）、武装部': '020700',
    u'北航学报编辑部': '040700',
    u'化学学院': '012700',
    u'国际通用工程学院': '013500',
    u'机关部处': '020000',
    u'电子信息工程学院': '010200',
    u'北航教育基金会': '040400',
    u'后勤保障处/后勤党委': '022300',
    u'航空科学与工程学院': '010500',
    u'新媒体艺术与设计学院': '012600',
    u'党政办公室': '020100',
    u'医工交叉创新研究院': '013800',
    u'档案馆/校史馆': '040500',
    u'生物与医学工程学院': '011000',
    u'北京学院': '011800',
    u'软件学院': '012100',
    u'体育部': '013100',
    u'发展规划处（部）': '020200',
    u'人才交流中心': '041000',
    u'人文社会科学学院（公共管理学院）': '011100',
    u'北航资产经营有限公司': '050700',
    u'法学院': '012000',
    u'组织部/党校': '020300',
    u'物理科学与核能工程学院': '011900',
    u'审计处': '021800',
    u'数学与系统科学学院': '010900',
    u'学校领导': '000000',
    u'校团委': '030200',
    u'自动化科学与电气工程学院': '010300',
    u'国家实验室办公室': '041200',
    u'校工会': '030100',
    u'北航实验学校中学部': '050500',
    u'经济管理学院': '010800',
    u'招生就业处/招生办公室/学生就业指导服务中心': '022000',
    u'教务处': '021100',
    u'空间与环境学院': '013300',
    u'离退休党委/离退休工作处': '022500',
    u'校园规划建设与资产管理处': '023100',
    u'人文与社会科学高等研究院': '013200',
    u'校园规划与基本建设处': '022400',
    u'机关党委（机关行政办公室）': '021000',
    u'无人机研究所': '012900',
    u'图书馆': '040800',
    u'北航科协': '030300',
    u'士谔书院': '017300',
    u'冯如书院': '017400',
    u'士嘉书院': '017500',
    u'守锷书院': '017600',
    u'致真书院': '017700',
    u'知行书院': '017900',
    u'航空科学与技术国家实验室大飞机班': '019900',
}

tag1totag2 = {
    'CYJQY99': ['CGDCHCL', 'CXYWRJ0', 'CZNXT00', 'CXTJG00', 'CXNXS00', 'CRGZN00', 'CRJJH00', 'CSWTZSB', 'CJQXX00',
                'CDSJ000', 'CQKL000', 'CXJWCXJ', 'CHLWJR0', 'CJYWLKX', 'CZHWL00', 'CNMFSCL', 'CFSGFNC', 'CWXTX00',
                'CTXCL00', 'CHKJTWL'],
    'DSWNLGL': ['DDXKJC0', 'DCXSW00', 'DYSSW00', 'DXSGL00', 'DLJSW00', 'DSJGL00', 'DZSGL00', 'DXXDL00', 'DSWJS00',
                'DQXGL00', 'DSXSW00'],
    'ESYZDFX': ['EHWLX00', 'EGJQYZD', 'EHWYJ00', 'EXLZX00', 'EXYGH00', 'EZYSY00', 'EZYXZ00'],
    'AJCXX99': ['AZDKZYL', 'AYY0000', 'AJSJZC0', 'AXXDS00', 'AGKGS00', 'AGKSF00', 'ASZFX00', 'AJGLX00', 'ASLX000',
                'AGKDW00', 'ADWSY00', 'AHXCL00', 'ATXDCJR'],
    'BKYCX99': ['BXKJS00', 'BFRB000', 'BSXJM00', 'BTZB000', 'BGCSJ00', 'BDC0000'],
}

tag2totag1 = {
    'AJSJ000': 'AJCXX99',
    'AZDKZYL': 'AJCXX99',
    'AYY0000': 'AJCXX99',
    'AJSJZC0': 'AJCXX99',
    'AXXDS00': 'AJCXX99',
    'AGKGS00': 'AJCXX99',
    'AGKSF00': 'AJCXX99',
    'ASZFX00': 'AJCXX99',
    'AJGLX00': 'AJCXX99',
    'ASLX000': 'AJCXX99',
    'AGKDW00': 'AJCXX99',
    'ADWSY00': 'AJCXX99',
    'AHXCL00': 'AJCXX99',
    'BXSLWXZ': 'BKYCX99',
    'BXKJS00': 'BKYCX99',
    'BFRB000': 'BKYCX99',
    'BSXJM00': 'BKYCX99',
    'BTZB000': 'BKYCX99',
    'BGCSJ00': 'BKYCX99',
    'BDC0000': 'BKYCX99',
    'CTYNDC0': 'CYJQY99',
    'CGDCHCL': 'CYJQY99',
    'CXYWRJ0': 'CYJQY99',
    'CZNXT00': 'CYJQY99',
    'CXTJG00': 'CYJQY99',
    'CXNXS00': 'CYJQY99',
    'CRGZN00': 'CYJQY99',
    'CRJJH00': 'CYJQY99',
    'CSWTZSB': 'CYJQY99',
    'CJQXX00': 'CYJQY99',
    'CDSJ000': 'CYJQY99',
    'CQKL000': 'CYJQY99',
    'CXJWCXJ': 'CYJQY99',
    'CHLWJR0': 'CYJQY99',
    'CJYWLKX': 'CYJQY99',
    'CZHWL00': 'CYJQY99',
    'CNMFSCL': 'CYJQY99',
    'CFSGFNC': 'CYJQY99',
    'DQYGL00': 'DSWNLGL',
    'DDXKJC0': 'DSWNLGL',
    'DCXSW00': 'DSWNLGL',
    'DYSSW00': 'DSWNLGL',
    'DXSGL00': 'DSWNLGL',
    'DLJSW00': 'DSWNLGL',
    'DSJGL00': 'DSWNLGL',
    'DZSGL00': 'DSWNLGL',
    'DXXDL00': 'DSWNLGL',
    'DSWJS00': 'DSWNLGL',
    'DQXGL00': 'DSWNLGL',
    'DSXSW00': 'DSWNLGL',
    'EXGLX00': 'ESYZDFX',
    'EHWLX00': 'ESYZDFX',
    'EGJQYZD': 'ESYZDFX',
    'EHWYJ00': 'ESYZDFX',
    'EXLZX00': 'ESYZDFX',
    'EXYGH00': 'ESYZDFX',
    'EZYSY00': 'ESYZDFX',
    'EZYXZ00': 'ESYZDFX',
    'ATXDCJR': 'AJCXX99',
    'CWXTX00': 'CYJQY99',
    'CTXCL00': 'CYJQY99',
    'CHKJTWL': 'CYJQY99',
}

tag1toname = {
    'AJCXX99': u'基础学习',
    'BKYCX99': u'科研创新',
    'CYJQY99': u'研究前沿',
    'DSWNLGL': u'思维与管理能力',
    'ESYZDFX': u'生涯指导方向',
}

tag2toname = {
    'AJSJ000': u'计算机',
    'AZDKZYL': u'自动控制原理',
    'AYY0000': u'英语',
    'AJSJZC0': u'计算机组成',
    'AXXDS00': u'线性代数',
    'AGKGS00': u'工科高数',
    'AGKSF00': u'工科数分',
    'ASZFX00': u'数值分析',
    'AJGLX00': u'结构力学',
    'ASLX000': u'水力学',
    'AGKDW00': u'工科大物',
    'ADWSY00': u'大物实验',
    'AHXCL00': u'化学材料',
    'BXSLWXZ': u'学术论文写作',
    'BXKJS00': u'学科竞赛',
    'BFRB000': u'冯如杯',
    'BSXJM00': u'数学建模',
    'BTZB000': u'挑战杯',
    'BGCSJ00': u'工程实践',
    'BDC0000': u'大创',
    'CTYNDC0': u'太阳能电池',
    'CGDCHCL': u'光电催化材料',
    'CXYWRJ0': u'旋翼无人机',
    'CZNXT00': u'智能系统',
    'CXTJG00': u'系统结构',
    'CXNXS00': u'虚拟现实',
    'CRGZN00': u'人工智能',
    'CRJJH00': u'人机交互',
    'CSWTZSB': u'生物特征识别',
    'CJQXX00': u'机器学习',
    'CDSJ000': u'大数据',
    'CQKL000': u'区块链',
    'CXJWCXJ': u'先进微成形技术',
    'CHLWJR0': u'互联网金融',
    'CJYWLKX': u'基因网络科学',
    'CZHWL00': u'智慧物流',
    'CNMFSCL': u'仿生纳米材料',
    'CFSGFNC': u'仿生高分子凝胶材料',
    'DQYGL00': u'企业管理',
    'DDXKJC0': u'多学科交叉',
    'DCXSW00': u'创新思维',
    'DYSSW00': u'艺术思维',
    'DXSGL00': u'学生管理',
    'DLJSW00': u'逻辑思维',
    'DSJGL00': u'时间管理',
    'DZSGL00': u'知识管理',
    'DXXDL00': u'学习动力',
    'DSWJS00': u'思维技术',
    'DSXSW00': u'数学思维',
    'DQXGL00': u'情绪管理',
    'EXGLX00': u'香港留学',
    'EHWLX00': u'海外留学',
    'EGJQYZD': u'国际前沿引导',
    'EHWYJ00': u'海外研究',
    'EXLZX00': u'心理咨询',
    'EXYGH00': u'学业规划',
    'EZYSY00': u'职业生涯',
    'EZYXZ00': u'专业选择',
    'ATXDCJR': u'天线与电磁兼容',
    'CWXTX00': u'无线通信',
    'CTXCL00': u'图像处理',
    'CHKJTWL': u'航空交通网络',
}

review_type_id2string = {
    0: u'其他类',
    1: u'学业类',
    2: u'心理类',
    3: u'成长类',
}
