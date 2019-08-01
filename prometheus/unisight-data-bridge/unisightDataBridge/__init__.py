def create_app(graphql_host, graphql_port, graphql_user, graphql_pass):

    from werkzeug.wsgi import DispatcherMiddleware
    from prometheus_client import make_wsgi_app
    import base64
    from simplejson.routes import create_app

    graphql_auth = 'Basic ' + base64.b64encode(graphql_user + ':' + graphql_pass.encode())

    app = create_app(graphql_host,
       graphql_port, graphql_auth)

    # Load the app
    application = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })

    # Load the node exporter app
    import nodeexporter.metrics
    import threading
    t = threading.Thread(target=nodeexporter.metrics.main, args=(graphql_host,
        graphql_port, graphql_auth ))
    t.daemon = True 
    t.start()
    return application
