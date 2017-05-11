AURA ![travis-status](https://travis-ci.org/giagiannis/aura.svg?branch=master)
====

About
-----
AURA is an Openstack application deployment tool with error-recovery enhancements.

Video Demonstration
-------------------

In the following links you can view a video demonstration of AURA for a Wordpress and a Hadoop deployment:

[![AURA - Wordpress Installation](https://img.youtube.com/vi/lBAST5GPHaI/0.jpg)](http://www.youtube.com/watch?v=lBAST5GPHaI "AURA - Wordpress Installation")

[![AURA - Hadoop Installation](https://img.youtube.com/vi/jP3hmU7kvfk/0.jpg)](http://www.youtube.com/watch?v=jP3hmU7kvfk "AURA - Hadoop Installation")

Installation
------------
Fork this repository and install the requirements with pip:

```bash
pip install -r requirements.txt
```

You can then install the python egg with:

```bash
python setup.py install
```

This command only installs the CLI Client, as the Web Server is designed to be launched from inside the project root.

Usage
-----

To use AURA, you must do the following things:

 - Use an image that supports ssh as root with a private key (the path of which is provided to the configuration file).
 - Make sure that AURA runs on the same network as the VMs (OpenVPN can make the trick if not there by default).

### CLI Client
You can use the CLI client (bin/aura) to run in standalone mode.

Example:

```
bin/aura example/wordpress conf/aura.yml
```

Please see the `example/wordpress` directory in order to create applications of your own.

### Web Server
If you want an interactive usage, launch the Web Server with:

```
bin/aura-server conf/aura.yml
```

By default, the server is launched at `http://0.0.0.0:8080`, but feel free to change the host and/or port through the configuration file.

**WARNING:** this utilizes the Flask Development Server, really **NOT** recommended for production.

License
-------
Apache License 2.0, please see the [LICENSE](LICENSE) file for more details.

Contact
-------
Giannis Giannakopoulos, ggian@cslab.ece.ntua.gr
