#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import re
from glob import glob
from tqdm import tqdm

def find_age_regex(d):
    string_pool = d['contents']
    l = re.findall(r'[만]*[\s]*[0-9]+[\s]*세[^가-힇()][\s]*[이]?[상하전후내외]?[미]?[만]?[초]?[과]?', string_pool)
    return [i.strip() for i in l]
def clean_item(d):
    d = d['age_list']
    data = [re.sub('[가의를인에로지]+', '', i) for i in d]
    return [i+'지' for i in data if i[-1]=='까']\
                +[i for i in data if i[-1]!='까'] \
                    +[i[:-2] for i in data if i[-1]=='이'] + [i+'세' for i in data if i[-1].isdigit()]

if __name__ == '__main__':
    files = glob('./data/*.csv')

    result = pd.DataFrame(columns=['title','contents'])
    print('데이터 병합중...\n')
    for ifile in tqdm(files):
        df = pd.read_csv(ifile)
        result = pd.concat([result,df], axis=0)

    print('타이틀 정규화중...\n')
    result['title'] = result['title'].apply(lambda x : x.strip() )
    result = result.reset_index(drop=True)



    print('타이틀 중복 제거중...\n')
    result = result.drop_duplicates(subset='title')
    result = result.set_index('title')

    print('법조문에서 연령 찾는중...\n')
    result['age'] = result.fillna('').apply(find_age_regex, axis=1)


    result = result.dropna() # 결측치 제거

    result_df = pd.DataFrame()
    cnt = 0
    print('법령 조문에서 연령 전체 찾는중...\n')
    for law in tqdm(result.index): # 법령명 하나의
        for text in result.loc[law]['contents'].split('.'): # 문장 . 으로 분리 후
            
            age_find = re.findall(r'[만]*[\s]*[0-9]+[\s]*세[^대환제트관임월][\s]*[이]?[상하전후내외]?[미]?[만]?[초]?[과]?[까]?[지]?[부]?[터]?', text)
            jo_text = re.findall(r'제[0-9]+조[의]?[0-9]?\([가-힇\s]+\)', text)
            if jo_text!=[]:
                cur_jo_text = jo_text
            if age_find:
                
                if jo_text: # 같은 조에 속할때
                    title = law
                    jo_title = cur_jo_text[0]
                    
                    age_list = [re.sub('[^0-9만세이상하전후내외미만초과까지부터]+', '', i) for i in age_find] # 한 줄 안에 여러 나이가 있을때
                    jo_contents = re.sub('[\[\]\>]', '', text) 
                    result_df = result_df.append({
                        'title':title,
                        'jo_title':jo_title,
                        'jo_contents': jo_contents,
                        'age_list': age_list
                    }, ignore_index=True)
                else: # 조 안에서 여러 줄로 나누어 져 있을때
                    jo_title = cur_jo_text[0]
                    jo_contents = re.sub('[\[\]\>]', '', text) 
                    title = law
                    age_list = [re.sub('[^A-Za-z0-9가-힣]', '', i) for i in age_find] # 한 줄 안에 여러 나이가 있을때
                    result_df = result_df.append({
                        'title':title,
                        'jo_title':jo_title,
                        'jo_contents': jo_contents,
                        'age_list': age_list
                    }, ignore_index=True)

    result_df['age_list'] = result_df.apply(clean_item, axis=1)

    result_df.to_json('data.json','records',force_ascii=False)
    print('완료하였습니다.')

 


