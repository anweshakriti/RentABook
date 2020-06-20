from flask import Flask, request, jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

#Init app
app= Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

#database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#init db
db=SQLAlchemy(app)

#init ma
ma=Marshmallow(app)

#=================================================CARD HOLDER MODEL-----------------------------------------------------#
#cardHolder
class cardHolder(db.Model):
    __tablename__ = "cardHolder"
    id = db.Column(db.Integer, primary_key=True)
    lastName = db.Column(db.String(100))
    firstName = db.Column(db.String(100))
    cardNumber=db.Column(db.String(100),unique=True)
    
    def __init__(self,lastName,firstName,cardNumber):
        self.firstName=firstName
        self.lastName=lastName
        self.cardNumber=cardNumber
    
#cardHolderSchema
class cardHolderSchema(ma.Schema):
    class Meta:
        fields=('id','firstName','lastName','cardNumber')

#create CardHolder
@app.route('/cardHolder', methods=['POST'])
def add_card():
    firstName=request.json['firstName']
    lastName=request.json['lastName']
    cardNumber=request.json['cardNumber']
    new_cardHolder=cardHolder(firstName,lastName,cardNumber)
    db.session.add(new_cardHolder)
    db.session.commit()

    return cardHolder_schema.jsonify(new_cardHolder)

#init Scheme
cardHolder_schema = cardHolderSchema()
cardHolders_schema = cardHolderSchema(many=True)
#================================================ End of CARD HOLDER MODEL=================================================#


#================================================ BOOK MODEL=================================================#
#Book
class Book(db.Model):
    __tablename__ = "book"
    id=db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(100), unique=True)
    author=db.Column(db.String(100))
    isbn= db.Column(db.String(10))

    def __init__(self,title,author,isbn):
        self.title=title
        self.author=author
        self.isbn=isbn

#BookSchema
class BookSchema(ma.Schema):
    class Meta:
        fields=('id','title','author','isbn')

#create book
@app.route('/book', methods=['POST'])
def add_book():
    title=request.json['title']
    author=request.json['author']
    isbn=request.json['isbn']

    new_book=Book(title,author,isbn)
    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)

#init Scheme
book_schema = BookSchema()
books_schema = BookSchema(many=True)

#get all books
@app.route('/book',methods=['GET'])
def get_books():
    all_books=Book.query.all()
    result=books_schema.dump(all_books)
    return jsonify(result)

#get single books
@app.route('/book/<id>',methods=['GET'])
def get_book(id):
    book=Book.query.get(id)
    return book_schema.jsonify(book)

#update Book
@app.route('/book/<id>', methods=['PUT'])
def update_book(id):
    book=Book.query.get(id)
    title=request.json['title']
    author=request.json['author']
    isbn=request.json['isbn']

    book.title=title
    book.author=author
    book.isbn=isbn

    db.session.commit()

    return book_schema.jsonify(book)

#================================================ End of BOOK MODEL=================================================#

#================================================ RENTAL MODEL=================================================#

#Rental Table
class Rentals(db.Model):
    __tablename__="rentals"
    book_id=db.Column(db.Integer, db.ForeignKey('book.id'),nullable=False)
    cardHolder_id=db.Column(db.Integer, db.ForeignKey('cardHolder.id'))
    id=db.Column(db.Integer, nullable=False,primary_key=True)

    def __init__(self,book_id,cardHolder_id):
        self.book_id=book_id
        self.cardHolder_id=cardHolder_id

#Rental SChema
class RentalSchema(ma.Schema):
    class Meta:
        fields=('id','book_id','cardHolder_id')
        include_fk = True

#Rent a book
@app.route('/rental', methods=['POST'])
def rentBook():
    book_id=request.json['book_id']
    cardHolder_id=request.json['cardHolder_id']
    if Book.query.get(book_id) is not None and cardHolder.query.get(cardHolder_id) is not None:
        new_rent=Rentals(book_id,cardHolder_id)
        db.session.add(new_rent)
        db.session.commit()
        return rent_schema.jsonify(new_rent)
    else:
        return Response("Invalid Input", status=403, mimetype='application/json')

#init Scheme
rent_schema = RentalSchema()
rents_schema = RentalSchema(many=True)

#All the Rented book
@app.route('/rentedBooks', methods=['GET'])
def rentedBooks():
    #rentedBook=session.query(Book,Rentals).filter(Book.id==Rentals.book_id).all()
    rentedBook=Book.query.filter_by(id=Rentals.book_id).all()
    result=books_schema.dump(rentedBook)
    return jsonify(result)


#Run Server
if __name__=='__main__':
    app.run(debug=True)