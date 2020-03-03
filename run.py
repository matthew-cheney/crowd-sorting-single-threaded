# from werkzeug.middleware.dispatcher import DispatcherMiddleware
# from werkzeug.wsgi import DispatcherMiddleware
# from werkzeug.serving import run_simple

from crowdsorting import app


if __name__ == '__main__':
    # Set debug environment triggers here

    # application = DispatcherMiddleware(
    #     None, {
    #         '/crowd-sorting': app
    #     }
    # )

    # run_simple('0.0.0.0', 5000, application, use_reloader=True, ssl_context='adhoc')
    app.run(debug=True, ssl_context='adhoc')
