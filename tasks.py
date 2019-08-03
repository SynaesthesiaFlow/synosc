from invoke import task
import magenta_helper

@task
def test(c):
    magenta_helper.test()
    sleep(5)