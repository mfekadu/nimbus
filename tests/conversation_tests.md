#### This file contains tests to evaluate that your bot behaves as expected.
#### If you want to learn more, please see the docs: https://rasa.com/docs/rasa/user-guide/testing-your-assistant/

## happy path 1
* greet: hello there!
  - utter_greet
* react_positive: amazing
  - utter_happy

## happy path 2
* greet: hello there!
  - utter_greet
* react_positive: amazing
  - utter_happy
* goodbye: bye-bye!
  - utter_goodbye

## sad path 1
* greet: hello
  - utter_greet
* react_negative: not good
  - utter_cheer_up
  - utter_did_that_help
* affirm: yes
  - utter_happy

## sad path 2
* greet: hello
  - utter_greet
* react_negative: not good
  - utter_cheer_up
  - utter_did_that_help
* deny: not really
  - utter_cheer_up
  - utter_did_that_help
* deny: no not at all
  - utter_oos_other
  - utter_goodbye

## sad path 3
* greet: hi
  - utter_greet
* react_negative: very terrible
  - utter_cheer_up
  - utter_did_that_help
* deny: no
  - utter_cheer_up
  - utter_did_that_help
* deny: no not at all
  - utter_oos_other
  - utter_goodbye

## say goodbye
* goodbye: bye-bye!
  - utter_goodbye

## bot challenge
* chitchat/ask_isbot: are you a bot?
  - utter_chitchat_ask_isbot
  - action_hello_world
