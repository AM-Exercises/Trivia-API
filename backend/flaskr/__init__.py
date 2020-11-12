import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
  # create and configure the app
      app = Flask(__name__)
      setup_db(app)
      cors = CORS(app)


      @app.after_request
      def after_request(response):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response

      '''
      Create an endpoint to handle GET requests
      for all available categories.
      '''
  
      @app.route('/categories', methods=['GET'])
      def get_categories():
            categories = Category.query.all()
      
            if len(categories) == 0:
                  abort(404)

            return jsonify({
                  "success":True,
                  "categories":{category.id: category.type for category in categories}
            })
      ''' 
       Create an endpoint to handle GET requests for questions, 
       including pagination (every 10 questions). 
       This endpoint should return a list of questions, 
       number of total questions, current category, categories. 

      TEST: At this point, when you start the application
      you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions. 
      '''

      def paginate_questions(request,selection):
            page = request.args.get('page',1,type =int)
            start = QUESTIONS_PER_PAGE * (page-1)
            end = start+QUESTIONS_PER_PAGE
            questions = [question.format() for question in selection]
            return questions[start:end]


      @app.route('/questions', methods=['GET'])
      def get_questions():
            questions =  Question.query.all()
            current_questions= paginate_questions(request,questions)

            categories = Category.query.all()
           
            if len(current_questions) == 0:
                  abort(404)
        
            return jsonify({
                  "success":True,
                  "total_questions":len(questions),
                  "questions":current_questions,
                  "categories":{category.id: category.type for category in categories},
                  "current_category":None
            })

      '''
      Create an endpoint to DELETE question using a question ID. 

      TEST: When you click the trash icon next to a question, the question will be removed.
      This removal will persist in the database and when you refresh the page. 
      '''

      @app.route('/questions/<int:question_id>' , methods=['DELETE'])
      def delete_question(question_id):
            question = Question.query.get(question_id)
            if not question:
                  abort(404)
            try:
                  question.delete()
                  questions = Question.query.all()
                  current_questions = paginate_questions(request, questions)
                  return jsonify ({
                        "success":True,
                        "question_id":question_id,
                        "current_questions":current_questions,
                        'total_questions': len(questions)

                  })
            except:
                  abort(422)
      

      ''' 
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  
      '''

      @app.route('/questions', methods=["POST"])
      def create_question():
            try:
                  body = request.get_json()

                  question = body.get("question")
                  answer = body.get("answer")
                  category = body.get("category")
                  difficulty = body.get("difficulty")

                  question = Question(question=question,answer=answer,category=category,difficulty=difficulty)
                  question.insert()

                  questions = Question.query.all()
                  current_questions = paginate_questions(request, questions)

                  return jsonify({
                        'success': True,
                        'created': question.id,
                        'current_questions': current_questions,
                        'total_questions': len(questions)
                   })

            except:
                  abort(422)
      '''
      Create a POST endpoint to get questions based on a search term. 
      It should return any questions for whom the search term 
      is a substring of the question. 

      TEST: Search by any phrase. The questions list will update to include 
      only question that include that string within their question. 
      Try using the word "title" to start. 
      '''
      @app.route('/questions/search', methods=['POST'])
      def search_question():

            try:
                  num_total_quesions =  len(Question.query.all())
                  body = request.get_json()
                  search = body.get('searchTerm', None)

                  if not search:
                        abort(422)

                  questions = Question.query.filter(Question.question.ilike('%{}%'.format(search)))
                  current_questions = paginate_questions(request, questions)

                  return jsonify({
                        "success":True,
                        "questions":current_questions,
                        "total_questions":num_total_quesions,
                        "current_category":None
                  })
            except:
                  abort(422)

      '''
       Create a GET endpoint to get questions based on category. 

      TEST: In the "List" tab / main screen, clicking on one of the 
      categories in the left column will cause only questions of that 
      category to be shown. 
      '''
      @app.route('/categories/<int:category_id>/questions' , methods=['GET'])
      def get_question_on_category(category_id):

            
            questions = Question.query.filter(Question.category==category_id)
            current_questions = paginate_questions(request, questions)

            if len(current_questions) == 0:
                  abort(404)

            return jsonify({
                  "success":True,
                  "questions":current_questions,
                  "current_category":category_id,
                  "total_questions":len(current_questions)
            })

      ''' 
      Create a POST endpoint to get questions to play the quiz. 
      This endpoint should take category and previous question parameters 
      and return a random questions within the given category, 
      if provided, and that is not one of the previous questions. 

      TEST: In the "Play" tab, after a user selects "All" or a category,
      one question at a time is displayed, the user is allowed to answer
      and shown whether they were correct or not. 
      '''
                  
      @app.route('/quizzes', methods=['POST'])
      def play():

            try:
                  body = request.get_json()
                  quiz_category = body.get('quiz_category')
                  previous_questions = body.get('previous_questions')

                  if not 'quiz_category' in body or not 'previous_questions' in body:
                        abort(422)

                  quiz_category_id = quiz_category['id']
                  
                  if quiz_category_id == 0:
                        questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
                  else:
                        questions = Question.query.filter(Question.category==quiz_category_id).filter(~Question.id.in_(previous_questions)).all()

                  num_remaining_questions = len(questions)
                  new_question = None

                  if num_remaining_questions > 0:
                        rand_question_id = random.randint(0, num_remaining_questions-1)
                        new_question = questions[rand_question_id]

                  if new_question is not None:
                        new_question = new_question.format()

                  return jsonify({
                        "success":True,
                        "question":new_question
                  })

            except:
                  abort(422)

      @app.errorhandler(404)
      def not_found(error):
            return jsonify({
                  "success": False, 
                   "error": 404,
                   "message": "resource not found"
            }), 404


      @app.errorhandler(422)
      def unprocessable(error):
            return jsonify({
                  "success": False, 
                  "error": 422,
                  "message": "unprocessable"
            }), 422

      @app.errorhandler(400)
      def bad_request(error):
            return jsonify({
                  "success": False, 
                  "error": 400,
                  "message": "bad request"
            }), 400


      return app

    