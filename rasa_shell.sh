export RASA_X_HOST="http://localhost:5002"
export RASA_ACTION_ENDPOINT=${RASA_ACTION_ENDPOINT:="http://localhost:5055/webhook"}

echo "RASA_ACTION_ENDPOINT is " $RASA_ACTION_ENDPOINT
echo "RASA_X_HOST is " $RASA_X_HOST

rasa shell -vv \
    --model models \
    --verbose \
    --endpoints endpoints_local_model.yml \
    --debug \
    "$@"


