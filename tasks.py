from invoke import task
from generators import music_generator


@task
def test(c):
    music_generator.test()
