import sqlite3
import pymorphy2
import re
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

morph = pymorphy2.MorphAnalyzer()


def get_db_connection():
    conn = sqlite3.connect('dt_base.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(recipe_id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?',
                        (recipe_id,)).fetchone()
    conn.close()
    if recipe is None:
        abort(404)
    return recipe


webapp = Flask(__name__)
webapp.config['SECRET_KEY'] = 'lost'


@webapp.route('/')
def start():
    return render_template('start.html')


@webapp.route('/what_do_you_want')
def what_do_you_want():
    return render_template('what_do_you_want.html')


@webapp.route('/ingredients')
def ingredients():
    return render_template('ingredients.html')


@webapp.route('/ingredients_you_do_not_want')
def ingredients_you_do_not_want():
    return render_template('ingredients_you_do_not_want.html')


@webapp.route('/cooking_method')
def cooking_method():
    return render_template('cooking_method.html')


@webapp.route('/action_page.php')
def action_page():
    return render_template('action_page.php')


@webapp.route('/main', methods=('GET', 'POST'))
def choice():
    #if request.method == 'POST':
        #title3 = request.form['title3']

        #conn = get_db_connection()
        #conn.execute('SELECT title2, recipe FROM recipes WHERE title2 = ?', (title3,))
        #conn.close()
    return render_template('main.html')


@webapp.route('/add', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title2 = request.form['title2']
        recipe = request.form['recipe']

        if not title2 or not recipe:
            flash('All fields are required!')
        else:
            words = re.sub(r'[^\w\s]', '', recipe).split()
            res = {}
            lemma = []
            for word in words:
                p = morph.parse(word)[0]
                res[p.normal_form] = p.tag
            for i in res:
                if 'NOUN' in res[i]:
                    lemma.append(i)
                if 'ADJF' in res[i]:
                    lemma.append(i)
                if 'INFN' in res[i]:
                    lemma.append(i)
                if 'PRTF' in res[i]:
                    lemma.append(i)
                if 'VERB' in res[i]:
                    lemma.append(i)
            lemma = str(lemma)
            conn = get_db_connection()
            conn.execute('INSERT INTO recipes (title2, recipe, lemma) VALUES ( ?, ?, ?)',
                         (title2, recipe, lemma))
            conn.commit()
            conn.close()
            return redirect(url_for('recipe'))
    return render_template('add.html')


@webapp.route('/all_of_rec')  # вставить название страницы, на которой будут все рецепты показаны
def recipe():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('all_of_rec.html', recipes=recipes)


@webapp.route('/all_of_rec/<int:recipe_id>')
def recipe2(recipe_id):
    recipe = get_post(recipe_id)
    return render_template('exact.html', recipe=recipe)


if __name__ == '__main__':
    webapp.run(debug=True)
