from appdb import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username=db.Column(db.String(50), unique = True)
    password = db.Column(db.String(50), nullable = True)
    token=db.Column(db.String(50), nullable = True)
    cookie=db.Column(db.String(50),nullable=True)
    
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
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    imagesent = db.Column(db.String(50))

    def __repr__(self):
        return '<Image %r sent by %r>' % (self.imagesent, self.username)


class WhisperLog(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    wid = db.Column(db.String(50))

#snapqueue
class Snap(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sentfrom = db.Column(db.String(50),index=True)
    sentto = db.Column(db.String(50),index=True)
    file = db.Column(db.String(50))
    timesent = db.Column(db.Integer,index=True)

#snaps for snapfeed
class FSnap(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sentfrom = db.Column(db.String(50),index=True)
    sentto = db.Column(db.String(50),index=True)
    file = db.Column(db.String(50))
    timesent = db.Column(db.String(50),index=True)