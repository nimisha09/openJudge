import bottle
from openjudge import tools, config, judge
from multiprocessing import Queue

app = bottle.Bottle()
job_queue = Queue()


@app.get('/')
def home():
    return tools.render('home.html')


@app.get('/question/<pk>')
def question_display(pk):
    contest = tools.read_contest_json()
    pk = str(pk)
    q = {'statement': 'This question does not exist'}
    if pk.isdigit():
        if pk in contest['questions'].keys():
            q = contest['questions'][pk]
    return tools.render('question.html', {'statement': q['statement']})


@app.post('/attempt')
def question_attempt():
    question_pk = bottle.json['question']
    language = bottle.json['language']
    code = bottle.json['code']
    message = 'Something Unexpected happened'
    contest = tools.read_contest_json()
    all_ok = True
    if question_pk in contest['questions'].keys():
        inp, out = [], []
        for key, val in contest['questions'][question_pk]['testcases'].items():
            inp.append(val['in'])
            out.append(val['out'])
    else:
        message, all_ok = 'This question does not exist', False
    if language in contest['wrappers'].keys():
        wrap = contest['wrappers'][language]
    else:
        message, all_ok = 'This Language is not available', False
    if all_ok:
        attid = tools.random_id()
        tools.check_results_by_running_code(code, inp, out, wrap, job_queue, attid)
    else:
        attid = None
    return {'attempt': attid, 'message': message}


@app.post('/attempt/status')
def attempt_status():
    att_id = bottle.json['attempt']
    status, message = judge.get_attempt_status(att_id, job_queue)
    return {'status': status, 'message': message}


@app.get('/static/<path:path>')
def static_server(path):
    root = config.static_root
    return bottle.static_file(path, root=root)