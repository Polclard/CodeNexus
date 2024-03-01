# main.py
import json
import sys
import traceback
from datetime import datetime
from io import StringIO, BytesIO

import flask_login
from flask import redirect, render_template, request, Blueprint, flash, url_for, jsonify, Response
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from __init__ import db
from models import Exercise, Attempt, User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, current_user=current_user)


@main.route('/saveChanges', methods=['POST'])
@login_required
def saveChanges():
    new_name = request.form.get('name')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    user = flask_login.current_user
    if not user or not check_password_hash(user.password, old_password):
        flash('Something is incorrect, please try again.')
        return redirect(url_for('main.profile'))

    if new_password != "" and new_password != " ":
        flask_login.current_user.password = generate_password_hash(new_password)
    flask_login.current_user.name = new_name
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route('/exercises', methods=['GET'])
def exercises():
    # DEPRECATED
    if current_user.is_authenticated:
        all_exercises = Exercise.query.all()
        return render_template('exercises.html', all_exercises=all_exercises)
    else:
        return redirect(url_for('main.index'))


@main.route('/exercises_api', methods=['GET'])
def exercises_api():
    if current_user.is_authenticated:
        all_exercises = Exercise.query.all()
        return render_template('exercises_api.html', all_exercises=all_exercises)
    else:
        return redirect(url_for('main.index'))


@main.route('/create_exercise', methods=['GET'])
def create_exercise():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        return render_template('create_exercise.html')
    else:
        return redirect(url_for('main.index'))


@main.route('/create_exercise_post', methods=['POST'])
def create_exercise_post():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        exercise_title = request.form.get('exercise_title')
        exercise_description = request.form.get('exercise_description')
        code = request.form.get('code')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        number_of_attempts = request.form.get('number_of_attempts')
        test_cases = request.form.get('test_cases')
        programming_language = request.form.get('programming_language')
        start_time = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        visible = request.form.get('visible')

        print("a")
        print(exercise_title)
        print(exercise_description)
        print(code)
        print(start_date)
        print(end_date)
        print(number_of_attempts)
        dict_a = {}

        for in_item in [item.split(":") for item in test_cases.split(',\r\n')]:
            dict_a[in_item[0]] = in_item[1]
        print(dict_a)
        print("a")

        new_exercise = Exercise(title=exercise_title,
                                description=exercise_description,
                                start_time=start_time,
                                end_time=end_time,
                                number_of_attempts=int(number_of_attempts),
                                code=code,
                                test_cases=dict_a,
                                date_created=datetime.utcnow(),
                                programming_language=programming_language,
                                visible=True if visible == 'true' else False)

        db.session.add(new_exercise)
        db.session.commit()

        return redirect(url_for('main.exercises_api'))
    else:
        return redirect(url_for('main.index'))


@main.route('/api/exercises', methods=['GET'])
def get_data():
    data = Exercise.query.all()
    json_data = [{"id": item.id,
                  "title": item.title,
                  "description": item.description,
                  "start_time": item.start_time,
                  "end_time": item.end_time,
                  "number_test_cases": item.number_test_cases} for item in data]
    return jsonify(json_data)


@main.route('/edit_exercise/<int:exercise_id>')
def edit_exercise(exercise_id):
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        found_exercise = [item for item in Exercise.query.all() if item.id == exercise_id][0]
        print(found_exercise)
        print(exercise_id)
        return render_template('edit_exercise.html', exercise=found_exercise)
    else:
        return redirect(url_for('main.index'))


@main.route('/edit_exercise_post/<int:exercise_id>', methods=['POST'])
def edit_exercise_post(exercise_id):
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        found_exercise = [item for item in Exercise.query.all() if item.id == exercise_id][0]

        found_exercise.title = request.form.get('exercise_title')
        found_exercise.description = request.form.get('exercise_description')
        found_exercise.code = request.form.get('code')
        found_exercise.start_time = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        found_exercise.end_time = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        found_exercise.number_of_attempts = request.form.get('number_of_attempts')
        found_exercise.test_cases = json.loads(request.form.get('test_cases').replace("'", '"'))
        found_exercise.programming_language = request.form.get('programming_language')

        if request.form.get('visible') == 'true':
            found_exercise.visible = True
            # print('fleze true')
        elif request.form.get('visible') == 'false':
            # print('fleze false')
            found_exercise.visible = False

        db.session.commit()
        return redirect(url_for('main.exercises_api'))
    else:
        return redirect(url_for('main.index'))


@main.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise_post(exercise_id):
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        Exercise.query.filter_by(id=exercise_id).delete()
        db.session.commit()
        return redirect(url_for('main.exercises_api'))
    else:
        return redirect(url_for('main.index'))


