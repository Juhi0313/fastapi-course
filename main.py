from fastapi import FastAPI, HTTPException
from typing import Optional
from enum import IntEnum
from pydantic import BaseModel, Field
#basemodel is used when we want to define model or schema for our data. it allows us to define the structure of our data and also validate it. we can use it to define the structure of our request body or response body. we can also use it to define the structure of our query parameters or path parameters. it is a very powerful tool that allows us to ensure that the data we receive is in the correct format and also allows us to provide default values for our data.

#field is a chill tool that provides description, example, and other metadata for our data. it is used in conjunction with basemodel to provide additional information about our data. it is a very useful tool that allows us to provide more context about our data and also allows us to generate better documentation for our api.
import os
import sys
print("Imported main from:", __file__, "cwd:", os.getcwd(), "sys.path[0]:", sys.path[0])


app = FastAPI()
class Priority(IntEnum):
  LOW = 3
  MEDIUM = 2
  HIGH = 1


class Todobase(BaseModel):
  todo_name: str = Field(..., min_length=3, max_length=512, description='Name of the todo')
  todo_description: str = Field(..., description='Description of the todo')
  priority: Priority = Field(default=Priority.LOW, description='Priority of the todo')
  #we didnt use id becuase this is parent class which will be inherited by other classes and the id will be generated automatically when we create a new todo. so we dont need to include it in the base class. also we can use the priority field to set the priority of the todo, it is an enum which has three values LOW, MEDIUM and HIGH. we can set the default value to LOW and also provide a description for it. this way we can ensure that the data we receive is in the correct format and also provides more context about our data.

class TodoCreate(Todobase):
  pass

class Todo(Todobase):
  id: int = Field(..., description='ID of the todo')
  model_config = {"frozen": False}
  #we can use this class to define the structure of our response body when we create a new todo or when we get a todo by id. it includes all the fields from the base class and also includes the id field which is generated automatically when we create a new todo.

  #usecase of this is as response not request body because when we create a new todo we dont need to provide the id in the request body, it will be generated automatically and returned in the response body. so we can use this class to define the structure of our response body when we create a new todo or when we get a todo by id.

class TodoUpdate(BaseModel):
  #it is like TodoBase but it is optional
  #it is optional to provide name, description and prioroity in update
  todo_name: Optional[str] = Field(None, min_length=3, max_length=512, description='Name of the todo')
  todo_description: Optional[str] = Field(None, description='Description of the todo')
  priority: Optional[Priority] = Field(None, description='Priority of the todo')

#all_todos = [{'id': 1, 'Name': 'Sports', 'Description': 'Play basketball'},
             #{'id': 2, 'Name': 'Read', 'Description': 'Read now'},
             #{'id': 3, 'Name': 'Study', 'Description': 'Go study'},
             #{'id': 4, 'Name': 'Shop', 'Description': 'Buy Groceries'},
             #{'id': 5, 'Name': 'Meditate', 'Description': 'Time to meditate'},
             #]
             #this was before pydantic. below is when we wrote Todo class using pydantic

all_todos = [
  Todo(id=1, todo_name='Sports', todo_description='Play basketball', priority=Priority.MEDIUM),
  Todo(id=2, todo_name='Read', todo_description='Read now', priority=Priority.LOW),
  Todo(id=3, todo_name='Study', todo_description='Go study', priority=Priority.HIGH),
  Todo(id=4, todo_name='Shop', todo_description='Buy Groceries', priority=Priority.MEDIUM),
  Todo(id=5, todo_name='Meditate', todo_description='Time to meditate', priority=Priority.LOW)
]

# to define end points we use http  methods like get, post, put, delete etc

@app.get('/')
def index():
  return {"message": "Hello world"}
# @app.get('/getdata')
# if the req is async then we can use async def instead of def, if synchronous then just def
# async def get_data():
#   return {"message": "This is the data"}

@app.get('/todos/{id}', response_model=Todo)
async def get_todo(id: int):
  for todo in all_todos:
    if todo.id == id:
      return todo
    
  raise HTTPException(status_code=404, detail='Todo not found')

@app.get('/todos') 
def get_todos(first_n: Optional[int] = None):
  if first_n:
    return all_todos[:first_n]
  return all_todos


#fastapi uses pydantic to validate the data

#to create new todo

@app.post('/todos', response_model=Todo) ##this will give list/collection of data
def create_todo(todo: TodoCreate): #why TodoCreate over Todo, because TodoCreate doesnt have id field which is generated automatically when we create a new todo, so we can use TodoCreate to define the structure of our request body when we create a new todo. and also it inherits all the fields from the base class which are required for creating a new todo.
  new_id = max(t.id for t in all_todos) + 1
  new_todo = Todo(id=new_id, todo_name=todo.todo_name, todo_description=todo.todo_description, priority=todo.priority)
  all_todos.append(new_todo)
  return new_todo


# the localhost is good for get requests but for post requests we need to use a tool like postman or curl to test the api. but an even convinient way is to use the interactive docs provided by fastapi. we can access it at http://localhost:8000/docs or http://localhost:8000/redoc. these docs are automatically generated based on the code we write and they allow us to test our api directly from the browser. we go to post and then we click on try it out and then we can enter the data in json format and then we can execute the request and see the response. this is a very convenient way to test our api without needing any external tools.

#now for update 
@app.put('/todos/{id}', response_model=Todo)
def update_todo(id: int, updated_todo: TodoUpdate):
  for todo in all_todos:
    if todo.id == id:
      updated = todo.model_copy(update={
        k: v for k, v in updated_todo.model_dump().items() if v is not None
      })
      all_todos[all_todos.index(todo)] = updated
      return updated
  
  raise HTTPException(status_code=404, detail='Todo not found')

#DELETE
@app.delete('/todos/{id}', response_model=Todo)
def delete_todo(id: int):
  for index, todo in enumerate(all_todos):
    if todo.id == id:
      deleted_todo = all_todos.pop(index)
      return deleted_todo
  
  raise HTTPException(status_code=404, detail='Todo not found')




  