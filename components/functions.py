import numpy as np
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings


def index_of(txt, sub):
  if txt.count(sub)<=0: 
    return -99
  else:
    return txt.index(sub)


def index_of2(txt, subs):
  ret=99999
  if isinstance(txt,list):
    for sub in subs:
      if txt.count(sub)>0:
        r=txt.index(sub)
        if ret>r: ret=r
  elif isinstance(txt,str):
    sub=subs
    if txt.count(sub)>0:
      r=txt.index(sub)
      if ret>r: ret=r
  if ret>999: return -99
  return ret


def yen_of(v):  # 文字列 -> XX 円 (実数)
  margin=1
  mult=1
  i=index_of(v,'円')
  if i>=0: v=v[:i]
  i= index_of(v,'約')
  if i>=0:
    v=v[i+1:]
    margin=0.9
  i=index_of(v,'万')
  if i>=0:
    v=v[:i]
    mult=10000
  i=index_of(v,'千')
  if i>=0:
    v=v[:i]
    mult=1000
  while v[0] not in ['0','1','2','3','4','5','6','7','8','9']:
    v=v[1:]
    if v == '': return -999
  v=v.replace(',','')
  return(float(v)*mult*margin)


def cos_similarity(vec1,vec2):
  vec1 = np.array(vec1)
  vec2 = np.array(vec2)
  return np.dot(vec1,vec2)/np.sqrt(np.dot(vec1,vec1)*np.dot(vec2,vec2))


def is_OK(v):     # 部分文字列検索に相応しいか？
  if len(v)<=0: return  False
  for NG in [ '空白', '不明', 'いずれか','もしくは','なし','ない','ありませ','以外','、', '?']:
    if v.count(NG): return False
  if len(v)<=0:     return False
  if v in [' ','　']: return False
  return True


def message2tuples(lines, line_user_id):  # parser_message -> query_tuples
  keys=['時給:','月給:','雇用形態:','勤務地:','資格:','経験:','職種:','スキルセット:','その他:']
  query_tuples=[]
  query_similar=''
  lines=lines.replace(':',':')
  for k,key in enumerate(keys):
    key=key.replace(':',':')
    v=''
    for line in lines.split('\n'):
      i=index_of(line,key)
      if i>=0:
        j=index_of(line[i:],':')
        v=line[i+j+1:]
    if is_OK(v):
      if key in ['時給:','月給:']:
        yen=yen_of(v)
        if key in ['月給:']:     query_tuples += [('LowerMonthlySalary','>',yen)]
        elif key in ['時給:']:    query_tuples += [('LowerHourlyWage','>',yen)]
      elif key in  ['資格:','経験:','職種:','スキルセット:','その他:']:
        if key in  ['スキルセット:']:        query_similar += '資格など:'+ v + ', '
        elif key in  ['職種:']:              query_similar += '仕事内容:'+ v + ', '
        query_similar += key + v + ', '
      else:
        if key in ['雇用形態:'] and v not in ['正社員','派遣社員','パート']: continue
        for NG in ['を希望','が希望','の希望','希望','内']:
          if index_of(v,NG)>0 : v=v[: index_of(v,NG)]
        query_tuples += [(key[:-1],'∋',v)]
  if len(query_similar)>1: query_tuples += [('','≒',query_similar)]
  return(query_tuples)


def retrieveDF2(df_tot,df_vec,query_txt): ## 2023-11-08
  rows = [True for a in df_vec.index]      # 全て検索対象
  df_sim = get_similarity2(df_vec,query_txt,rows)
  return pd.concat([df_sim,df_tot['all']],axis=1,join='inner')


def cal_similarity(df_vec,query_txt,rows=None,cols=None):
  embeddings = OpenAIEmbeddings()
  if rows == None:  rows = [True for a in df_vec.index]
  if cols == None:  cols = list(df_vec.columns.values)
  sim_vec = [-999 for a in rows]
  col_vec = [-999 for a in rows]
  vec1=np.array( embeddings.embed_query(str(query_txt)))
  smax,idx_max,col_max=-999,-999,-999
  for i,idx in enumerate(df_vec.index):
    if not rows[i]:continue
    for j,col in enumerate(cols):
      vec2 = df_vec.loc[idx,col]
      if vec2.iloc[0] == 'nan': continue
      s=cos_similarity(vec1,vec2)
      if sim_vec[i]<s:
        sim_vec[i]=s
        col_vec[i]=col
        if smax < sim_vec[i]:
          smax=sim_vec[i]
          idx_max,col_max=idx,col
  return sim_vec,smax,idx_max,col_max,col_vec


def get_similarity2(df_vec,query_txt,rows): ## 2023-11-08
  # query_txtに格納されたvectorとdf_vecとの類似性を計算し、best 5を返す
  sim_vec,smax,idx_max,col_max,col_vec = cal_similarity(df_vec,query_txt,rows=rows)
  if smax < 0: return None
  df_sim = pd.DataFrame({'similarity':sim_vec},index=df_vec.index)
  return df_sim.sort_values('similarity', ascending=False).head(5) 


def remove_element(dictionary, key):
  if key in dictionary:
    value = dictionary.pop(key)
    return value
  else:
    raise KeyError(f'Key "{key}" not found in dictionary')


def take_col(job_msg_json, col_name):
  col_array = []
  for entry in job_msg_json.values():
    url = entry.get(col_name)
    if url:
      col_array.append(url)
  return col_array


def match_company_inMessage(txt):
  df = pd.read_pickle('components/pkl_files/hire1200.pkl')
  company_names = set(df['会社名'])
  flag = any(company in txt for company in company_names)
  return flag


def match_url_inMessage(txt):
  if 'https://' in txt or 'http://' in txt:
    flag = True
  return flag