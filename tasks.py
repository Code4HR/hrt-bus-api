from invoke import run, task

@task
def acceptance():
    run("behave")

@task
def test():
    run("python -m unittest discover -s test/")

@task
def lint():
    run("pylint web/app.py test/*.py")

@task
def debug():
    run("python web/app.py")

@task(default = True, pre = [test, lint])
def default():
    print "Build complete!"