@main.route('/exercise_detail_view/<int:exercise_id>', methods=['POST', 'GET'])
def exercise_detail_view(exercise_id):
    if current_user.is_authenticated:
        # id
        # start_date
        # finish_date
        # submitted
        # user_id
        # exercise_id
        # user
        # exercise

        number_of_attempts_per_exercise = Attempt.query.filter_by(id=exercise_id, user_id=current_user.id).count()

        # TODO Make so users cannot go above attempts on certain exercise

        print(f"Visible: {Exercise.query.filter_by(id=exercise_id).first().visible}")
        print(f"number of attempts: {number_of_attempts_per_exercise}")
        print(f"vk number: {Exercise.query.filter_by(id=exercise_id).first().number_of_attempts}")

        if (Exercise.query.filter_by(
                id=exercise_id).first().visible == True and number_of_attempts_per_exercise < Exercise.query.filter_by(
            id=exercise_id).first().number_of_attempts) or current_user.role.name == "ADMIN":
            new_attempt = Attempt(user_id=current_user.id,
                                  exercise_id=exercise_id,
                                  start_date=datetime.utcnow(),
                                  number_of_passed_tests=0)
            current_exercise = Exercise.query.filter_by(id=exercise_id).first()

            db.session.add(new_attempt)
            db.session.commit()
            new_attempt.exercise = Exercise(title=current_exercise.title,
                                            description=current_exercise.description,
                                            start_time=current_exercise.start_time,
                                            end_time=current_exercise.end_time,
                                            number_of_attempts=current_exercise.number_of_attempts,
                                            code=current_exercise.code,
                                            test_cases=current_exercise.test_cases,
                                            date_created=current_exercise.date_created,
                                            programming_language=current_exercise.programming_language,
                                            visible=True if current_exercise.visible == 'true' else False)
            new_attempt.test_cases = ""
            db.session.commit()
            runned_tests = 0
            return (redirect(url_for('main.attempt', attempt=new_attempt, exercise=new_attempt.exercise,
                                     runned_tests=runned_tests, attempt_id=new_attempt.id)))
            # return render_template('detail_exam_view.html', attempt=new_attempt, exercise=new_attempt.exercise,
            #                        runned_tests=runned_tests)
        print("here out 2")
        return (redirect(url_for('main.exercises_api')))
    else:
        return redirect(url_for('main.index'))


@main.route('/attempt/<int:attempt_id>', methods=['GET'])
def attempt(attempt_id):
    if current_user.is_authenticated:
        print(f"Attempt id = {attempt_id}")
        attempt = Attempt.query.filter_by(id=attempt_id).first()
        # print(f"Id: {attempt.id}")
        # print(f"User Id: {attempt.user_id}")
        # print(f"Exercise Id: {attempt.exercise_id}")
        # print(f"Exercise Id Id{attempt.exercise.id}")
        # print(f"Exercise Id title{attempt.exercise.title}")
        # print(f"Exercise Id description{attempt.exercise.description}")
        # print(f"Exercise Id code{attempt.exercise.code}")

        runned_tests = [item for item in attempt.test_cases.split("-_--_")]
        print(f"1. {attempt.number_of_passed_tests}")
        print(f"2. {len(attempt.exercise.test_cases.values())}")
        print("here out")
        return render_template('detail_exam_view.html', attempt=attempt, exercise=attempt.exercise,
                               runned_tests=runned_tests)
    else:
        print("here out")
        return redirect(url_for('main.index'))


@main.route('/test_attempt/<int:attempt_id>', methods=['POST'])
def test_attempt(attempt_id):
    if current_user.is_authenticated:
        attempt_to_submit = Attempt.query.filter_by(id=attempt_id).first()
        if attempt_to_submit.submitted is not True or current_user.role.name == "ADMIN":
            attempt = Attempt.query.filter_by(id=attempt_id).first()
            code_from_user = request.form.get('codeTextArea')
            attempt.exercise.code = code_from_user

            print(f"Attempt Exercise{hex(id(attempt.exercise))}")
            print(f"Give Exercise{hex(id(Exercise.query.filter_by(id=attempt.exercise.id).first()))}")

            runned_tests = list()
            number_of_passed_test_cases = 0

            for key, value in attempt.exercise.test_cases.items():
                try:
                    execCode = compile(f"input_numbers='{key}'\n{attempt.exercise.code}", 'mulstring', 'exec')
                    output_buffer = StringIO()
                    sys.stdout = output_buffer
                    exec(execCode)
                    output = output_buffer.getvalue()
                    output = output.rstrip('\n')
                    sys.stdout = sys.__stdout__
                    runned_tests.append(output)
                except Exception as e:
                    print(f"Error: {e}")
                    print("")
                    runned_tests.append(f"Error: {traceback.format_exc()}")

                print(runned_tests)
                print(list(attempt.exercise.test_cases.values()))

            for i in range(len(attempt.exercise.test_cases)):
                if runned_tests[i] == list(attempt.exercise.test_cases.values())[i]:
                    number_of_passed_test_cases += 1

            attempt.number_of_passed_tests = number_of_passed_test_cases
            attempt.test_cases = '-_--_'.join(runned_tests)
            print(f"Attempt Id: {attempt.id}")
            db.session.commit()

            return render_template('detail_exam_view.html', exercise=attempt.exercise,
                                   runned_tests=[item for item in attempt.test_cases.split("-_--_")],
                                   number_of_passed_test_cases=attempt.number_of_passed_tests, attempt=attempt)
    else:
        return redirect(url_for('main.index'))


