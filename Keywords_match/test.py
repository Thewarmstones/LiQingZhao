import jieba.posseg as pseg
# words = pseg.cut("你平时有什么爱好。他是谁？请背诵声声慢的全文。全文呢？表达了怎样的感情？你们的感情如何？可以讲讲你的爱好吗？")
# for word, flag in words:
#     print('%s %s'%(word,flag))


with open('/home/zkp/LiQingZhao/resources/Database/Keywords_match/keyword/show_.txt','r',encoding='utf-8') as f:
    data1 = f.readlines()

with open('/home/zkp/LiQingZhao/resources/Database/Keywords_match/keyword/add_poem_keyword.txt','r',encoding='utf-8') as f:
    data2 = f.readlines()

poem = set()
data = []
for e in data2:
    poem.add(e.split(' ')[0])
for e in data1:
    if e.split('\t')[0] not in poem:
        data.append(e)

with open('/home/zkp/LiQingZhao/resources/Database/Keywords_match/keyword/show.txt','w',encoding='utf-8') as f:
    f.write(''.join(data))
exit()

while True:
    query = input()
    for word,flag in pseg.cut(query):
        print(word,flag)