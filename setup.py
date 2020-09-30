from setuptools import setup


setup(name='county_radius_scraper',
      version='0.0.1',
      description='Tools to make scraping easier for zipcode radius searches and zips within county searches.',
      url='',
      author='Andrew Klampert',
      author_email='aklampert4@gmail.com',
      license='Andrew Klampert',
      packages=['county_radius_scraper'],
      install_requires=[
            'bs4==0.0.1',
            'numpy==1.19.2',
            'pandas==1.1.2',
            'requests==2.24.0'
      ],
      zip_safe=False
      )
