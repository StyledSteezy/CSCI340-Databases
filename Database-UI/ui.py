from flask import Flask, request, url_for, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import pandas as pd
from flask_table import Table, Col, LinkCol
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'postgresql://cslab:TacoSh%40ck@localhost:5432/dboverflow'
db = SQLAlchemy(app)


engine = create_engine('postgresql://cslab:TacoSh%40ck@localhost:5432/dboverflow')


class UserTable(Table):
    id = Col("Id")
    name = Col("User Name")
    about = Col("About this user")

class QuestionTable(Table):
    ownerid = Col("Owner ID")
    id = Col("Question ID")
    question = Col("Questions")

class AnswerTable(Table):
    ownerid = Col("Owners ID")   
    questionid = Col("Questions ID")
    answer = Col("Answers")
    
class HomeTable(Table):
    questionid = Col("Questions ID")
    question = Col("Questions")
    answer = Col("Answers")
    #questionid = LinkCol('QuestionID', 'soloqpage', url_kwargs=dict(id='id'))
    #id = LinkCol('id', 'questionspage', url_kwargs=dict(id='id'))

class SoloQPage(Table):
    id = LinkCol('id', 'questionspage', url_kwargs=dict(questionid='id'))

class AggregateTable(Table):
    id = Col("Question ID")
    creationdate = Col("Date")
    questionid = Col("Questions ID")
    question = Col("Question")
    answer = Col("Answer")


#Home page
@app.route('/')
@app.route('/home/')
def home():
    df = pd.read_sql_query("select questionid,question,answer from answers inner join questions on answers.questionid = questions.id;", con=engine)
    t = HomeTable(df.itertuples(index=False))
    return '<h1 style="; text-align: center">Home page</h1>' + '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + '<p><a href="http://127.0.0.1:5000/users/">Visit Users page</a></p>' +'<h1 style="; text-align: left">Browse questions and answers:</h1>' + t.__html__()

@app.route('/soloqpage/')
def SoloQPage():
    df = pd.read_sql_query(text("SELECT * FROM questions WHERE id = :id"), params={id: request.args['id']}, con=engine)
    t = SoloQPage(df.itertuples(index=False))
    return t.__html__()

#Users page
@app.route('/users/')
def users():
    df = pd.read_sql_query("select id, name, about from users", con=engine)
    t = UserTable(df.itertuples(index=False))
    return '<p><a href="http://127.0.0.1:5000/home/">Visit Home Page</a></p>' + '<p><a href="http://127.0.0.1:5000/questions/">Visit Questions page</a></p>' + t.__html__() # df.to_html()


#Unable to get this to work
@app.route('/postquestion/')
def PostQuestion():
    your_question = raw_input("What is your question? - ")
    your_id = raw_input("What is your id? - ")
    with engine.connect() as con:
        statement = text(pd.read_sql_query('insert into questions (question, ownerid) values(' + str(your_question) + ',' + your_id + ')', con=engine))
    return statement
#If you really need to post a question just run this code ;) -> INSERT INTO questions (question, ownerid) VALUES ('your_question', your_id);

#Unable to get this to work
@app.route('/postanswer/')
def PostAnswer():
    your_answer = raw_input("Input answer - ")
    the_questionid = raw_input("What is the question id? - ")
    with engine.connect() as con:
        statement = text(pd.read_sql_query('insert into answers (answer, ownerid,' + the_questionid + ') values(' + str(your_answer) + ',' + the_questionid + ')', con=engine))
    return statement
#If you really need to answer a question just run this code ;) -> INSERT INTO answers (answer, ownerid, questionid) VALUES ("I'm an answer", 8, 144) RETURNING id

#Questions page
@app.route('/questions/')
def questions():
    df = pd.read_sql_query("select id,ownerid,question from questions", con=engine)
    t = QuestionTable(df.itertuples(index=False))
    return '<p><a href="http://127.0.0.1:5000/users/">Visit Users page</a></p>' + t.__html__()


