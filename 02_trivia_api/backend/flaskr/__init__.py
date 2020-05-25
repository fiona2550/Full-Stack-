import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

'''
@Todo2
'''


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions 
    

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    '''
    ---1---
    @TODO: Set up CORS. Allow '*' for origins. 
    Delete the sample route after completing the TODOs
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 
            'Content-Type,Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods', 
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    ----2----
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        if (len(categories_dict) == 0):
            abort(404)
    
        return jsonify({
            'success': True,
            'categories': categories_dict
        })
        
    '''
    ----3----
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom 
    of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    
    @app.route('/questions')    
    def get_questions():
        '''
        Handles GET requests for getting all questions.
        '''
        
        questions = Question.query.all()
        questions_len = len(questions)
        current_questions = paginate_questions(request, questions)
        
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        if (len(current_questions) == 0):
            abort(404)
        
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': questions_len,
            'categories': categories_dict
        })
            
    '''
    ----4----
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    
    TEST: When you click the trash icon next to a question, 
    the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    
    @app.route("/questions/<int:question_id>", methods=['DELETE'])    
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question:
                question.delete()
            else:
                absort(404)
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)
    
    '''
    ----5----
    TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear 
    at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()        
        keys = ['question', 'answer', 'difficulty', 'category']
        if all([key in body.keys() for key in keys]):
                    
            new_question = body['question']
            new_answer = body['answer']
            new_category = body['category']
            new_difficulty = body['difficulty']
    
            try:
                question = Question(
                                    question=new_question, 
                                    answer=new_answer,
                                    difficulty=new_difficulty, 
                                    category=new_category
                                    )
                question.insert()
        
                return jsonify({
                    'success': True,
                    'created': question.id,
                })
    
            except:
                abort(422)
        else:
            abort(422)    

    '''
    ----6----
    Create a POST endpoint to get questions based on category.
    '''
    @app.route('/questions/<int:id>/categorysearch' )
    def get_questions_by_category(id):
        '''
        Handles GET requests for getting questions based on category.
        '''
        
        # get the category by id
        category = Category.query.filter(Category.id == id).all()
        # return str(category[0].id)            
        # get the data if it matches
        if category:
        
            selection = Question.query.filter(Question.category == id).all()    
            paginated = paginate_questions(request, selection)
            # return str(paginated[0])
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all()),
                'current_category': category[0].type
            })
        # abort 400 for bad request if category isn't found
        else:
            absort(400)
            
    '''
    @TODO:
    
    ----7----    
    Create a GET endpoint to get questions based on category. 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    
    
    
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
      #  return str(len(body))
        search_term = request.form.get('searchTerm', '')
      #  return (search_term)
        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)
    '''   

    @app.route('/questions/search', methods = ['POST'])
    def search_questions():
        body = request.get_json()
      # return str(len(body))
        term = body.get('searchTerm', None)

        if term:
            search = "%{}%".format(term)            
            search_results = Question.query.filter(
                    Question.question.like(search)).all()
            #paginated = paginate_questions(request, selection)
            # return search_results.questions
            return jsonify({
                'success': True,
                'questions': 
                    [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
        else:
            abort(404)


    '''
    ----8----
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
  
    @app.route('/quizzes', methods=['POST'])
    def play_the_quiz():
	    
        quizzedata = request.get_json()
        if not ('quiz_category' in quizzedata and 'previous_questions' in quizzedata):
            abort(400)
			
        previous_questions = quizzedata['previous_questions']
        quiz_category = quizzedata['quiz_category']
    
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)               
                
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
                    
        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()
            random_question = random.choice(questions).format()
                    
            return jsonify({
                        'success': True,
                        'question': random_question})
  
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

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
        
    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500
    
    return app    