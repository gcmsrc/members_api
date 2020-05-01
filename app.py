from flask import Flask, g, request, jsonify
from database import get_db
import functools

app = Flask(__name__)
app.config['DEBUG'] = True

api_username = 'admin'
api_password = 'password'

### CLOSE DB ###
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def protected(f):
    @functools.wraps(f)
    def decorated(*arg, **kwargs):
        auth = request.authorization
        if auth:
            if auth.username == api_username and auth.password == api_password:
                return f(*arg, **kwargs)
            else:
                return jsonify({'message' : 'Authentication failed!'}), 403 
    return decorated

### ROUTES ###
@app.route('/member', methods=['GET'])
@protected
def get_members():

    db = get_db()
    members_cur = db.execute('select * from members')
    members = members_cur.fetchall()

    members_list = []
    for m in members:
        m_dict = {}
        m_dict['id'] = m['id']
        m_dict['name'] = m['name']
        m_dict['email'] = m['email']
        m_dict['level'] = m['level']
        members_list.append(m_dict)

    return jsonify({'members' : members_list})

@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):

    db = get_db()
    member_cur = db.execute('select * from members where id = ?', [member_id])
    member = member_cur.fetchone()

    member_dict = {
        'id' : member['id'],
        'name' : member['name'],
        'email' : member['email'],
        'level' : member['level']
    }

    return jsonify({'member' : member_dict})

@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('insert into members (name, email, level) values (?,?,?)', [name, email, level])
    db.commit()

    member_cur = db.execute('select id, name, email, level from members where name = ?', [name])
    new_member = member_cur.fetchone()

    member_dict = {
        'id' : new_member['id'],
        'name' : new_member['name'],
        'email' : new_member['email'],
        'level' : new_member['level']
    }

    return jsonify({'member' : member_dict})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):

    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
    db.commit()

    member_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member = member_cur.fetchone()

    member_dict = {
        'id' : member['id'],
        'name' : member['name'],
        'email' : member['email'],
        'level' : member['level']
    }

    return jsonify({'member' : member_dict})

@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):

    db = get_db()
    db.execute('delete from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message' : 'The member has been deleted'})

if __name__ == '__main__':
    app.run()