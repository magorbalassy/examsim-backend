import logging, re
from models import Question
from flask import Flask
from flask import jsonify

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def hello():
    return 'Welcome to SimExam.'

def custom_response(data):
  res = jsonify(data)
  res.headers.add('Access-Control-Allow-Origin', '*')
  return res

def sanitize_file(file_name):
  ''' Removes empty lines and whitespaces and returns a string with the whole
  content of the file.'''
  space_beg_reg = re.compile(r'^(\s*)')
  whitespace_reg = re.compile(r'^\s*$')

  file_content = ''
  try:
    file_handler = open(file_name)
  except IOError:
    return 'Cannot open file.'
  for line in file_handler:
    line = space_beg_reg.sub('', line)
    if whitespace_reg.match(line):
      continue
    else:
      file_content = file_content + line
  return file_content


@app.route('/sendq/')
def sendq():
  questions = []
  input_file = 'progtec2.txt'

  content = sanitize_file(input_file)

  logging.basicConfig(filename='example.log', level=logging.DEBUG)
  logging.debug('content:', content)

  question_section_reg = re.compile(
      r'^(QUESTION [0-9]{,3})(.*?)(?=QUESTION|\Z)', re.DOTALL | re.MULTILINE)
  answer_section_reg = re.compile(
    r'^^([A-Za-z]{1}[)\.]{1})(.*?)(?=^[A-Za-z]{1}[)\.]{1}|Correct|\Z)', re.DOTALL | re.MULTILINE )

  exam_section_reg = re.compile(
      r'^(\s*Exam [A-Z]$)(.*?)(?=E[Xx][Aa][Mm] [A-Z]|\Z)', re.DOTALL | re.MULTILINE)
  section_reg = re.compile(r'\s*Section:.*')
  correct_ans_reg = re.compile(r'^Correct [Aa]nswer: |^Answer:')
  answer_options_reg = re.compile(r'^([A-Za-z]{1}[\.\)]{1})')  

  exam_nr = 1
  question = False
  q_id=0
  correct_ans=[]
  for question_nr in question_section_reg.finditer(content):
    q_id += 1
    q_text = ''
    q_type = ''
    answer_options = []
    section = False
    answers = []
    explanation = ''
    for line_nr, line in enumerate(question_nr.group(2).split('\n')):
      logging.debug('Line {} : {}'.format(line_nr, line))
      answers_nr = 0
      if section_reg.match(line):
        answer_options = False
        section = True
      if correct_ans_reg.match(line):
        question = False
        correct_ans = str(line.split(':')[1]).strip()
        q_type = 'multiple-choice' if answer_options else 'fill-in-the-blank'
        if answer_options and len(correct_ans) == 1:
          q_type = 'single-choice'
        continue
      if answer_options_reg.match(line) or answer_options:
        question = False
        answer_options = True
        if not answer_options_reg.match(line):
          answers[answers_nr] = answers[answers_nr] + line
        else:
          answers.append(line)
          answers_nr += 1
        continue
      if line_nr == 1 or question:
        question = True
        q_text = q_text + str(line) + '\n'
      if section or section_reg.match(line):
        # Skip useless lines.
        if section_none_reg.match(line):
          continue
        if explanation_reg.match(line):
          continue
        if whitespace_reg.match(line):
          continue
        explanation += line + '\n'
    q = Question()
    #q.answers = list_to_json(answers)
    q.q_text = q_text
    q.q_type = q_type
    q.explanation = explanation
    q.correct_ans = correct_ans
    q.exam_nr = exam_nr
    try:
      pass  # questions.append(json.dumps(q))
    except:
      logging.debug(q.answers, q.q_text, q.q_type,
                    q.explanation, q.correct_ans, q.exam_nr)
    #answers_json = list_to_json(answers)
    if q_type == 'fill-in-the-blank':
      answers = [correct_ans, ]
    questions.append({
        'exam_nr': exam_nr,
        'q_text': q_text,
        'q_type': q_type,
        'answers': answers,
        'correct_ans': correct_ans,
        'explanation': explanation})
    # exam_file['questions'] = q_id
  # logging.debug('Exam section : {}'.format(exam_content.group(2)))
  # return "This is the response."
  #return jsonify({'a':'5'})
  # logging.debug(jsonify(questions))
  return custom_response({"questions":questions})

