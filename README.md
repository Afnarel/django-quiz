Django quiz app
===============

This is a configurable quiz app for Django, developed by
Tom Walker ([tomwalker](https://github.com/tomwalker)).

This project differs from the original one in several ways:

* Only logged in users can access a quiz, not anonymous users
* Everything that has to do with following the progress of a user over time
  has been removed
* The Python source code is PEP8 compliant
* This project can be installed as a pip module (setup.py and MANIFEST.in)

The choices above have been made to make the project as simple to use as
possible.

Architecture
------------

The architecture is very simple:

There are 5 models: Category, Quiz, Question, Answer and Sitting.

A Quiz is composed of several Questions. For each Question, several Answers are
possible that can be either correct or incorrect. Both Quizzes and Questions
can be associated with a Category.

The Sitting models is a sort of session that is used to track the users:

  * Is he just starting a new Quiz or is he coming back to finish a Quiz that
    he previous left without completing it entirely?
  * Is he at the begining of the Quiz, in the middle or has he just finished
    it?
  * What is the current score of the user for this Quiz (absolute or
    percentage)?
  * Which answers of the Quiz did he answer correctly? Incorrectly?

Current features
----------------
Features of each quiz:

* Question order randomisation
* Correct answers can be shown after each question or all at once at the end
* Users can return to an incomplete quiz to finish it
* Questions have a category
* Explanation for each question result can be given
