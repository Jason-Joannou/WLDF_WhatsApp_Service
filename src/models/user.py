from extentions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.role}', '{self.number}')"
