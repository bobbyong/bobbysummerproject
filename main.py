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
import re
import hashlib

import webapp2
import jinja2
import logging

from google.appengine.ext import db

##### Website Page Handlers #####

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class PageHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))





##### User Database Stuff #####

class User(db.Model):
    email = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    joined = db.DateTimeProperty(auto_now_add = True)

class Signup(db.Model):
    email = db.StringProperty()     #temporary removed required = True
    joined = db.DateTimeProperty(auto_now_add = True)    

class Submit(db.Model):
    name = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    joined = db.DateTimeProperty(auto_now_add = True)    



##### Playlist and Quiz List #####

addmaths_f4= { 'ch2': [(1, 'Quadratic Equations', 'Jg0nvDjdqsI',''),
                        (2, '2.1 Quadratic Equations and its Roots', 'bp6_gAesCTk',''), 
                        (3, '2.2 Quadratic Equations - Part 1', '2pW7MF6kL74',''), 
                        (4, '2.2 Quadratic Equations - Part 2', 'Pl6eaqIcqdg',''),
                        (5, '2.2 Quadratic Equations - Part 3', 'ooD8CvFPhig',''),
                        (6, '2.2 Quadratic Equations - Part 4', 'SKDw3EtBabs',''),
                        (7, '2.3 Types of Roots of Quadratic Equations - Part 1', 'Sd15kSxzM0w',''),
                        (8, '2.3 Types of Roots of Quadratic Equations - Part 2', 'KANVMqizc4Y','')],
                'public': [(1, 'Quadratic Function - Quadratic Inequality', 'TFxnznhE51Y','&start=6&end=399'),
                        (2, 'Quadratic Function - Linear Inequality', 'u85dFT_5H-c','&start=6&end=266'),
                        (3, 'Function - Type of Relation and Function Notation', '2WaCcWftvr8','&start=6&end=115'),
                        (4, 'Function - Finding Domain, Codomain and Range from Arrow Diagram', 'KhoRxK9XEKs','&start=6&end=104'),
                        (5, 'Function - Finding Object and Image for Ordered Pair', 'usNfqLgy7mM','&start=6&end=100'),
                        (6, 'Logarithm', 'n8eIOs4ARGE',''),
                        (7, 'Understanding Rates of Change', 'GKugLlsSsp8',''),
                        (8, 'Understanding Rates of Change Part 2', 'gZC2JHM-WxE','')],  
                'ch1': [] }
     

### PLAYLIST FORMAT --> DICTIONARY {chapter: [playlist]}
### [playlist] format --> [id, title, youtube link, time_delay]    

