#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import sys
import jinja2
import webapp2
import models
import logging
import json 
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape = True)

def getPage(handler, page):
    user = users.get_current_user()
    if user:
        handler.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template(page)
        handler.response.write(template.render())
    else:
        handler.redirect(users.create_login_url(self.request.uri))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-Type'] = 'text/html'
            template = JINJA_ENVIRONMENT.get_template('views/index.html')
            existsTasks = models.User.query(models.User.user_id == user.user_id())
            if existsTasks != None: 
                tasks = models.Task().query(models.Task.author == user)#list of tasks the author has
                tasks_with_id = []#save tasks as list [task, id]
                tags_set = set()
                tags_with_id = []
                for task in tasks:
                    tasks_with_id.append((task, task.key.id()))
                    tags_set.add(task.tag)
                for tag in tags_set:
                    tagObject = models.Tag.query(models.Tag.tag == tag)
                    #logging.info(tagObject)
                    for obj in tagObject:
                        #logging.info("Hello")
                        tags_with_id.append((tag, obj.key.id()))
                logging.info(tags_with_id)
                self.response.write(template.render(user = user, tags = tags_with_id, tasks = tasks_with_id))
            else:
                self.response.write("Add a task!")

        else:
            self.redirect(users.create_login_url(self.request.uri))


class Oops(Exception):
    def __init__(self, foo):
        self.foo = foo

class Update(webapp2.RequestHandler):
    def post(self):
        #user = users.get_current_user()
        data = json.loads(self.request.body)
        logging.info(data["tid"])
        logging.info(data)
        tid = data["tid"]
        entry = models.Task.get_by_id(int(tid))
        logging.info(entry)
        entry.task = data['task']
        entry.put()

class NewTaskHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        data = json.loads(self.request.body)
        tag = models.Tag.get_by_id(int(data["tid"]))
        logging.info(tag)
        tag = tag.tag
        entry = models.Task()
        entry.author = user
        entry.task = data['task']
        entry.tag = tag
        entry.put()

class AddTaskHandler(webapp2.RequestHandler):
    def get(self):
        getPage(self, 'views/test.html')

    def post(self):
        entry = models.Task()
        entry.author = users.get_current_user()
        entry.task = self.request.get('taskname')
        #entry.duedate = self.request.get('duedate')

        tag = self.request.get('tag')
        if tag:
            entry.tag = tag
        else:
            entry.tag = None
        entry.put()

        existsTag = models.Tag.query(models.Tag.tag == tag).get()
        logging.info("OII")
        logging.info(existsTag)

        if existsTag is None: #check if tag in database
            newTag = models.Tag() #add the new tag
            newTag.tag = tag
            newTag.put()

        user = entry.author

        existsUser = models.User.query(models.User.user_id == user.user_id())
        existsUser = existsUser.get()

        if existsUser is None:
            newUser = models.User()
            newUser.user_id = user.user_id()
            newUser.tags = [entry.tag]
            newUser.put()
        else:
            logging.info("outputted %s", str(existsUser))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/add', AddTaskHandler),
    ('/new', NewTaskHandler),
    ('/update', Update)], 
    debug=True)
