from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template,
    jsonify,
    session)




def home():   
    return render_template('page/home.html')

    return(page)

def construct_page_blueprint(app):

    myblueprint = Blueprint('myblueprint', __name__)
    page = Blueprint('page', __name__, template_folder='templates')
    a1 = app.auth.login_required( home )
    app.add_url_rule('/',"home",a1) 
    return page
    
 




   


