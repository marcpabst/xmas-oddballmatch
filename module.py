from parsl.app.app import python_app

@python_app
def my_app():
	return "Hello World!"
