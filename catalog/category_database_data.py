#category_database_data.py
#This file is responsible for preloading the category database with information

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Category, Item
engine = create_engine('sqlite:///category.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

user1 = User(name = "Ariana Lopez")
session.add(user1)

user2 = User(name = "Alaina Lopez")
session.add(user2)

user3 = User(name = "Mike  Wayne")
session.add(user3)

user4 = User(name = "Thomas Nyguen")
session.add(user4)

category1 = Category(name = "Football")
session.add(category1)

category2 = Category(name = "Softball")
session.add(category2)

category3 = Category(name = "Volleyball")
session.add(category3)


class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False)
	description = Column(Text)
	user_id = Column(Integer, ForeignKey('user.id'))
	category_id = Column(Integer, ForeignKey('category.id'))
	user = relationship(User)
	category = relationship(Category)

item1 = Item(name = "Bats", description="For softball, the best bat to use is a Louisville slugger.", user_id = 1, category_id = 2)
session.add(item1)

item2 = Item(name = "Knee Pads", description="Knee pads are really important.", user_id = 4, category_id = 3)
session.add(item2)

session.commit()