from crowdsorting import app


if __name__ == '__main__':
    # Set debug environment triggers here


    app.run(debug=True, ssl_context='adhoc')
