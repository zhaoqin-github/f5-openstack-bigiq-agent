import f5_lbaasv2_bigiq_agent
import setuptools

setuptools.setup(
    version=f5_lbaasv2_bigiq_agent.__version__,
    name="f5-openstack-lbaasv2-bigiq-agent",
    description = ("F5 Networks BIG-IQ Agent for OpenStack services"),
    license = 'Apache License, Version 2.0',
    author="F5 Networks",
    author_email="q.zhao@f5.com",
    packages=setuptools.find_packages(exclude=['test']),
    data_files=[('/etc/neutron/services/f5', ['etc/neutron/services/f5/f5-lbaasv2-bigiq-agent.conf']),
                ('/usr/lib/systemd/system', ['lib/systemd/system/f5-lbaasv2-bigiq-agent.service']),
                ('/etc/init.d', ['etc/init.d/f5-lbaasv2-bigiq-agent'])],
    classifiers=[
        'Environment :: OpenStack',
	'Intended Audience :: Information Technology',
	'Intended Audience :: System Administrators',
	'License :: OSI Approved :: Apache Software License',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'f5-lbaasv2-bigiq-agent = f5_lbaasv2_bigiq_agent.agent:main'
        ]
    },
    install_requires=[]
)
