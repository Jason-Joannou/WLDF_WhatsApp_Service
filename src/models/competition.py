from app import db
from sqlalchemy.orm import relationship



class Competition(db.Model):
    __tablename__ = 'competitions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)  # Maximum number of participants
    
    # Relationship with Dance Styles
    dance_styles = relationship('DanceStyle', backref='competition', lazy=True)
    
    # Relationship with Dance Groups
    dance_groups = relationship('DanceGroup', backref='competition', lazy=True)
    
    # Relationship with registrations (users joining competitions)
    registrations = relationship('Registration', backref='competition', lazy=True)