from datetime import datetime

from flask import Flask, request, render_template, redirect, url_for
from flask.ext.mongokit import MongoKit, Document

app = Flask(__name__)

class Task(Document):
    __collection__ = 'tasks'
    structure = {
        'title': unicode,
        'text': unicode,
        'creation': datetime,
    }
    required_fields = ['title', 'creation']
    default_values = {'creation': datetime.utcnow()}
    use_dot_notation = True 
    
db = MongoKit(app)
db.register([Task])

@app.route('/')
def show_all():
    tasks = db.Task.find()
    return render_template('list.html', tasks=tasks)

@app.route('/<ObjectId:task_id>')
def show_task(task_id):
    task = db.Task.get_from_id(task_id)
    return render_template('task.html', task=task)

@app.route('/new', methods=["GET", "POST"])
def new_task():
    if request.method == 'POST':
        task = db.Task()
        task.title = request.form['title']
        task.text = request.form['text']
        task.save()
        return redirect(url_for('show_all'))
    return render_template('new.html')

if __name__ == '__main__':
    app.run(debug=True)