quiz = [('Which of the following are hydrocarbons?', 'Alkanes and Alkenes','Alkanes and Carboxylic Acids', \
         'Alkenes and Alcohols','Alcohols and Carboxylic Acids', 'Alkenes and Carboxylic Acids', 'Alkanes and Alcohols', \
         'Alkanes and Alkenes are hydrocarbons because they consist of H and C atoms only. Hydrocarbons are compounds that \
         consist of H (Hydrogen) and C (Carbon) atoms only. Alcohols have the functional group -OH. It has an O (Oxygen) \
         therefore it is not a hydrocarbon. Carboxylic acids have the functional group -COOH. Esters have the functional \
         group -COO<sup>-</sup>', 1), 
        
        ('Which of the following are alkanes?', 'CH<sub>4</sub> and C<sub>4</sub>H<sub>8</sub>', \
         'C<sub>3</sub>H<sub>2</sub> and CH<sub>3</sub>COOH', 'C<sub>3</sub>H<sub>8</sub> and C<sub>3</sub>H<sub>2</sub>', \
         'C<sub>2</sub>H<sub>4</sub> and C<sub>2</sub>H<sub>5</sub>OH', 'C<sub>3</sub>H<sub>9</sub> and C<sub>4</sub>H<sub>10</sub>',\
         'C<sub>2</sub>H<sub>6</sub> and C<sub>4</sub>H<sub>10</sub>', 'Remember that the general formula of alkanes is \
         C<sub>n</sub>H<sub>2n+2</sub> <br>C<sub>2</sub>H<sub>6</sub>: Number of Carbon atoms = 2: \
         n=2 C<sub>(2)</sub>H<sub>2(2)+2</sub> = C<sub>2</sub>H<sub>6</sub><br> C<sub>4</sub>H<sub>10</sub>: \
         Number of Carbon atoms = 4: n=4 C<sub>(4)</sub>H<sub>2(4)+2</sub> = C<sub>4</sub>H<sub>10</sub>' ,6),

        ('How many Carbon atoms does Propane have?','1','2','3','4','5','6','<br>Propane <img src="http://upload.wikimedia.org/wikipedia/commons/a/a2/Propane-2D-flat.png" \
            height = 150px><br><br>Remember: <br>Meth- has 1 Carbon atom, <br>Eth- has 2 Carbon atoms, <br>Prop- has 3 Carbon atoms, <br>But- has 4 Carbon atoms \
            <br><br><i><h3>Kalau susah nak hafal ni...Hafal \"Mak Engkau Perut Buncit\" - Methane, Ethane, Propane, Butane: 1,2,3,4 Carbon atoms.</h3></i>',3),

        ('What is the name of this alkane? <br><img src="http://upload.wikimedia.org/wikipedia/commons/b/b9/Butane-2D-flat.png" height="150px">',\
            'Methane','Ethane','Propane','Butane', 'Pentane','Hexane','This is a Butane. The alkane shown has 4 Carbon atoms with single C-C bonds as the only functional group. \
             With 4 Carbon atoms on the parent chain and no side chains, the naming convention states that this alkane is named Butane.',4),

        ('What is the name of this alkane?<br><br><img src="http://www.ivy-rose.co.uk/Chemistry/Organic/molecules/alkanes/methylbutane.gif" height="150px">','2-methylpropane','3-methylbutane',\
            '2-methylbutane','2-ethylpropane','1,1-dimethylpropane','Pentane','The alkane shown has 4 Carbon atoms on its parent chain so it is a butane.  It has one side chain with 1 Carbon atom \
            - a methyl. This side chain is attached to 2nd Carbon atom of the parent chain - not the 3rd because IUPAC naming convention states that the smaller number is chosen when naming compounds',3),

        ('Which is this is not true for alkanes when the number of Carbon atoms increases?','Boiling point decreases','Insoluble in water', \
          'Soluble in organic solvents','More energy is required to overcome Van der Waals forces', 'Strength of Van der Waals forces increases', 'Boiling point increases', \
          'Alkanes are insoluble in water and soluble in organic compounds. As the number of Carbon atoms increases for an alkane, the strength of Van der Waals forces increases, \
          thus more energy is required to break these bonds and as such boiling point will increase.', 1),

        ('Which of the following reactions can an alkane undergo?','Combustion and Oxidation','Addition and Dehydration','Esterification and Substition','Dehydration and Combustion',\
            'Substitution and Addition','Combustion and Substitution', 'Alkanes undergo only combustion and substitution reactions.<br>Chemical Properties of Alkanes:<br><br><h3><ul><li>Undergo substitution reaction with halogens in sunlight <br> \
        eg CH<sub>4</sub> + Cl<sub>2</sub> -> CH<sub>3</sub>Cl + HCl<br><br><li>Burn in excess oxygen <br> eg C<sub>2</sub>H<sub>6</sub> + 3O<sub>2</sub> -> 2CO<sub>2</sub> + 3H<sub>2</sub>0</li></ul></h3> ',6)]


##### Main Page #####

class MainHandler(PageHandler):
    def get(self):
        self.render('main.html')

    def post(self):
        have_error = False
        email = self.request.get('email')
        
        params = dict(email = email)

        que = db.Query(Signup).filter("email =", email).fetch(limit=1)

        if que:
            params['error_email_register'] = "That email address is already registered."
            have_error = True
        
        if not valid_email(email):
            params['error_email'] = "That is not a valid email address."
            have_error = True

        if have_error:
            self.render('home.html', **params)

        else:      
            u = Signup(email=email)
            u.put()     
            
            self.render('home.html', message="Thank you for signing up with TuitionX. You may now begin your learning journey.<br><br>") 
        


##### Video Playlist Page #####

class PlaylistHandler(PageHandler):
    def get(self):
        
        subject = self.request.get("subject")
        year = self.request.get("year")
        chapter = self.request.get("chapter")
        lesson = self.request.get("lesson")
        lesson_id = int(lesson)-1
        
        list_to_use = addmaths_f4[chapter]

        while int(lesson_id+1)<len(list_to_use):
            self.render('playlist.html', playlist = list_to_use, lesson=lesson_id, \
                url = '/playlist?subject=%s&year=%s&chapter=%s&lesson=%s' %(subject,year,chapter,str(lesson_id + 2)), \
                button = "Next Video", time_delay=str(list_to_use[lesson_id][-1]), temp = addmaths_f4["public"])
            return

        self.render('playlist.html', playlist = list_to_use, lesson=lesson_id, url = '/quiz/1', \
            button = 'Continue Learning', time_delay=str(list_to_use[lesson_id][-1]), temp = addmaths_f4["public"])

        
                

