from components.job_manage import JobManager
from components.template import system_prompt
from components.db import DB
import streamlit as st



# 変数の定義
pkl_tot = 'components/pkl_files/tot_iwane.pkl'
pkl_vec = 'components/pkl_files/vec_iwane.pkl'
table_name = 'iwane'


st.title("大構想chat")

# 定数定義
USER_NAME = "user"
ASSISTANT_NAME = "assistant"
USER_ID = "st_demo"


def create_ai_msg(user_msg: str):
    chain_bot = JobManager(system_prompt, pkl_tot, pkl_vec, table_name, user_msg, model_name="gpt-4-1106-preview")
    db = DB('iwane-DBmsg', USER_ID)
    DB_msg = chain_bot.get_info(user_msg)
    if DB_msg == 'NullQuery' or DB_msg == '':
      DB_msg = db.get_item_if_exists()
    if len(DB_msg) > 50: 
      DB_msg_input = ' 参考:'+ DB_msg
    else:
      DB_msg_input = ''
    ai_message = chain_bot.response(input=f'問合せ:{user_msg}{DB_msg_input}')
    return ai_message


# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

custom_css = """
<style>
  .stApp{
    background: url('https://drive.google.com/file/d/1XZm6POLwuBqy3iTEp3_tfr4TLsn3c6Xe/view?usp=drive_link');
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
  }
  .stChatInputContainer textarea {
      height: 150px;
  }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
user_msg = st.chat_input("ここにメッセージを入力")
if user_msg:
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.write(chat["msg"])

    # 最新のメッセージを表示
    with st.chat_message(USER_NAME):
        st.write(user_msg)

    # アシスタントのメッセージを表示
    ai_message = create_ai_msg(user_msg)
    with st.chat_message(ASSISTANT_NAME):
        assistant_msg = ""
        assistant_response_area = st.empty()
        for chunk in ai_message:
            # 回答を逐次表示
            # tmp_assistant_msg = chunk["choices"][0]["delta"].get("content", "")
            tmp_assistant_msg = chunk
            assistant_msg += tmp_assistant_msg
            assistant_response_area.write(assistant_msg)

    # セッションにチャットログを追加
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})