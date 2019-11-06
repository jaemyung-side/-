from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import pymongo
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.flask_practice

@app.route('/review', methods=['GET'])
def find_movie_rank():
   rank = int(request.args.get('rank'))

   movies = list(db.movie_review.find({}, sort=[('star', pymongo.DESCENDING)]).limit(rank))
   target_movie = movies[-1]
   return jsonify({'result': 'success', 'name': target_movie['name'], 'rank':rank, 'star':target_movie['star']})

@app.route('/review', methods=['POST'])
def upload_user_review():
   user_id = request.form['user_id']
   movie_name = request.form['movie_name']
   star = float(request.form['star'])

   # user_review collection에 사용자 영화 리뷰 정보를 저장
   db.user_review.insert_one({'user_id':user_id, 'movie_name':movie_name, 'star':star})

   # 해당 영화의 리뷰 정보를 가져옴
   movie_info = db.movie_review.find_one({'name':movie_name})
   n_reviewer = movie_info['n_reviewer']
   mean_star = movie_info['star']

   mean_star = (mean_star * n_reviewer + star) / (n_reviewer + 1)
   n_reviewer += 1

   # 해당 영화의 정보를 업데이트함
   db.movie_review.update_one({'name':movie_name}, {'$set':{'star': mean_star, 'n_reviewer': n_reviewer}})

   return jsonify({'result': 'success'})

@app.route('/movie', methods=['GET'])
def get_movie_info():
   name = request.args.get('name')
   info = db.movies.find_one({'name': name}, {'_id':0})
   return jsonify({'result': 'success', 'name':info['name'], 'rank':info['rank'], 'star':info['star']})

@app.route('/movie', methods=['POST'])
def update_movie_rank():
   name = request.form['name']
   star = float(request.form['star'])
   update_result = db.movies.update_one({'name':name}, {'$set':{'star':star}})

   if update_result.matched_count == 0:
      return jsonify({'result': 'failure', 'msg': '해당 영화가 없습니다.'})
   if update_result.modified_count == 0:
      return jsonify({'result': 'failure', 'msg': '변경된 것이 없습니다.'})

   return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)