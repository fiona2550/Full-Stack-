import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:Password".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    ---2----
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def get_paginated_questions_test(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']),10)
        
    def get_paginated_questions_test_404(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    '''
    ---3----
    ''' 
    
    def get_all_categories_test(self):
        """Test for get_all_categories
        Tests for the status code, if success is true,
        if categories is returned and the length of
        the returned categories
        """
        response = self.client().get('/categories')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6 ) 
        
    def get_all_categories_test_404(self):
        """Test for get_all_categories
        Failure Example
        """
        response = self.client().get('/categories/99')
        data = json.loads(response.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    '''
    ---4----
    ''' 
    	
    def delete_question_test(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id
        
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        
        question = Question.query.filter(
            Question.id == question.id).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)    

    def delete_question_test_422(self):
        res = self.client().delete('/questions/a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
   
    '''
    ---5----
    ''' 
    	
    def test_post_question(self):
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    def test_post_question_422(self):
        question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")        
    
    '''
    ---6----
    ''' 
    
    def test_get_questions_category(self):
        res = self.client().get('/questions/1/categorysearch')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        
        
    def test_get_questions_category_404(self):
        res = self.client().get('/questions/no/categorysearch')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    '''
    ---7----
    '''
    
    def test_search_questions(self):
      # new_search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', 
                                    json={'searchTerm': 'egyptians'})
      # return res
        data = json.loads(res.data)
      # return(data['success'])

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_search_question_404(self):
        res = self.client().post('/questions/termsearch', 
                                    json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    '''
    ---8----
    '''       
       
    def test_play_quiz(self):
     #   new_quiz_round = {'previous_questions': [1],
     #                   'quiz_category': {'type': 'Entertainment', 'id': 5}}
        
        res = self.client().post('/quizzes', json=
                                    {'previous_questions': [1],
                                    'quiz_category': {'type': 'Entertainment', 'id': 5}
                                    })
        data = json.loads(res.data)
      # return res
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
  
    def test_play_quiz_400(self):
     #   new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', 
                            json={'previous_questions': '' ,'previous_questions': ''})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")
  
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()