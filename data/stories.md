## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_happy
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye
  
## identity
* identity
 - utter_identity

## bot challenge
* bot_challenge
  - utter_iamabot
  - action_hello_world

<!-- only die via `/die` command, else will die on "di" and "de" and "dies" -->
## stop program
* die
  - utter_goodbye
  - action_stop_program