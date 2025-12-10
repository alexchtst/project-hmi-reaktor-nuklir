from setuptools import setup, find_packages

setup(
    name='DigsilentPowerFactoryLibrary',
    version='0.0.1',
    description='Python Power Factory Connector Library',
    long_description=(
        'Library untuk menghubungkan Python dengan DIgSILENT PowerFactory, '
        'mendeteksi project, study case, menjalankan loadflow, serta '
        'melakukan simulasi dinamis.'
    ),
    long_description_content_type='text/plain',
    url='https://github.com/alexchtst/project-hmi-reaktor-nuklir',
    author='sukan',
    author_email='acinatra@gmail.com',
    license='MIT',  # atau sesuaikan lisensi Anda

    packages=find_packages(),
    python_requires='>=3.9',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
    ],

    keywords='PowerFactory digsilent loadflow dynamic-simulation',

    install_requires=[
        # Tambahkan dependency jika ada, contoh:
        # 'pandas',
        # 'numpy',
    ],

    project_urls={
        'Source': 'https://github.com/alexchtst/project-hmi-reaktor-nuklir',
        'Issues': 'https://github.com/alexchtst/project-hmi-reaktor-nuklir/issues',
    },
)
