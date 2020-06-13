## thanks
* thank
    - utter_noworries
    - utter_anything_else

## goodbye
* goodbye
    - utter_goodbye

## greet
* greet
    - utter_greet
    - action_hello_world

## immediate denial
* greet
    - utter_greet
* deny
    - utter_nohelp

## anything else? - yes
* affirm
    - utter_anything_else
    - utter_what_help

## anything else? - no
* deny
    - utter_thumbsup
    - utter_anything_else

## positive reaction
* react_positive
    - utter_react_positive

## negative reaction
* react_negative
    - utter_react_negative

## story_for_intent:greet
* greet
    - utter_greet

## story_for_intent:goodbye
* goodbye
    - utter_greet

## story_for_intent:affirm
* affirm
    - utter_greet

## story_for_intent:deny
* deny
    - utter_greet

## story_for_intent:thank
* thank
    - utter_greet

## story_for_intent:react_positive
* react_positive
    - utter_greet

## story_for_intent:react_negative
* react_negative
    - utter_greet

## story_for_intent:restart
* restart
    - utter_greet

## chitchat
* chitchat
    - respond_chitchat

## faq
* faq
    - respond_faq

## out_of_scope
* out_of_scope
    - respond_out_of_scope