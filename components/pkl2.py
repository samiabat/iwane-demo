import pandas as pd
import pickle


# DataFrameをpickelファイルに保存する
def to_pkl(df:pd.core.frame.DataFrame,pkl_file:str) -> None:
  with open(pkl_file,"wb") as f:    pickle.dump(df, f)

# DataFrameをpickelファイルから読み込む
def read_pkl(pkl_file:str) -> pd.core.frame.DataFrame:
  try:
    with open(pkl_file, "rb") as f:    df = pickle.load(f)
  except FileNotFoundError :
    raise  FileNotFoundError(f'{pkl_file} is not found')
  except:
    raise
  return(df)

# DataFrameをlistで名称指定されたpickelファイル群に分割保存する
def to_pkls(df:pd.core.frame.DataFrame,pkl_files:list) -> pd.core.frame.DataFrame:
  N=len(pkl_files)
  M=len(df)
  L=int(M/N)+1
  for i in range(N):
    df1=df.loc[i*L:(i+1)*L-1]
#    print(f'{df1.index[0]}-{df1.index[-1]}: {pkl_files[i]}')
    to_pkl(df1,pkl_files[i])

def read_pkls(pkl_files):
  lst=[]
  for i, pkl in enumerate(pkl_files):
    try:
      df=read_pkl(pkl)
      lst += [df]
    except:
      raise FileNotFoundError(f'skip "{pkl}", because it is not found.')
  if lst == []:
    return None
  return pd.concat(lst)