# Basic aggregate information about the database/website
@app.route('/aggregateinfo/')
def aggregateinfo():
    return '<h1 style=" text-align: left">Some basic aggregate information:</h1>' + '<p><a href="http://127.0.0.1:5000/home/">Visit Home Page</a></p>' + '<p><a href="http://127.0.0.1:5000/tsq/">Top Scoring Question</a></p>' + '<p><a href="http://127.0.0.1:5000/luq/">Longest Unanswered Questions</a></p>' + '<p><a href="http://127.0.0.1:5000/dwmqa/">Day With Most Questions Asked</a></p>' + '<p><a href="http://127.0.0.1:5000/dwmag/">Day With Most Answers Given</a></p>' + '<p><a href="http://127.0.0.1:5000/mau/">Most Active User</a></p>'

@app.route('/tsq/')
def TopScoringQuestion():
    tsq = pd.read_sql_query("select id,upvote - downvote as score from votecounts order by score desc limit 5", con=engine).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + tsq

@app.route('/luq/')
def LongestUnansweredQuestion():
    luq = pd.read_sql_query("select id,creationdate::date from questions where id not in (select questionid from answers) order by creationdate asc limit 5", con=engine).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + luq

@app.route('/dwmqa/')
def DayWithMostQuestionsAsked():
    dwmqa = pd.read_sql_query("select count(id),creationdate::date as date from questions group by date order by count(id) desc limit 1;", con=engine).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + dwmqa

@app.route('/dwmag/')
def DayWithMostAnswersGiven():
    dwmag = pd.read_sql_query("select count(id),creationdate::date as date from answers group by date order by count(id) desc limit 1;", con=engine).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + dwmag

@app.route('/mau/')
def MostActiveUser():
    mau = pd.read_sql_query("select ownerid,count(ownerid) from (select id,ownerid from questions union select id,ownerid from answers) as activities group by ownerid order by count desc limit 1;", con=engine).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + mau

'''
All of this was working and it looked much better than the output of the code above, but then it randomly stopped working..
It game me this error -> OperationalError: (sqlite3.OperationalError) no such table: answers
(Background on this error at: http://sqlalche.me/e/e3q8)
This was very annoying and set me back. I had to redo all of the basic aggregate information in a new way that did not look as nice as before.
'''

'''
@app.route('/tsq/')
def TopScoringQuestion():
    df = pd.DataFrame(db.engine.execute('select id,upvote - downvote as x from votecounts order by x desc limit 5'),columns=['QuestionID','Score']).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + df

@app.route('/luq/')
def LongestUnansweredQuestion():
    df = pd.DataFrame(db.engine.execute('select id,creationdate::date from questions where id not in (select questionid from answers) order by creationdate asc limit 5'),columns=['QuestionID','Date']).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + df

@app.route('/dwmqa/')
def DayWithMostQuestionsAsked():
    df = pd.DataFrame(db.engine.execute('select count(id),creationdate::date as x from questions group by x order by count(id) desc limit 1;'),columns=['Questions Asked','Date']).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + df

@app.route('/dwmag/')
def DayWithMostAnswersGiven():
    df = pd.DataFrame(db.engine.execute('select count(id),creationdate::date as x from answers group by x order by count(id) desc limit 1;'),columns=['Answers Given','Date']).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + df

@app.route('/mau/')
def MostActiveUser():
    df = pd.DataFrame(db.engine.execute('select ownerid,count(ownerid) from (select id,ownerid from questions union select id,ownerid from answers) as x group by ownerid order by count desc limit 1;'),columns=['User ID','Number Of Activities']).to_html()
    return '<p><a href="http://127.0.0.1:5000/aggregateinfo/">Visit Aggregate Info Page</a></p>' + df
'''


if __name__ == '__main__':
    app.run(debug=True)
