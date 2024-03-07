from flask import Flask, render_template, request
from components.job_manage import JobManager
from components.template import system_prompt
from components.db import DB

app = Flask(__name__)

# Define your variables here
path = 'components/pkl_files'
pkl_tots = [f'{path}/tot_iwane1.pkl', f'{path}/tot_iwane2.pkl', f'{path}/tot_iwane3.pkl', f'{path}/tot_iwane4.pkl', f'{path}/tot_iwane5.pkl', f'{path}/tot_iwane6.pkl', f'{path}/tot_iwane7.pkl']
pkl_vecs = [f'{path}/vec_iwane1.pkl', f'{path}/vec_iwane2.pkl', f'{path}/vec_iwane3.pkl', f'{path}/vec_iwane4.pkl', f'{path}/vec_iwane5.pkl', f'{path}/vec_iwane6.pkl', f'{path}/vec_iwane7.pkl']
USER_NAME = "user"
ASSISTANT_NAME = "assistant"
USER_ID = "flask_test"
table_name = 'iwane'

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_msg = request.form["user_msg"]
        ai_message = create_ai_msg(user_msg)
        return render_template("index.html", user_msg=user_msg, assistant_msg=ai_message)

    return render_template("index.html", user_msg="", assistant_msg="")

def create_ai_msg(user_msg):
    chain_bot = JobManager(system_prompt, table_name, USER_ID, pkl_tots, pkl_vecs, model_name="gpt-4-1106-preview")
    DB_msg = chain_bot.get_info(user_msg)
    
    if DB_msg == 'NullQuery':
        DB_msg = ''
    
    if len(DB_msg) > 50:
        DB_msg_input = ' 参考:' + DB_msg
    else:
        DB_msg_input = ''
    
    ai_message = chain_bot.response(input=f'問合せ:{user_msg}{DB_msg_input}')
    return ai_message

if __name__ == "__main__":
    app.run(debug=True)
