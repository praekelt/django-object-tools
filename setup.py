from setuptools import setup, find_packages
from setuptools.command.test import test

class TestRunner(test):
    def run(self, *args, **kwargs):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)
        from runtests import runtests
        runtests()
setup(
    name='django-object-tools',
    version='0.0.1',
    description='Django app enabling painless creation of additional admin object tools.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    url='http://github.com/praekelt/django-object-tools',
    packages = find_packages(),
    include_package_data=True,
    test_suite = "object_tools.tests",
    cmdclass={"test": TestRunner},
    tests_require = [
        'django-snippetscream',
        'django>=1.3',
    ],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
