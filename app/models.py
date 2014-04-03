class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username=db.Column(db.String(50), unique = True)
    token=db.Column(db.String(50),unique = True)
    
    def __repr__(self):
        return '<User %r>' % (self.username)

class GroupMember(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(50))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
   
    def __repr__(self):
        return '<GroupMember %r in Group %d>' % (self.username, self.group_id)


class Group(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dummy_user = db.Column(db.String(50), index=True)
    dummy_password = db.Column(db.String(50))
    dummy_token = db.Column(db.String(50))
    members = db.relationship('GroupMember', backref='group',lazy='dynamic')

    def __repr__(self):
        return '<Group %d, owned by %r>' % (self.group_id, self.owner.username)

class SecretSanta(db.Model):
    id = db.Column(db.Integer.primary_key=True)
    username = db.Column(db.String(50))
