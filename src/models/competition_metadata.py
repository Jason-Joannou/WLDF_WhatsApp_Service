from app import db

class DanceStyle(db.Model):
    __tablename__ = 'dance_styles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    
class DanceGroup(db.Model):
    __tablename__ = 'dance_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    group_type = db.Column(db.String, nullable=False)  # Solo, Duet, Trio, etc.
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)