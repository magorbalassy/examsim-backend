'''from google.appengine.ext import ndb

class Question(ndb.Model):
    q_text = ndb.StringProperty()
    q_type = ndb.IntegerProperty()
    explanation = ndb.StringProperty()
    answers = ndb.StringProperty(repeated=True)
    correct = ndb.StringProperty()
    exam_nr = ndb.IntegerProperty()
'''

class Question:
	correct_ans = ''
	exam_nr = 0
	explanation = ''
	q_text = ''
	q_type = ''
	answers = []