##### Quizzes Page #####

class QuizHandler(PageHandler):
    def get(self, id):
        tuple_id = int(id)-1
        self.render('quiz.html', quiz = quiz, id=tuple_id, playlist=addmaths_f4)       


    def post(self, id):
        
        answer = self.request.get("quiz%s" %id)                     #get answer from form in 1,2,3,4 type

        if answer == '':                                            #form validation if no answer is selected
            self.write("Please click the Back button and select an answer.")
            return

        id = int(id)                                                #makes the id given in url an integer
        tuple_id = int(id) - 1                                      #refer to the id on the quiz tuple
        right_answer = "You got it right."
        wrong_answer = "You got it wrong."
        correct_answer = quiz[tuple_id][1 + quiz[tuple_id][-1]]     #print the correct answer in value type eg David Cameron
        given_answer = quiz[tuple_id][1 + int(answer)]              #print the answer given in value type eg Margaret Thatcher 
        explanation = quiz[tuple_id][-2]


        signup_button = """
                        <br><b><em>Congratulations on reaching this far in your learning. 
                        <br>We are working hard to build TuitionX. Kindly sign-up to our mailing list to keep updated.</em></b><br><br>
                        <a href = "/home" class="btn btn-primary btn-large">Sign Up Now &raquo;</a>
                        """  

        next_button = '<div class="playlist-button"><a href="/quiz/%s" class="btn btn-primary btn-large">Next Question &raquo;</a></div>' % str(id+1)                                    

        #signup_button and next_button SHOULD NOT be in this python/controller file --> it should be in the TEMPLATE/view/quiz.html file
        #signup_button and next_button is here for temporary convenience sake                  



        if int(answer) == quiz[tuple_id][-1]:                       #checks submitted answer with correct answer in tuple list
            if id+1 <= len(quiz):                                   #checks to see if this is the last question
                self.render("answer.html", quiz = quiz, correct_answer = correct_answer, given_answer = given_answer, tuple_id = tuple_id, solution = right_answer, explanation = explanation, nextquestion = next_button, playlist = addmaths_f4)
            else:
                self.render("answer.html", quiz = quiz, correct_answer = correct_answer, given_answer = given_answer, tuple_id = tuple_id, solution = right_answer, explanation = explanation, nextquestion = signup_button, playlist = addmaths_f4)
        else:                                                       #if wrong answer
            if id+1 <= len(quiz):                                   #if wrong answer and last question                
                self.render("answer.html", quiz = quiz, correct_answer = correct_answer, given_answer = given_answer, tuple_id = tuple_id, solution = wrong_answer, explanation = explanation, nextquestion = next_button, playlist = addmaths_f4)
            else:
                self.render("answer.html", quiz = quiz, correct_answer = correct_answer, given_answer = given_answer, tuple_id = tuple_id, solution = wrong_answer, explanation = explanation, nextquestion = signup_button, playlist = addmaths_f4)





##### Learn Page #####

