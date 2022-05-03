from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as dbb
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import plotly
import plotly.express as px
from flask_migrate import Migrate
import config



db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = 'super secret key'
migrate = Migrate()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ekdldksk@localhost:3306/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def index():
    return render_template("index.html")



@app.route('/login', methods=['POST'])
def login_():
    request.method = 'POST' 
    if request.form["id_"] == "asd" and request.form["pw_"] == "asd":
        return redirect(url_for("main"))
    else:
        return redirect(url_for("index"))


@app.route('/main')
def main():
    return render_template("main.html")


@app.route('/search', methods=['POST'])
def main_():
    request.method = 'POST' 
    name = request.form["search_"]
    start = request.form["start_date_"]
    end = request.form["end_date_"] 
    period_time = int(request.form["contact"])
    
    engine = dbb.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                                .format(host="ls-a20f4420f7aa9967e25c1e0aecf4d8b641af5f13.cgtgapkuvqbt.ap-northeast-2.rds.amazonaws.com",
                                        user="dbmasteruser",
                                        pw="r,3Ipn|O7mL2vL4S)9Q~;7QVdHMV6R9j",
                                        db="stock"))

    connection = engine.connect()
    metadata = dbb.MetaData()
    table = dbb.Table('date_index', metadata, autoload=True, autoload_with=engine)

    columns_pd = table.columns.keys()

    query = dbb.select([table])
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    
    date_index = pd.DataFrame(data=result_set, columns=columns_pd) 
    
    # 인덱스 가져오기
    ####################################################################################
    # 주식데이터 가져오기

    table = dbb.Table(name, metadata, autoload=True, autoload_with=engine)

    columns_pd = table.columns.keys()

    query = dbb.select([table])
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
   
    stock_data = pd.DataFrame(data=result_set, columns=columns_pd)

    #인덱스와 머지
    globals()[name]=pd.merge(date_index, stock_data , how='left', on='date')

    start_date = start+" 09:00:00"
    end_date = end+" 09:00:00"

    #int64index기 때문에 list로 변환후 0번째로 꺼내서 숫자로 설정
    first = globals()[name].index[globals()[name]['date'] == start_date].tolist()[0]
    last = globals()[name].index[globals()[name]['date'] == end_date].tolist()[0]
    
    #1날짜까지짜르고 2앞의값으로채우고 3인덱스리셋 4date타입을 스트링으로변경(차트빈공간채우기위함)
    globals()[name]=globals()[name].iloc[first:last+382,:]
    globals()[name]=globals()[name].fillna(method='ffill')
    #globals()[name]['date'] = globals()[name]['date'].apply(lambda x : datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))              
    #globals()[name]=globals()[name].set_index('date')    

    #radio값에 맞춰서 분봉설정
    globals()[name]=globals()[name].iloc[::period_time,:]

    each_df = globals()[name]

    fig = go.Figure(data=[go.Candlestick(x=each_df['date'],
                                    open=each_df['open'],
                                    high=each_df['high'],
                                    low=each_df['low'],
                                    close=each_df['close'])])
                # x축 type을 카테고리 형으로 설정, 순서를 오름차순으로 날짜순서가 되도록 설정
    fig.layout = dict(xaxis = dict(type="category", 
                                    categoryorder='category ascending'))
    fig.update_xaxes(nticks=5)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # header="Fruit in North America"
    # description = """
    # A academic study of the number of apples, oranges and bananas in the cities of
    # San Francisco and Montreal would probably not come up with this chart.
    # """
    return render_template("stock.html", graphJSON=graphJSON, df=each_df, name=name) #, header=header,description=description)


#@app.route('/stock/주식코드명')
#def main():
    #return render_template("main.html", chart_iplot=asd)




if __name__ == '__main__':
    app.run(port=5000, debug=True) #post는 여기로 옴



