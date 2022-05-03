from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as dbb
import pandas as pd
from datetime import datetime

db = SQLAlchemy()


class query_sql:
        def __init__(self):
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

                # query = db.select([table]).where(table.columns.password == '1234') 패스워드칼럼의 1234인것을 가져옴
                # query = db.select([table]).where(table.columns.password.isnot(None)) 눌체크를 위해서 사용

                # 이때 query의 내용을 출력해보면 sql query인 것을 알 수 있음
                # print(query)

                # 쿼리 실행
                result_proxy = connection.execute(query)
                result_set = result_proxy.fetchall()

                # 결과 print 이때 10개만 출력하도록 함. 단순한 set 자료구조의 형태를 하고 있음.
                
                self.date_index = pd.DataFrame(data=result_set, columns=columns_pd)

        def stock(self, name, date):
                engine = dbb.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                                .format(host="ls-a20f4420f7aa9967e25c1e0aecf4d8b641af5f13.cgtgapkuvqbt.ap-northeast-2.rds.amazonaws.com",
                                        user="dbmasteruser",
                                        pw="r,3Ipn|O7mL2vL4S)9Q~;7QVdHMV6R9j",
                                        db="stock"))

                connection = engine.connect()
                metadata = dbb.MetaData()
                table = dbb.Table(name, metadata, autoload=True, autoload_with=engine)

                columns_pd = table.columns.keys()

                query = dbb.select([table])

                # query = db.select([table]).where(table.columns.password == '1234') 패스워드칼럼의 1234인것을 가져옴
                # query = db.select([table]).where(table.columns.password.isnot(None)) 눌체크를 위해서 사용

                # 이때 query의 내용을 출력해보면 sql query인 것을 알 수 있음
                # print(query)

                # 쿼리 실행
                result_proxy = connection.execute(query)
                result_set = result_proxy.fetchall()

                # 결과 print 이때 10개만 출력하도록 함. 단순한 set 자료구조의 형태를 하고 있음.
                
                stock_data = pd.DataFrame(data=result_set, columns=columns_pd)

                globals()[name]=pd.merge(self.date_index, stock_data , how='left', on='date')

                until_date = date+" 09:00:00"

                #int64index기 때문에 list로 변환후 0번째로 꺼내서 숫자로 설정
                last = globals()[name].index[globals()[name]['date'] == until_date].tolist()[0]
                
                #1날짜까지짜르고 2앞의값으로채우고 3인덱스리셋 4date타입을 스트링으로변경(차트빈공간채우기위함)
                globals()[name]=globals()[name].iloc[:last,:]
                globals()[name]=globals()[name].fillna(method='ffill')
                #globals()[name]['date'] = globals()[name]['date'].apply(lambda x : datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))              
                # globals()[name]=globals()[name].set_index('date')                
                
#######################################################################################################################
#######################################################################################################################
# 차트그리기(start_date, end_date는 폼에서 가져오기)

class chart:
    def __init__(self, name):
        import cufflinks as cf
        cf.go_offline(connected=True)

        qf=cf.QuantFig( name,title='Samsung Quant Figure',legend='top',name=name) #원래는 타이틀과 네임이 있음!
        qf.add_bollinger_bands()
        qf.add_volume()
        qf.add_macd()
        qf.iplot()