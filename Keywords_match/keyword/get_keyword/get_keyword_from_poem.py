import re,json,os

all_poem_path = '/home/zkp/Z_train_command/ori_data/content.json'
output_path = '/home/zkp/Keywords_match/keyword/add_poem_keyword2.txt'

with open(all_poem_path,'r',encoding='utf-8') as f:
    data = json.load(f)

exist_title = set()

f = open(output_path,'a',encoding='utf-8')
for poem in data:
    title = (poem['title']+'·').split('·')[0]
    if title in exist_title:
        continue
    exist_title.add(title)
    f.write(title)
    f.write(' 200 nz\n')
    continue
    if title=='《金石录》后序' or title=='词论':
        continue
    content = poem['content']
    
    # 分割诗词内容
    sentences = [s.strip() for s in re.split(r'[。！？，]', content) if len(s.strip())>3]

    # f.write('title:'+title+'\n')
    f.write(' 200 nz\n'.join(sentences))
    f.write(' 200 nz\n')
    # f.write('\n'+"*"*100+'\n')

