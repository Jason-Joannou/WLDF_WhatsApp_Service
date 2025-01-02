from app import db
class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('dance_groups.id'), nullable=False)  # Foreign key to dance groups
    
    user = db.relationship('User', backref='registrations')
    competition = db.relationship('Competition', backref='registrations')
    group = db.relationship('DanceGroup', backref='registrations')