from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as dbb
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


app = Flask(__name__)
app.secret_key = 'super secret key'



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


@app.route('/stock')
def main():
    return render_template("main.html", chart_=None, df=None)

def search(name, date):
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

    until_date = date+" 09:00:00"

    #int64index기 때문에 list로 변환후 0번째로 꺼내서 숫자로 설정
    last = globals()[name].index[globals()[name]['date'] == until_date].tolist()[0]
    
    #1날짜까지짜르고 2앞의값으로채우고 3인덱스리셋 4date타입을 스트링으로변경(차트빈공간채우기위함)
    globals()[name]=globals()[name].iloc[:last,:]
    globals()[name]=globals()[name].fillna(method='ffill')
    #globals()[name]['date'] = globals()[name]['date'].apply(lambda x : datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))              
    #globals()[name]=globals()[name].set_index('date')    

    each_df = globals()[name]

    fig = go.Figure(data=[go.Candlestick(x=name['date'],
                                    open=name['open'],
                                    high=name['high'],
                                    low=name['low'],
                                    close=name['close'])])
                # x축 type을 카테고리 형으로 설정, 순서를 오름차순으로 날짜순서가 되도록 설정
    fig.layout = dict(xaxis = dict(type="category", 
                                    categoryorder='category ascending'))
    fig.update_xaxes(nticks=5)
    send_html = fig.to_html()

    return render_template("main.html", df=each_df, chart_=send_html)


#@app.route('/stock/주식코드명')
#def main():
    #return render_template("main.html", chart_iplot=asd)


if __name__ == '__main__':
    app.run(port=5000, debug=True) #post는 여기로 옴



