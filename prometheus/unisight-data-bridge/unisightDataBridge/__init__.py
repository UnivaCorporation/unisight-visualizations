# Copyright 2008-2019 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def create_app(graphql_host="", graphql_port=0, graphql_user="", graphql_pass=""):

    from werkzeug.wsgi import DispatcherMiddleware
    from prometheus_client import make_wsgi_app
    import base64
    from .simplejson.routes import create_app

    graphql_auth = 'Basic ' + base64.b64encode((graphql_user + ':' + graphql_pass).encode()).decode()

    app = create_app(graphql_host,
       graphql_port, graphql_auth)

    # Load the app
    application = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })

    # Load the node exporter app
    from .nodeexporter import metrics
    import threading
    t = threading.Thread(target=nodeexporter.metrics.main, args=(graphql_host,
        graphql_port, graphql_auth ))
    t.daemon = True 
    t.start()
    return application
