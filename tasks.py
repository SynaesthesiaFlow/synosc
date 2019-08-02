from invoke import task
import core

@task
def test(c):
    core.test()
    sleep(5)