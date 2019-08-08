from invoke import task
from generators import magenta_generator


@task
def test(c):
    magenta_generator.test()