alkane = ['Hydrocarbons are compounds that consist of H (Hydrogen) and C (Carbon) atoms only. <br><br> Hydrocarbons = Hydrogen + Carbon <br> That is why hydrocarbon compounds do not have any other elements apart from Hydrogen and Carbon, geddit?',
         
         'Alkanes and Alkenes are hydrocarbons because they consist of H and C atoms only. <br><br> Ethane <img src="http://upload.wikimedia.org/wikipedia/commons/9/99/Ethane-flat.png" height=150px> &nbsp;&nbsp;&nbsp; Ethene <img src="http://images.suite101.com/1954206_com_ethylene2.png" height=150px> <br><br> Look, there\'s no Oxygen or any other weird atoms there!',
         0,
         
         'Alkanes have the general formula C<sub>n</sub>H<sub>2n+2</sub>. <br><br>It has a single C-C bond as a functional group <br><br>Alkanes are saturated hydrocarbons because only single C-C bonds are present.<br><br><h3><i>There ain\'t any easy way to put those into memory except by simply memorising them!</i></h3>',
         1,
        
        'Examples of Alkanes:<br><br>1 Carbon atom: Methane <br>CH<sub>4</sub> [n=1 C<sub>(1)</sub>H</sub>2(1)+2</sub> = CH<sub>4</sub>] <br><img src = "http://upload.wikimedia.org/wikipedia/commons/b/b2/Methane-2D-flat-small.png" height = 150px> &nbsp;&nbsp; \
           <br><br>2 Carbon atoms: Ethane <br>C<sub>2</sub>H<sub>6</sub> [n=2 C<sub>(2)</sub>H<sub>2(2)+2</sub> = C<sub>2</sub>H<sub>6</sub>], <br><img src = "http://upload.wikimedia.org/wikipedia/commons/3/35/Ethan_Lewis.svg" height = 150px> &nbsp;&nbsp; \
           <br><br>3 Carbon atoms: Propane <br>C<sub>3</sub>H<sub>8</sub> [n=3 C<sub>(3)</sub>H<sub>2(3)+2</sub> = C<sub>3</sub>H<sub>8</sub>], <br><img src = "http://upload.wikimedia.org/wikipedia/commons/a/a2/Propane-2D-flat.png" height = 150px> &nbsp;&nbsp; \
           <br><br>4 Carbon atoms: Butane <br>C<sub>4</sub>H<sub>10</sub> [n=4 C<sub>(4)</sub>H<sub>2(4)+2</sub> = C<sub>4</sub>H<sub>10</sub>], <br><img src = "http://upload.wikimedia.org/wikipedia/commons/b/b9/Butane-2D-flat.png" height = 150px>',
        
        'Notice the names of Alkanes all end with -ane as in <u>Meth</u>ane, <u>Eth</u>ane, <u>Prop</u>ane, <u>But</u>ane. \
           <br>The underlined first part of the respective alkane names signifies the number of Carbon atoms in the parent chain. \
           <br><br>Meth- = 1 Carbon atom, <br>Eth- = 2 Carbon atoms, <br>Prop- = 3 Carbon atoms, <br>But- = 4 Carbon atoms \
           <br><br><i><h3>Kalau susah nak hafal ni...Hafal \"Mak Engkau Perut Buncit\" - Methane, Ethane, Propane, Butane: 1,2,3,4 Carbon atoms.</h3></i>',
         2,
         3,
        
        '<h3>IUPAC nomenclature: <br><br><ul><li>The longest chain is used as the parent name \
            <li> Alkyl side chains (-C<sub>n</sub>H<sub>2n+1</sub>) are named according to the number of carbon atoms present (1 Carbon atom - Methyl, 2 Carbon atoms - Ethyl, 3 Carbon atoms - Propyl, 4 Carbon atoms - Butyl)</li> \
            <li> The position of side chains are numbered accordingly</li> \
            <li> Side chains of same type are given prefix di, tri, tetra (2,3,4) according to their numbers present</li> \
            <li> Side chains are arranged alphabetically disregarding prefixes (eg ethyl, methyl, propyl, butyl)</li> \
            <li> Smaller numbers are chosen when naming compounds</li></ul></h3>',
        
        'Example of an IUPAC nomenclature:<br><br><img src="http://images.wikia.com/gcse/images/6/60/2-methyl_propane.jpg" height="200px"><br> \
            2-methylpropane <br><br><h3>Explanation:<ul><li>This structural formula is a type of propane because the longest parent chain has 3 Carbon atoms</li> \
            <li>There is a side chain with 1 Carbon atom hence the name methyl</li> \
            <li>This side chain is bolted onto the second Carbon atom of the parent chain hence the number 2</li></ul></h3>', 

        4,      
        
        'Physical Properties of Alkanes:<br><br><h3><ul><li>As number of Carbon atoms increases...</li> \
            <li>Strength of Van der Waals (VdW) forces between molecules increase...</li> \
            <li>More energy is  required to overcome these VdW forces...</li> \
            <li>Boiling point increases...</li><br><li>Insoluble in water</li><li>Soluble in organic solvents</li></ul></h3>',

        5,    
        
        'Chemical Properties of Alkanes:<br><br><h3><ul><li>Undergo substitution reaction with halogens in sunlight <br> \
        eg CH<sub>4</sub> + Cl<sub>2</sub> -> CH<sub>3</sub>Cl + HCl<br><br><li>Burn in excess oxygen <br> eg C<sub>2</sub>H<sub>6</sub> + 3O<sub>2</sub> -> 2CO<sub>2</sub> + 3H<sub>2</sub>0</li></ul></h3>',
        6  
        ]

