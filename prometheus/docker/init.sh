#!/bin/bash


REST_USER=${UNISIGHT_ADMIN_USER:-"rest"}
REST_PSWD=${UNISIGHT_ADMIN_PSWD:-"rest"}
 
GRAPHQL_HOST=${GRAPHQL_HOST:-"unisight-graphql"}
GRAPHQL_PORT=${GRAPHQL_PORT:-3000}

if [ $$ -eq 1 ];then

    script=auth.sh
cat << EOF > $script 
import base64
print("Basic " + base64.b64encode("$REST_USER:$REST_PSWD".encode()).decode())
EOF

    auth=`python $script`
    rm -f $script

    export GRAPHQL_URL="http://$GRAPHQL_HOST:$GRAPHQL_PORT/graphql"
    export GRAPHQL_AUTH="$auth"
    /opt/unisight-data-bridge/bin/gunicorn -b 0.0.0.0:8001 'unisightDataBridge:create_app()'

fi

# Run the command
exec "$@"
 