@main.route('/submit_attempt/<int:attempt_id>', methods=['POST', 'GET'])
def submit_attempt(attempt_id):
    if current_user.is_authenticated:

        attempt_to_submit = Attempt.query.filter_by(id=attempt_id).first()
        if attempt_to_submit.submitted is not True or current_user.role.name == "ADMIN":
            attempt_to_submit.submitted = True
            attempt_to_submit.finish_date = datetime.utcnow()
            db.session.commit()

        return redirect(url_for('main.my_attempts'))
    else:
        return redirect(url_for('main.index'))


@main.route('/my_attempts', methods=['GET'])
def my_attempts():
    if current_user.is_authenticated:
        attempts_for_current_user = Attempt.query.filter_by(user_id=current_user.id).all()
        return render_template('attempts.html', attempts=attempts_for_current_user)
    else:
        return redirect(url_for('main.index'))


@main.route('/all_attempts', methods=['GET'])
def all_attempts():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        all_attempts_i = Attempt.query.filter(Attempt.user_id != current_user.id).all()
        return render_template('all_attempts.html', attempts=all_attempts_i)
    else:
        return redirect(url_for('main.index'))


@main.route('/attempts_per_exercise', methods=['GET'])
def attempts_per_exercise():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":

        all_attempts_that_someone_attempted = list([attempt1.exercise for attempt1 in [at for at in Attempt.query.all()
                                                                                       if
                                                                                       at.user.role.name != 'ADMIN']])
        all_attempts_that_someone_attempted = list(set(all_attempts_that_someone_attempted))

        new_list_title_attempts = list()
        new_list_exercises = list()
        for exercise in all_attempts_that_someone_attempted:
            if exercise.title not in new_list_title_attempts:
                new_list_title_attempts.append(exercise.title)
                new_list_exercises.append(exercise)

        # attempts_for_current_user = Attempt.query.filter(Attempt.user_id != current_user.id).all()
        # return render_template('all_attempts.html', attempts=attempts_for_current_user)
        return render_template('attempts_per_exercise.html', exercises=new_list_exercises)
    else:
        return redirect(url_for('main.index'))


@main.route('/attempts_per_exercise_list', methods=['POST'])
def attempts_per_exercise_list():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":

        ex_id = request.form.get('ex_id')
        exercise_title = Exercise.query.filter_by(id=ex_id).first().title

        list_attempts = Attempt.query.all()

        list_attempts_with_certain_title = [item for item in list_attempts if
                                            item.exercise.title == exercise_title and item.user.role.name != 'ADMIN']
        attempts_id_list = [item.id for item in list_attempts_with_certain_title]
        return render_template('attempts_per_exercise_list.html', attempts=list_attempts_with_certain_title, attempts_id_list=attempts_id_list)
    else:
        return redirect(url_for('main.index'))


@main.route('/grade_attempt/<int:attempt_id>', methods=['POST'])
def grade_attempt(attempt_id):
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        attempt_to_submit = Attempt.query.filter_by(id=attempt_id).first()
        attempt_to_submit.grade = int(request.form.get('grade_n'))
        db.session.commit()
        return redirect(url_for('main.all_attempts'))
    else:
        return redirect(url_for('main.index'))

@main.route('/export_attempts_to_csv', methods=['POST'])
def export_attempts_to_csv():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        number_of_attempts = int(request.form.get('number_of_attempts'))
        attempts_list = (request.form.get('attempts_list'))

        attempts_list_ids = list(attempts_list.replace("[", "").replace("]", "").split(", "))
        attempts_list_objects = [Attempt.query.filter_by(id=item).first() for item in attempts_list_ids]
        print(attempts_list_objects)

        import csv
        from datetime import datetime

        data = []
        for obj in attempts_list_objects:
            data.append({
                'id': obj.id,
                'user': obj.user.name,
                'exercise': obj.exercise.title,
                'grade': obj.grade,
            })

        # Prepare CSV data
        csv_data = StringIO()
        csv_writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(data)

        csv_data_encoded = csv_data.getvalue().encode('utf-8')

        # Return CSV file as response with appropriate headers
        response = Response(
            csv_data.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment;filename=data.csv'}
        )

        return response
    else:
        return redirect(url_for('main.index'))