alkene = ['1','2']

chapter_dic = {1: ['Alkanes',alkane], 2: ['Alkenes',alkene]}


class LearnHandler(PageHandler):
    def get(self, chapter, id):
        learn_id = int(id)-1
        learn = chapter_dic[int(chapter)][1]
        title = chapter_dic[int(chapter)][0]

        if int(id) <= len(learn):
            if isinstance(learn[learn_id], int ): 
                self.render('newquiz.html', quiz=quiz, id=learn[learn_id], title=title) 
            else:    
                self.render('learn.html', learn=learn, id=learn_id, chapter=chapter, title=title)    
        else:
            self.render('endoflearn.html')  
           

    def post(self, chapter, id):
        learn_id = int(id)-1
        learn = chapter_dic[int(chapter)][1]
        title = chapter_dic[int(chapter)][0]
        
        quiz_id = learn[learn_id]
        answer = self.request.get("quiz%s" % str(quiz_id))
        correct_answer_id = quiz[quiz_id][-1]

        if answer == '':                                            #form validation if no answer is selected
            self.write("Please click the Back button and select an answer.")
            return

        
        if int(answer) == quiz[quiz_id][-1]:
            self.render('newanswer.html', solution = "right", quiz=quiz, id=quiz_id, next=learn_id+2, \
            given_answer = quiz[quiz_id][int(answer)], correct_answer = quiz[quiz_id][correct_answer_id], points = '+50', title=title)        
        else:
            self.render('newanswer.html', solution = "wrong", quiz=quiz, id=quiz_id, next=learn_id+2, \
            given_answer = quiz[quiz_id][int(answer)], correct_answer = quiz[quiz_id][correct_answer_id], points = '+0', title=title)




##### SignUp Page #####


PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

def hash_str(s):
    return hashlib.md5(s).hexdigest()


class SignUpHandler(PageHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        have_error = False
        email = self.request.get('email')
        verify = self.request.get('verify')
        password = self.request.get('password')
        
        params = dict(email = email)

        que = db.Query(User).filter("email =", email).fetch(limit=1)

        if que:
            params['error_email_register'] = "That email address is already registered."
            have_error = True
        
        if not valid_password(password):
            params['error_password'] = "That is not a valid password."
            have_error = True
        
        elif email != verify:
            params['error_verify'] = "Your email addresses do not match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That is not a valid email address."
            have_error = True

        if have_error:
            self.render('signup.html', **params)

        else:      
            u = User(email=email, password=hash_str(password))
            u.put()     
            
            self.render('welcome.html') 





##### Home Handler #####

class HomeHandler(PageHandler):
    def get(self):
        self.render('home.html')

    def post(self):
        have_error = False
        email = self.request.get('email')

        params = dict(email = email)

        que = db.Query(Signup).filter("email =", email).fetch(limit=1)

        if que:
            params['error_email_register'] = "That email address is already registered."
            have_error = True
        
        if not valid_email(email):
            params['error_email'] = "That is not a valid email address."
            have_error = True

        if have_error:
            self.render('home.html', **params)

        else:      
            u = Signup(email=email)
            u.put()     
            
            self.render('welcome.html') 
    



##### Submit Handler #####

class SubmitHandler(PageHandler):
    def get(self):
        self.render('submit.html')

    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        content = self.request.get('content')

        if name and email != '' and valid_email(email) and content:
            p = Submit(name = name, email = email, content = content)
            p.put()
            self.render('home.html', message="Thank you for submitting your useful links. <br><br>") 
        
        else:
            error = "Name, valid email and content, please!"
            self.render("submit.html", name=name, email=email, content=content, error=error)    
    




##### About Handler #####

class AboutHandler(PageHandler):
    def get(self):
        self.render('about.html')

    

##### URL Mapping #####

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/home', HomeHandler),
                               ('/about', AboutHandler),
                               ('/playlist', PlaylistHandler),
                               ('/quiz/([0-9]+)', QuizHandler),
                               ('/learn/([0-9]+)/([0-9]+)', LearnHandler),
                               ('/submit', SubmitHandler),
                               ('/signup', SignUpHandler)],
                              debug=True)