'''@app.route('/analyzer/')
def analyzer():

    question_reg = re.compile('^QUESTION [0-9]{1,2}|^Q[0-9]{1,2}')
    exam_reg = re.compile('\s*E[Xx][Aa][Mm] [A-Z]{1}$')
    correct_ans_reg = re.compile('^Correct Answer: |^Answer:')
    number_reg = re.compile('([0-9]){1,3}')
    answer_options_reg = re.compile('^([A-Z]\.){1}')
    exam_code_reg = re.compile('Number: [a-zA-Z0-9\-]*')
    score_reg = re.compile('Passing Score: [0-9]{3}')
    time_reg = re.compile('Time Limit: [0-9]{1,2,3}')
    version_reg = re.compile('File Version: .*')
    section_reg = re.compile('\s*Section:.*')
    section_none_reg = re.compile('.*[Nn]one.*')
    explanation_reg = re.compile('\s*Explanation')
    question_section_reg = re.compile(
        '^(QUESTION [0-9]{,2})(\s.*?)(?=QUESTION|\Z)', re.DOTALL | re.MULTILINE)
    exam_section_reg = re.compile(
        '^(\s*Exam [A-Z]$)(.*?)(?=E[Xx][Aa][Mm] [A-Z]|\Z)', re.DOTALL | re.MULTILINE)
    # sanitize file regexes
    whitespace_reg = re.compile('^\s*$')
    gratisexam_reg = re.compile('.*gratisexam.com.*')
    space_beg_reg = re.compile('^(\s*)')

    def sanitize_file(file_name):
        file_content = ''
        try:
            file_handler = open(file_name)
        except IOError:
            return 'Cannot open file.'
        for line in file_handler:
            line = space_beg_reg.sub('', line)
            if whitespace_reg.match(line) or gratisexam_reg.match(line):
                continue
            else:
                file_content = file_content + line
        return file_content

    # As the name says - convert lists to json.
    def list_to_json(input_list):
        return_json = {}
        for i, j in enumerate(input_list):
            return_json['{}'.format(i+1)] = j
        return return_json

    # Will check the file type / structure, to see if it is processable or not.
    def testfile(file_name):
        pass

    f = 'test'
    content = sanitize_file(f)

    # object to store the content of the exam file, should have the following
    # fields :
    # exam_file_title = ""
    # exam_code = ""
    # exam_id = ""
    # exam_descr = ""
    exam_file = {}

    line_nr = 0
    q_id = 0
    description = False
    exam_file_descr = ''

    # This for loop will obtain the 3 values needed for the Exam_files table,
    # into exam_file, properties exam_id (if it already exists), exam_file_id,
    # exam_file_descr
    for line in content.split('\n'):
        line_nr += 1
        if question_reg.match(line) or exam_reg.match(line):
            break
        if line_nr == 1:
            exam_file['exam_file_title'] = line
            continue
        if exam_code_reg.match(line):
            exam_file['exam_code'] = str(line.split(':')[1]).strip()
            continue
        if version_reg.match(line) or description:
            description = True
            exam_file_descr = exam_file_descr + line + "\n"
    exam_file['exam_file_descr'] = exam_file_descr

    # exam_sections iterable which contains the blocks of exams (A,B,C...),
    # this might be a single block
    for exam_nr, exam_content in enumerate(exam_section_reg.finditer(content)):
        question = False
        for question_nr in question_section_reg.finditer(exam_content.group(2)):
            q_id += 1
            q_text = ''
            q_type = ''
            answer_options = False
            section = False
            answers = []
            explanation = ''
            for line_nr, line in enumerate(question_nr.group(2).split('\n')):
                answers_nr = 0
                if section_reg.match(line):
                    answer_options = False
                    section = True
                if correct_ans_reg.match(line):
                    question = False
                    correct_ans = str(line.split(':')[1]).strip()
                    q_type = 'multiple-choice' if answer_options else 'fill-in-the-blank'
                    continue
                if answer_options_reg.match(line) or answer_options:
                    question = False
                    answer_options = True
                    if not answer_options_reg.match(line):
                        answers[answers_nr] = answers[answers_nr] +  line
                    else:
                        answers.append(line)
                        answers_nr += 1
                    continue
                if line_nr == 1 or question:
                    question = True
                    q_text = q_text + str(line) + '\n'
                if section or section_reg.match(line):
                    if section_none_reg.match(line):
                        continue
                    if explanation_reg.match(line):
                        continue
                    if whitespace_reg.match(line):
                        continue
                    explanation += line + '\n'
            answers_json = list_to_json(answers)
            exam_file['{}'.format(q_id)] = {
                'exam_nr' : exam_nr,
                'q_text'  : q_text,
                'q_type'  : q_type,
                'answers' : answers_json,
                'correct_ans' : correct_ans,
                'explanation' : explanation}
    return jsonify(exam_file)'''


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
