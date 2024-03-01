from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# init SQLAlchemy so we can use it later in our app_models
db = None


def create_app():
    global db
    db = SQLAlchemy()
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        # db.drop_all()
        db.create_all()
        db.session.commit()

#     # region intialize one Admin
#     from models import UserRole
#     new_admin = User(email="Admin@Admin", name="Admin", password=generate_password_hash("Admin"), role=UserRole.ADMIN)
#     new_user_1 = User(email="John@Doe", name="John Doe", password=generate_password_hash("John12345"), role=UserRole.USER)
#     new_user_2 = User(email="Jane@Smith", name="Jane Smith", password=generate_password_hash("Jane12345"), role=UserRole.USER)
#
#     # add the new user to the database
#     with app.app_context():
#         db.session.add(new_admin)
#         db.session.add(new_user_1)
#         db.session.add(new_user_2)
#         db.session.commit()
#     # endregion
#
#     # region Data Initializer
#     from models import Exercise
#     from datetime import datetime, timedelta
#     new_exercise_1 = Exercise(title="Вежба 1: Пресметување на плоштината на круг",
#                                 description="Дополни ја функцијата area(), каде што ќе ја пресметаш и вратиш површината на одреден круг со даден радиус r заокружено на 2 децимали. PI = 3.14 (Не менувај ништо друго)",
#                                 start_time= datetime.now().date() - timedelta(days=1),
#                                 end_time=datetime.now().date() + timedelta(days=20),
#                                 code=
#                                 """
# def area(r):
#     return "{:0.2f}".format(r * r * 3.14)
#
# print(area(int(input_numbers)))""",
#                                 number_of_attempts = 10,
#                                 test_cases={"2": "12.56", "5": "78.50", "7": "153.86"},
#                                 date_created = datetime.utcnow(),
#                                 programming_language = "python",
#                                 visible = True)
#
#     new_exercise = Exercise(title="Вежба 2: Собирање на два броја",
#                                 description="Дополни ја функцијата add(), каде шт треба да се пресмета и врати збирот на дадените броеви како аргумент. (Не менувај ништо друго)",
#                                 start_time= datetime.now().date() - timedelta(days=1),
#                                 end_time=datetime.now().date() + timedelta(days=20),
#                                 code=
#                                 """
# def add(a, b):
#     pass
#
# print(add(int(input_numbers.split(" ")[0]), int(input_numbers.split(" ")[1])))
#                                 """,
#                                 number_of_attempts = 20,
#                                 test_cases={"1 3": "4", "15 4": "19", "25 9": "34", "1 7": "8"},
#                                 date_created = datetime.utcnow(),
#                                 programming_language = "python",
#                                 visible = True)
#
#     with app.app_context():
#         db.session.add(new_exercise)
#         db.session.add(new_exercise_1)
#         db.session.commit()
#     # endregion


    return app