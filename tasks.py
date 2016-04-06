from invoke import run, task

@task
def clean():
    run("rm -rf **/*.pyc")

@task
def acceptance():
    run("behave")

@task
def test():
    run("coverage run tests.py")
    run("coverage report")

@task
def lint():
    run("pylint web/app.py test/*.py")

@task
def debug():
    run("python web/app.py")

@task(default = True, pre = [test, lint])
def default():
    print "Build complete!"

