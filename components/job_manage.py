import boto3
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import (
  ChatPromptTemplate,
  MessagesPlaceholder,
  SystemMessagePromptTemplate,
  HumanMessagePromptTemplate
)
from components.functions import retrieveDF2, remove_element
from components.pkl2 import read_pkls
from typing import List


# dynamoDBの設定
# dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"], aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"])
# client = boto3.client('dynamodb', region_name='ap-northeast-1', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"], aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"])


class JobManager():
  def __init__(self, template: str, table_name: str, USER_ID: str, pkl_tots: List[str], pkl_vecs: List[str], model_name: str="gpt-3.5-turbo-1106"):
    # LangChainの設定
    llm = ChatOpenAI(model_name=model_name, temperature=0.8)
    # message_history = DynamoDBChatMessageHistory(table_name=table_name, session_id=USER_ID)
    memory = ConversationBufferWindowMemory(
      return_messages=True, k=5
    )
    prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate.from_template(template),
      MessagesPlaceholder(variable_name="history"),
      HumanMessagePromptTemplate.from_template("{input}")
    ])
    self.chain = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    self.df_tot, self.df_vec = self.load_DB(pkl_tots, pkl_vecs)


  def response(self, input):
    return self.chain.predict(input=input)


  def load_DB(self, pkl_tots, pkl_vecs):
    embeddings = OpenAIEmbeddings()
    df_tot = read_pkls(pkl_files=pkl_tots)
    df_vec = read_pkls(pkl_files=pkl_vecs)
    return df_tot, df_vec


  def get_info(self, usr_msg): ## 2023-11-08
    df_hit=retrieveDF2(self.df_tot, self.df_vec, usr_msg)
    if df_hit is None:
      return("NoHits")
    df_hit=df_hit.drop(columns=['similarity']) # 2023-11-18 similarityを除外
    dic=df_hit.T.to_dict()
    ret=str(list(dic.values())).replace("'all':",'')  # json.dumps(dic,ensure_ascii=False) 2023-11-18　JSONだと、キーをLLMが勘違い
    while len(dic)>0:
      ret=str(list(dic.values())).replace("'all':",'')  # json.dumps(dic,ensure_ascii=False) 2023-11-18　JSONだと、キーをLLMが勘違い
      if len(ret)<1000: return ret              # 1000文字以下望ましい
      dic_old=dic
      remove_element(dic, list(dic.keys())[-1]) # lastの削除
    if len(ret)<2000: return ret                # 2000文字以下許容
    else:             return 'HitTooBig'        # 以上はToo Big